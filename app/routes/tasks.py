"""
=== app/routes/tasks.py ===
Task CRUD routes.

Laravel equivalent: app/Http/Controllers/TaskController.php

Tasks belong to Projects, so we check that:
1. The user is authenticated
2. The project exists and belongs to the user
3. The task belongs to that project

This is similar to how you'd use nested resource authorization in Laravel:
  $this->authorize('view', [$task, $project]);
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.project import Project
from app.models.task import Task
from app.schemas.task import (
    task_schema, tasks_schema,
    task_create_schema, task_update_schema
)

tasks_bp = Blueprint('tasks', __name__)


def get_user_project(project_id, user_id):
    """
    Helper to verify a project belongs to the current user.

    Laravel equivalent: A Policy or helper like:
      $project = Project::where('id', $id)->where('user_id', auth()->id())->firstOrFail();
    """
    return Project.query.filter_by(id=project_id, user_id=user_id).first()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/tasks?project_id=1 — List tasks for a project
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tasks_bp.route('', methods=['GET'])
@jwt_required()
def index():
    """
    List tasks, optionally filtered by project, status, or priority.

    Laravel equivalent:
      public function index(Request $request) {
          return TaskResource::collection(
              auth()->user()->tasks()
                  ->when($request->project_id, fn($q, $id) => $q->where('project_id', $id))
                  ->when($request->status, fn($q, $s) => $q->where('status', $s))
                  ->paginate(20)
          );
      }
    """

    current_user_id = int(get_jwt_identity())

    # Start with a base query joining projects to verify ownership
    # This is like: Task::whereHas('project', fn($q) => $q->where('user_id', auth()->id()))
    query = Task.query.join(Project).filter(Project.user_id == current_user_id)

    # ── Optional Filters (from query string) ────────────────────
    project_id = request.args.get('project_id', type=int)
    if project_id:
        query = query.filter(Task.project_id == project_id)

    status = request.args.get('status')
    if status:
        query = query.filter(Task.status == status)

    priority = request.args.get('priority')
    if priority:
        query = query.filter(Task.priority == priority)

    # ── Pagination ──────────────────────────────────────────────
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'tasks': tasks_schema.dump(pagination.items),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/tasks — Create a new task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tasks_bp.route('', methods=['POST'])
@jwt_required()
def store():
    """
    Create a new task within a project.
    """

    json_data = request.get_json()

    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        data = task_create_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    # Verify the project belongs to the user
    current_user_id = int(get_jwt_identity())
    project = get_user_project(data['project_id'], current_user_id)

    if not project:
        return jsonify({'error': 'Project not found or access denied'}), 404

    # Create the task
    task = Task(
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'todo'),
        priority=data.get('priority', 'medium'),
        due_date=data.get('due_date'),
        project_id=data['project_id']
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        'message': 'Task created successfully',
        'task': task_schema.dump(task)
    }), 201


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/tasks/<id> — Get a single task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def show(task_id):
    """Get a single task by ID."""

    current_user_id = int(get_jwt_identity())
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    # Verify ownership through the project
    if not get_user_project(task.project_id, current_user_id):
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({
        'task': task_schema.dump(task)
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PUT /api/tasks/<id> — Update a task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update(task_id):
    """Update an existing task."""

    current_user_id = int(get_jwt_identity())
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if not get_user_project(task.project_id, current_user_id):
        return jsonify({'error': 'Access denied'}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        data = task_update_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    # If changing project_id, verify user owns the new project too
    if 'project_id' in data:
        new_project = get_user_project(data['project_id'], current_user_id)
        if not new_project:
            return jsonify({'error': 'Target project not found or access denied'}), 404
        task.project_id = data['project_id']

    # Update fields that were provided
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        task.due_date = data['due_date']

    db.session.commit()

    return jsonify({
        'message': 'Task updated successfully',
        'task': task_schema.dump(task)
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DELETE /api/tasks/<id> — Delete a task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def destroy(task_id):
    """Delete a task."""

    current_user_id = int(get_jwt_identity())
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if not get_user_project(task.project_id, current_user_id):
        return jsonify({'error': 'Access denied'}), 403

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        'message': 'Task deleted successfully'
    }), 200
