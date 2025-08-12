from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, date, timedelta


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'tracker.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'change_this_secret'

db = SQLAlchemy(app)


# Helper functions for weekday calculations
def next_weekday(d, weekday):
    """Get the next weekday (0=Monday, 6=Sunday) from date d"""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days=days_ahead)

def adjust_to_weekday(d):
    """Adjust date to next Monday if it falls on weekend"""
    if d.weekday() >= 5:  # Saturday (5) or Sunday (6)
        return next_weekday(d, 0)  # Next Monday
    return d

def add_weekdays(d, days):
    """Add business days (weekdays only) to a date"""
    result = d
    remaining_days = days
    
    while remaining_days > 0:
        result += timedelta(days=1)
        if result.weekday() < 5:  # Monday to Friday
            remaining_days -= 1
    
    return adjust_to_weekday(result)


# Models
# Project model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    stage = db.Column(db.String(20), default='Planning')   # ← NEW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship('Task', backref='project', cascade='all, delete-orphan', lazy=True)
    todos = db.relationship('Todo', backref='project', cascade='all, delete-orphan', lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    vendor = db.Column(db.String(120))          # ← NEW COLUMN
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    dependency_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    status = db.Column(db.String(20), default='Not Started')
    notes = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship for dependencies
    dependency = db.relationship('Task', remote_side=[id], backref='dependent_tasks')
    
    # Relationship for file attachments
    attachments = db.relationship('TaskAttachment', backref='task', cascade='all, delete-orphan')
    
    def get_duration_days(self):
        """Get the duration of the task in business days"""
        if not self.start_date or not self.end_date:
            return 0
        
        current = self.start_date
        business_days = 0
        
        # Count business days from start_date to end_date (inclusive)
        while current <= self.end_date:
            if current.weekday() < 5:  # Monday to Friday
                business_days += 1
            current += timedelta(days=1)
        
        return business_days
    
    def adjust_dates_for_dependency(self, dependency_end_date_change):
        """Adjust start and end dates when dependency changes"""
        if not self.dependency_id:
            return
        
        # Get the current dependency task
        dependency = Task.query.get(self.dependency_id)
        if not dependency or not dependency.end_date:
            return
        
        # Instead of moving by the same number of days, 
        # set start date to the next day after dependency ends
        if dependency.end_date:
            new_start = dependency.end_date + timedelta(days=1)
            self.start_date = adjust_to_weekday(new_start)
        
        # Adjust end date to maintain the same duration
        if self.start_date and self.end_date:
            duration = self.get_duration_days()
            new_end = self.start_date
            business_days_added = 0
            
            # Add business days to reach the required duration
            while business_days_added < duration:
                new_end += timedelta(days=1)
                if new_end.weekday() < 5:  # Monday to Friday
                    business_days_added += 1
                # If we hit a weekend, continue to the next day without counting it
            
            # Ensure the final date is not on a weekend
            self.end_date = adjust_to_weekday(new_end)
        
        # Recursively adjust dependent tasks - this will cascade through the entire chain
        for dependent_task in self.dependent_tasks:
            dependent_task.adjust_dates_for_dependency(0)


class Todo(db.Model):                                   # ← NEW TABLE
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TaskAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    variants = db.relationship('MaterialVariant', back_populates='material', cascade='all, delete-orphan')
    task = db.relationship('Task', back_populates='materials')
    project = db.relationship('Project', back_populates='materials')


class MaterialVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=True)  # URL is now optional
    note = db.Column(db.String(255))
    cost = db.Column(db.Float, nullable=True)  # Cost field for each variant
    picked = db.Column(db.Boolean, default=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    
    material = db.relationship('Material', back_populates='variants')


Task.materials = db.relationship('Material', back_populates='task', cascade='all, delete-orphan')
Project.materials = db.relationship('Material', back_populates='project', cascade='all, delete-orphan')


# Home - list projects
@app.route('/')
def index():
    stage_pct = {
        'Planning': 0, 'Pre-Construction': 25,
        'Construction': 50, 'Finish Work': 75,
        'Complete': 100,
    }
    enriched = []
    for p in Project.query.all():
        # Calculate estimated completion date (latest task end date)
        estimated_completion = None
        if p.tasks:
            # Get all tasks with end dates
            tasks_with_dates = [t for t in p.tasks if t.end_date]
            if tasks_with_dates:
                # Find the latest end date
                latest_end_date = max(t.end_date for t in tasks_with_dates)
                estimated_completion = latest_end_date
        
        pct = stage_pct.get(p.stage, 0)
        enriched.append(dict(project=p, estimated_completion=estimated_completion, pct=pct))
    return render_template('index.html', projects=enriched)


# Add new project
@app.route('/project/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description')
        if name.strip() == '':
            flash('Project name cannot be empty.', 'danger')
            return redirect(url_for('add_project'))
        new_proj = Project(name=name, description=description)
        db.session.add(new_proj)
        db.session.commit()
        flash('Project created.', 'success')
        return redirect(url_for('index'))
    return render_template('add_project.html')


# Project detail & tasks
@app.route('/project/<int:project_id>', methods=['GET', 'POST'])
def project_detail(project_id):
    proj = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        # add task
        task_name = request.form['task_name']
        category = request.form.get('category')
        vendor = request.form.get('vendor')
        dependency_id = request.form.get('dependency_id')
        
        # Parse start and end dates
        start_date = None
        end_date = None
        
        start_date_str = request.form.get('start_date')
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid start date format. Use YYYY-MM-DD.', 'danger')
                return redirect(url_for('project_detail', project_id=project_id))
        
        end_date_str = request.form.get('end_date')
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid end date format. Use YYYY-MM-DD.', 'danger')
                return redirect(url_for('project_detail', project_id=project_id))
        
        # Handle dependency logic
        if dependency_id and dependency_id != '':
            dependency = Task.query.get(dependency_id)
            if dependency and dependency.end_date:
                # Ensure start date is at least 1 business day after dependency end date
                min_start_date = add_weekdays(dependency.end_date, 1)
                if start_date and start_date < min_start_date:
                    start_date = min_start_date
                    flash(f'Start date adjusted to {start_date.strftime("%Y-%m-%d")} based on dependency.', 'info')
        
        # Adjust dates to weekdays
        if start_date:
            start_date = adjust_to_weekday(start_date)
        if end_date:
            end_date = adjust_to_weekday(end_date)
        
        status = request.form.get('status', 'Not Started')
        
        new_task = Task(
            name=task_name, 
            category=category, 
            vendor=vendor, 
            start_date=start_date, 
            end_date=end_date, 
            dependency_id=dependency_id if dependency_id else None,
            status=status, 
            project=proj
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task added.', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    # Convert tasks to serializable format for JavaScript
    tasks_json = []
    for task in proj.tasks:
        tasks_json.append({
            'id': task.id,
            'name': task.name,
            'start_date': task.start_date.strftime('%Y-%m-%d') if task.start_date else None,
            'end_date': task.end_date.strftime('%Y-%m-%d') if task.end_date else None,
            'dependency_id': task.dependency_id
        })
    
    # Get today's date for overdue checking
    today = date.today()
    
    # Create a list of overdue task IDs for easier template processing
    overdue_tasks = []
    for task in proj.tasks:
        if task.end_date and task.end_date < today:
            overdue_tasks.append(task.id)
    
    return render_template('project_detail.html', project=proj, tasks_json=tasks_json, today=today, overdue_tasks=overdue_tasks)


# Edit the project name and description
@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    proj = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        new_name = request.form['name'].strip()
        new_desc = request.form.get('description', '').strip()

        if new_name == '':
            flash('Project name cannot be empty.', 'danger')
            return redirect(url_for('edit_project', project_id=project_id))

        proj.name = new_name
        proj.description = new_desc
        db.session.commit()
        flash('Project details updated.', 'success')
        return redirect(url_for('project_detail', project_id=project_id))

    return render_template('edit_project.html', project=proj)


# Update task status
@app.route('/task/<int:task_id>/status', methods=['POST'])
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get('status', task.status)
    task.status = new_status
    db.session.commit()
    flash('Task status updated.', 'success')
    return redirect(url_for('project_detail', project_id=task.project_id))


# Delete task
@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'info')
    return redirect(url_for('project_detail', project_id=project_id))


# Delete project
@app.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    proj = Project.query.get_or_404(project_id)
    db.session.delete(proj)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('index'))


# ------------------------------------------------------------------
#   Quick To-Do API (AJAX)
# ------------------------------------------------------------------
@app.route('/project/<int:project_id>/todo', methods=['POST'])
def add_todo(project_id):
    data = request.get_json(force=True)
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'text required'}), 400
    todo = Todo(text=text, project_id=project_id)
    db.session.add(todo)
    db.session.commit()
    return jsonify({'id': todo.id, 'text': todo.text, 'completed': todo.completed}), 201


@app.route('/todo/<int:todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    return jsonify({'id': todo.id, 'completed': todo.completed})


@app.route('/task/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json(force=True)
    
    # Store old end date for dependency calculations
    old_end_date = task.end_date
    
    if 'notes' in data:
        task.notes = data['notes']
    if 'name' in data:
        task.name = data['name']
    if 'category' in data:
        task.category = data['category']
    if 'vendor' in data:
        task.vendor = data['vendor']
    if 'start_date' in data:
        if data['start_date']:
            try:
                new_start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                new_start_date = adjust_to_weekday(new_start_date)
                
                # Check dependency constraints for start date
                if task.dependency_id:
                    dependency = Task.query.get(task.dependency_id)
                    if dependency and dependency.end_date:
                        min_start_date = add_weekdays(dependency.end_date, 1)
                        if new_start_date < min_start_date:
                            return jsonify({'error': f'Start date cannot be earlier than {min_start_date.strftime("%Y-%m-%d")} based on dependency'}), 400
                
                task.start_date = new_start_date
            except ValueError:
                return jsonify({'error': 'Invalid start date format'}), 400
        else:
            task.start_date = None
    if 'end_date' in data:
        if data['end_date']:
            try:
                new_end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                new_end_date = adjust_to_weekday(new_end_date)
                
                # Check that end date is not before start date
                if task.start_date and new_end_date < task.start_date:
                    return jsonify({'error': 'End date cannot be before start date'}), 400
                
                task.end_date = new_end_date
            except ValueError:
                return jsonify({'error': 'Invalid end date format'}), 400
        else:
            task.end_date = None
    if 'dependency_id' in data:
        new_dependency_id = data['dependency_id'] if data['dependency_id'] else None
        
        # If changing dependency, validate the new dependency
        if new_dependency_id != task.dependency_id:
            if new_dependency_id:
                dependency = Task.query.get(new_dependency_id)
                if dependency and dependency.end_date and task.start_date:
                    min_start_date = add_weekdays(dependency.end_date, 1)
                    if task.start_date < min_start_date:
                        return jsonify({'error': f'Start date must be at least {min_start_date.strftime("%Y-%m-%d")} based on new dependency'}), 400
        
        task.dependency_id = new_dependency_id
    if 'status' in data:
        task.status = data['status']
    
    # Handle dependency adjustments when end date changes
    dependent_tasks_updated = []
    if old_end_date != task.end_date and task.dependent_tasks:
        # Helper function to collect all tasks in the dependency chain
        def collect_updated_tasks(task_list, collected_tasks):
            for t in task_list:
                # Add this task to collected tasks
                collected_tasks.append({
                    'id': t.id,
                    'start_date': t.start_date.strftime('%Y-%m-%d') if t.start_date else None,
                    'end_date': t.end_date.strftime('%Y-%m-%d') if t.end_date else None
                })
                # Recursively collect dependent tasks
                if t.dependent_tasks:
                    collect_updated_tasks(t.dependent_tasks, collected_tasks)
        
        # Trigger dependency adjustments for all dependent tasks
        for dependent_task in task.dependent_tasks:
            dependent_task.adjust_dates_for_dependency(0)
        
        # Collect information about ALL tasks in the dependency chain
        collect_updated_tasks(task.dependent_tasks, dependent_tasks_updated)
    
    db.session.commit()
    
    return jsonify({
        'id': task.id, 'name': task.name, 'category': task.category,
        'vendor': task.vendor, 'start_date': task.start_date.strftime('%Y-%m-%d') if task.start_date else None,
        'end_date': task.end_date.strftime('%Y-%m-%d') if task.end_date else None,
        'dependency_id': task.dependency_id, 'status': task.status, 'notes': task.notes,
        'dependent_tasks_updated': dependent_tasks_updated
    })


@app.route('/todo/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'success': True})


# File attachment routes
@app.route('/task/<int:task_id>/upload', methods=['POST'])
def upload_file(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(BASE_DIR, 'uploads', str(task_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            import uuid
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Create attachment record
            attachment = TaskAttachment(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                mime_type=file.content_type or 'application/octet-stream',
                task_id=task_id
            )
            
            db.session.add(attachment)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'attachment': {
                    'id': attachment.id,
                    'filename': attachment.original_filename,
                    'file_size': attachment.file_size,
                    'uploaded_at': attachment.uploaded_at.strftime('%Y-%m-%d %H:%M')
                }
            })
        
        return jsonify({'error': 'File upload failed'}), 500
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/task/<int:task_id>/attachments')
def get_attachments(task_id):
    task = Task.query.get_or_404(task_id)
    attachments = []
    
    for attachment in task.attachments:
        attachments.append({
            'id': attachment.id,
            'filename': attachment.original_filename,
            'file_size': attachment.file_size,
            'uploaded_at': attachment.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            'mime_type': attachment.mime_type
        })
    
    return jsonify({'attachments': attachments})


@app.route('/attachment/<int:attachment_id>/download')
def download_attachment(attachment_id):
    attachment = TaskAttachment.query.get_or_404(attachment_id)
    
    if not os.path.exists(attachment.file_path):
        return jsonify({'error': 'File not found'}), 404
    
    from flask import send_file
    return send_file(
        attachment.file_path,
        as_attachment=True,
        download_name=attachment.original_filename
    )


@app.route('/attachment/<int:attachment_id>', methods=['DELETE'])
def delete_attachment(attachment_id):
    attachment = TaskAttachment.query.get_or_404(attachment_id)
    
    # Delete physical file
    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)
    
    # Delete database record
    db.session.delete(attachment)
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/project/<int:project_id>/stage', methods=['PATCH'])
def update_stage(project_id):
    proj = Project.query.get_or_404(project_id)
    data = request.get_json(force=True)
    proj.stage = data.get('stage', proj.stage)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/materials/<int:project_id>/<task_id>')
def get_materials(project_id, task_id):
    if task_id == "general":
        materials = Material.query.filter_by(project_id=project_id, task_id=None).all()
    else:
        materials = Material.query.filter_by(project_id=project_id, task_id=task_id).all()
    
    # Check if each material has a picked variant
    materials_data = []
    for m in materials:
        has_picked = any(v.picked for v in m.variants)
        materials_data.append({
            "id": m.id, 
            "name": m.name,
            "has_picked": has_picked
        })
    
    return jsonify(materials=materials_data)


@app.route('/materials/add', methods=['POST'])
def add_material():
    data = request.get_json()
    name = data.get("name")
    task_id = data.get("task_id")
    project_id = data.get("project_id")

    material = Material(name=name, project_id=project_id, task_id=task_id)
    db.session.add(material)
    db.session.commit()
    return jsonify(success=True)


@app.route("/materials/decision/<int:material_id>")
def material_decision(material_id):
    material = Material.query.get_or_404(material_id)
    return render_template("partials/decision_modal.html", material=material)


@app.route("/materials/ordered/<int:material_id>", methods=["POST"])
def mark_ordered(material_id):
    data = request.get_json()
    material = Material.query.get_or_404(material_id)
    material.ordered = data.get("ordered", False)
    db.session.commit()
    return jsonify(success=True)


@app.route("/materials/update/<int:material_id>", methods=["POST"])
def update_material(material_id):
    data = request.get_json()
    material = Material.query.get_or_404(material_id)
    material.name = data.get("name")
    db.session.commit()
    return jsonify(success=True)


@app.route("/materials/delete/<int:material_id>", methods=["POST"])
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    db.session.delete(material)
    db.session.commit()
    return jsonify(success=True)


@app.route("/materials/variant/add", methods=["POST"])
def add_variant():
    data = request.get_json()
    url = data.get("url", "").strip()
    note = data.get("note", "").strip()
    cost = data.get("cost")
    material_id = data.get("material_id")

    # Convert cost to float if provided, otherwise None
    if cost and cost.strip():
        try:
            cost = float(cost)
        except ValueError:
            cost = None
    else:
        cost = None

    # If URL is empty, use note as the display text and set URL to empty string
    if not url:
        url = ""  # Store as empty string since SQLite doesn't support changing NOT NULL constraint
        # If no note provided, use a default text
        if not note:
            note = "No description"

    variant = MaterialVariant(url=url, note=note, cost=cost, material_id=material_id)
    db.session.add(variant)
    db.session.commit()

    material = Material.query.get(material_id)
    return render_template("partials/_variant_list.html", variants=material.variants)


@app.route("/materials/variant/pick", methods=["POST"])
def pick_variant():
    data = request.get_json()
    picked_id = data.get("variant_id")

    picked = MaterialVariant.query.get_or_404(picked_id)

    # Unpick all other variants for this material
    MaterialVariant.query.filter_by(material_id=picked.material_id).update({"picked": False})

    # Mark the selected one as picked
    picked.picked = True

    db.session.commit()

    return jsonify(success=True)


@app.route("/materials/variant/unpick", methods=["POST"])
def unpick_variant():
    data = request.get_json()
    variant_id = data.get("variant_id")
    material_id = data.get("material_id")

    if variant_id:
        # Unpick specific variant
        variant = MaterialVariant.query.get_or_404(variant_id)
        variant.picked = False
    elif material_id:
        # Unpick all variants for this material
        MaterialVariant.query.filter_by(material_id=material_id).update({"picked": False})
    else:
        return jsonify(error="Missing variant_id or material_id"), 400

    db.session.commit()

    return jsonify(success=True)


@app.route("/materials/variant/delete/<int:variant_id>", methods=["POST"])
def delete_variant(variant_id):
    variant = MaterialVariant.query.get_or_404(variant_id)
    material_id = variant.material_id
    db.session.delete(variant)
    db.session.commit()

    material = Material.query.get(material_id)
    return render_template("partials/_variant_list.html", variants=material.variants)


# --- helper to build tables ----------------------------------------
def init_db():
    """Create tracker.db and all tables if they don't exist yet."""
    with app.app_context():
        db.create_all()
        
        # Add cost column to material_variant table if it doesn't exist
        try:
            with db.engine.connect() as conn:
                # Check if cost column exists
                result = conn.execute(db.text("PRAGMA table_info(material_variant)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'cost' not in columns:
                    conn.execute(db.text("ALTER TABLE material_variant ADD COLUMN cost FLOAT"))
                    conn.commit()
                    print("✓ Added cost column to material_variant table")
                else:
                    print("✓ Cost column already exists")
                    
                # Note: SQLite doesn't support ALTER COLUMN to change nullability
                # The url column will remain NOT NULL in the schema, but we can store NULL values
                # This is a limitation of SQLite - the model allows nullable=True but the DB constraint remains
        except Exception as e:
            print(f"⚠️  Error checking/adding cost column: {e}")
        
        # Check if we need to migrate from due_date to start_date/end_date
        try:
            with db.engine.connect() as conn:
                # Check if due_date column exists
                result = conn.execute(db.text("PRAGMA table_info(task)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'due_date' in columns and 'start_date' not in columns:
                    # Migrate from due_date to start_date/end_date
                    conn.execute(db.text("ALTER TABLE task ADD COLUMN start_date DATE"))
                    conn.execute(db.text("ALTER TABLE task ADD COLUMN end_date DATE"))
                    conn.execute(db.text("ALTER TABLE task ADD COLUMN dependency_id INTEGER REFERENCES task(id)"))
                    
                    # Copy due_date to end_date for existing tasks
                    conn.execute(db.text("UPDATE task SET end_date = due_date WHERE due_date IS NOT NULL"))
                    
                    # Set start_date to 1 week before end_date for existing tasks
                    conn.execute(db.text("UPDATE task SET start_date = date(end_date, '-7 days') WHERE end_date IS NOT NULL"))
                    
                    # Remove the old due_date column (SQLite limitation - we'll just ignore it)
                    print("✓ Migrated from due_date to start_date/end_date")
                    print("⚠️  Note: due_date column remains but is no longer used")
                else:
                    print("✓ Task table already has start_date/end_date structure")
                    
        except Exception as e:
            print(f"⚠️  Error checking/migrating task table: {e}")
        
        # Create uploads directory
        uploads_dir = os.path.join(BASE_DIR, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        print("✓ Uploads directory created")
        
        # Ensure TaskAttachment table exists
        try:
            with db.engine.connect() as conn:
                # Check if TaskAttachment table exists
                result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='task_attachment'"))
                if not result.fetchone():
                    print("⚠️  TaskAttachment table not found - creating it...")
                    # Create the TaskAttachment table specifically
                    conn.execute(db.text("""
                        CREATE TABLE task_attachment (
                            id INTEGER PRIMARY KEY,
                            filename VARCHAR(255) NOT NULL,
                            original_filename VARCHAR(255) NOT NULL,
                            file_path VARCHAR(500) NOT NULL,
                            file_size INTEGER NOT NULL,
                            mime_type VARCHAR(100),
                            task_id INTEGER NOT NULL,
                            uploaded_at DATETIME,
                            FOREIGN KEY (task_id) REFERENCES task (id)
                        )
                    """))
                    conn.commit()
                    print("✓ TaskAttachment table created manually")
                else:
                    print("✓ TaskAttachment table already exists")
        except Exception as e:
            print(f"⚠️  Error checking/creating TaskAttachment table: {e}")
        
        print("✓ Database initialized (tracker.db)")


# -------------------------------------------------------------------
if __name__ == '__main__':
    init_db()
    # Remove the app.run() line for PythonAnywhere
    app.run(debug=True, host='0.0.0.0', port=5000)
