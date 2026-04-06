"""
=== app/routes/projects.py ===
Project CRUD routes — the bread and butter of REST APIs.

Laravel equivalent: app/Http/Controllers/ProjectController.php
With routes like:
  Route::apiResource('projects', ProjectController::class);

This gives you the standard RESTful endpoints:
  GET    /api/projects         → index()   — List all projects
  POST   /api/projects         → store()   — Create a project
  GET    /api/projects/{id}    → show()    — Get one project
  PUT    /api/projects/{id}    → update()  — Update a project
  DELETE /api/projects/{id}    → destroy() — Delete a project

KEY CONCEPT — Query Patterns (SQLAlchemy vs Eloquent):
  Laravel:  Project::where('user_id', auth()->id())->get();
  Flask:    Project.query.filter_by(user_id=current_user_id).all()

  Laravel:  Project::findOrFail($id);
  Flask:    Project.query.get_or_404(id)  (or manual check)

  Laravel:  $project->update($request->validated());
  Flask:    project.name = data['name']; db.session.commit()
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.project import Project
from app.schemas.project import (
    project_schema, projects_schema,
    project_create_schema, project_update_schema
)

projects_bp = Blueprint('projects', __name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/projects — List all projects for the authenticated user
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@projects_bp.route('', methods=['GET'])
@jwt_required()
def index():
    """
    List all projects belonging to the current user.

    Laravel equivalent:
      public function index() {
          $projects = auth()->user()->projects()
              ->when($request->status, fn($q, $s) => $q->where('status', $s))
              ->paginate(20);
          return ProjectResource::collection($projects);
      }
    """

    current_user_id = int(get_jwt_identity())

    # ── Query with optional filtering ───────────────────────────
    # Start building a query (like Laravel's query builder)
    query = Project.query.filter_by(user_id=current_user_id)

    # Optional filter by status via query string
    # Laravel: $request->query('status')
    # Flask: request.args.get('status')
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    # ── Pagination ──────────────────────────────────────────────
    # Laravel: ->paginate(20)
    # Flask-SQLAlchemy: .paginate(page=1, per_page=20)
    page = request.args.get('page', 1, type=int)      # Default page 1
    per_page = request.args.get('per_page', 20, type=int)  # Default 20 items

    # paginate() returns a Pagination object with items, total, pages, etc.
    pagination = query.order_by(Project.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False  # Don't raise 404 on empty page
    )

    return jsonify({
        'projects': projects_schema.dump(pagination.items),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            # Laravel: $projects->hasMorePages()
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/projects — Create a new project
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@projects_bp.route('', methods=['POST'])
@jwt_required()
def store():
    """
    Create a new project.

    Laravel equivalent:
      public function store(StoreProjectRequest $request) {
          $project = auth()->user()->projects()->create($request->validated());
          return new ProjectResource($project);
      }
    """

    json_data = request.get_json()

    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    # Validate
    try:
        data = project_create_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    # Create project
    current_user_id = int(get_jwt_identity())
    project = Project(
        name=data['name'],
        description=data.get('description'),  # .get() returns None if key doesn't exist
        status=data.get('status', 'active'),
        user_id=current_user_id
    )

    db.session.add(project)
    db.session.commit()

    return jsonify({
        'message': 'Project created successfully',
        'project': project_schema.dump(project)
    }), 201


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/projects/<id> — Get a single project
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def show(project_id):
    """
    Get a single project by ID.

    Laravel equivalent:
      public function show(Project $project) {
          $this->authorize('view', $project);
          return new ProjectResource($project->load('tasks'));
      }

    Note the <int:project_id> in the route — this is like {project} in Laravel routes.
    Flask automatically extracts it and passes it as a function argument.
    The 'int:' part ensures it's an integer (type casting).
    """

    current_user_id = int(get_jwt_identity())

    # Find the project — Laravel: Project::findOrFail($id)
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # Authorization check — like Laravel's authorize() or Policy
    # Ensure the project belongs to the current user
    if project.user_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({
        'project': project_schema.dump(project)
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PUT /api/projects/<id> — Update a project
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update(project_id):
    """
    Update an existing project.

    Laravel equivalent:
      public function update(UpdateProjectRequest $request, Project $project) {
          $this->authorize('update', $project);
          $project->update($request->validated());
          return new ProjectResource($project);
      }
    """

    current_user_id = int(get_jwt_identity())
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    if project.user_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        data = project_update_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    # ── Update fields ───────────────────────────────────────────
    # In Laravel: $project->update($validated) does this automatically.
    # In Flask, you update each field manually:
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        project.status = data['status']

    # Commit the changes — like calling $project->save() in Laravel
    db.session.commit()

    return jsonify({
        'message': 'Project updated successfully',
        'project': project_schema.dump(project)
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DELETE /api/projects/<id> — Delete a project
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def destroy(project_id):
    """
    Delete a project and all its tasks.

    Laravel equivalent:
      public function destroy(Project $project) {
          $this->authorize('delete', $project);
          $project->delete();  // Cascade deletes tasks too
          return response()->json(['message' => 'Deleted'], 200);
      }
    """

    current_user_id = int(get_jwt_identity())
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    if project.user_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403

    # Delete — cascade='all, delete-orphan' in the model handles related tasks
    db.session.delete(project)
    db.session.commit()

    return jsonify({
        'message': 'Project deleted successfully'
    }), 200
