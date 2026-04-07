"""
=== app/routes/tags.py ===
Tag routes — CRUD for tags + attach/detach tags to tasks.

Laravel equivalent: app/Http/Controllers/TagController.php

Routes:
  GET    /api/tags                        → List all available tags
  POST   /api/tags                        → Create a new tag
  PUT    /api/tags/<id>                   → Update a tag
  DELETE /api/tags/<id>                   → Delete a tag

  POST   /api/tags/<id>/attach/<task_id>  → Attach tag to a task
  DELETE /api/tags/<id>/detach/<task_id>  → Detach tag from a task
  GET    /api/tags/task/<task_id>         → Get all tags for a task

KEY CONCEPT — Many-to-Many attach/detach:
  In Laravel:
    $task->tags()->attach($tagId);
    $task->tags()->detach($tagId);
    $task->tags()->sync([$tagId1, $tagId2]);  // Replace all at once

  In SQLAlchemy:
    task.tags.append(tag)   # attach
    task.tags.remove(tag)   # detach
    task.tags = [tag1, tag2] # sync (replace all)
    db.session.commit()      # always commit after changes!
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.tag import Tag
from app.models.task import Task
from app.models.project import Project
from app.schemas.tag import (
    tag_schema, tags_schema,
    tag_create_schema, tag_update_schema
)

tags_bp = Blueprint('tags', __name__)


def get_accessible_task(task_id, user_id):
    """Helper: get a task that belongs to the current user (via project)."""
    return Task.query.join(Project).filter(
        Task.id == task_id,
        Project.user_id == user_id
    ).first()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/tags — List all tags
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tags_bp.route('', methods=['GET'])
@jwt_required()
def index():
    """
    List all available tags.
    Tags are global (shared across all users, like GitHub labels).

    Laravel equivalent:
      public function index() {
          return TagResource::collection(Tag::orderBy('name')->get());
      }
    """

    tags = Tag.query.order_by(Tag.name.asc()).all()
    return jsonify({'tags': tags_schema.dump(tags)}), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/tags — Create a tag
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tags_bp.route('', methods=['POST'])
@jwt_required()
def store():
    """Create a new tag."""

    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        data = tag_create_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    # Check uniqueness — like Laravel's 'unique:tags' rule
    if Tag.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'A tag with this name already exists'}), 409

    tag = Tag(name=data['name'], color=data.get('color'))
    db.session.add(tag)
    db.session.commit()

    return jsonify({
        'message': 'Tag created successfully',
        'tag': tag_schema.dump(tag)
    }), 201


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PUT /api/tags/<id> — Update a tag
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tags_bp.route('/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update(tag_id):
    """Update a tag's name or color."""

    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        data = tag_update_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    if 'name' in data:
        existing = Tag.query.filter_by(name=data['name']).first()
        if existing and existing.id != tag_id:
            return jsonify({'error': 'A tag with this name already exists'}), 409
        tag.name = data['name']
    if 'color' in data:
        tag.color = data['color']

    db.session.commit()

    return jsonify({
        'message': 'Tag updated successfully',
        'tag': tag_schema.dump(tag)
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DELETE /api/tags/<id> — Delete a tag
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def destroy(tag_id):
    """
    Delete a tag.
    SQLAlchemy automatically removes rows from the task_tags pivot table too
    because of the CASCADE set on the foreign key — same as Laravel's cascadeOnDelete().
    """

    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404

    db.session.delete(tag)
    db.session.commit()

    return jsonify({'message': 'Tag deleted successfully'}), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/tags/<tag_id>/attach/<task_id>  — Attach tag to task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tags_bp.route('/<int:tag_id>/attach/<int:task_id>', methods=['POST'])
@jwt_required()
def attach(tag_id, task_id):
    """
    Attach a tag to a task (adds a row in the task_tags pivot table).

    Laravel equivalent:
      $task->tags()->attach($tagId);
      // This inserts: INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)

    SQLAlchemy equivalent:
      task.tags.append(tag)
      db.session.commit()
    """

    current_user_id = int(get_jwt_identity())

    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404

    task = get_accessible_task(task_id, current_user_id)
    if not task:
        return jsonify({'error': 'Task not found or access denied'}), 404

    # Check if already attached — like checking before attach() to avoid duplicates
    if tag in task.tags:
        return jsonify({'error': 'Tag is already attached to this task'}), 409

    # Attach: append to the relationship list → SQLAlchemy inserts into task_tags
    # Laravel: $task->tags()->attach($tagId);
    task.tags.append(tag)
    db.session.commit()

    return jsonify({
        'message': f'Tag "{tag.name}" attached to task "{task.title}"',
        'task_id': task.id,
        'tag': tag_schema.dump(tag)
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DELETE /api/tags/<tag_id>/detach/<task_id> — Detach tag from task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tags_bp.route('/<int:tag_id>/detach/<int:task_id>', methods=['DELETE'])
@jwt_required()
def detach(tag_id, task_id):
    """
    Detach a tag from a task (removes the row from task_tags pivot table).

    Laravel equivalent:
      $task->tags()->detach($tagId);
      // This deletes: DELETE FROM task_tags WHERE task_id=? AND tag_id=?

    SQLAlchemy equivalent:
      task.tags.remove(tag)
      db.session.commit()
    """

    current_user_id = int(get_jwt_identity())

    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404

    task = get_accessible_task(task_id, current_user_id)
    if not task:
        return jsonify({'error': 'Task not found or access denied'}), 404

    if tag not in task.tags:
        return jsonify({'error': 'Tag is not attached to this task'}), 409

    # Detach: remove from the relationship list → SQLAlchemy deletes from task_tags
    # Laravel: $task->tags()->detach($tagId);
    task.tags.remove(tag)
    db.session.commit()

    return jsonify({
        'message': f'Tag "{tag.name}" detached from task "{task.title}"'
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/tags/task/<task_id> — Get all tags for a task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tags_bp.route('/task/<int:task_id>', methods=['GET'])
@jwt_required()
def task_tags_list(task_id):
    """
    Get all tags currently attached to a task.

    Laravel equivalent:
      return TagResource::collection($task->tags);
    """

    current_user_id = int(get_jwt_identity())
    task = get_accessible_task(task_id, current_user_id)

    if not task:
        return jsonify({'error': 'Task not found or access denied'}), 404

    return jsonify({
        'task_id': task.id,
        'task_title': task.title,
        'tags': tags_schema.dump(task.tags)
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/tags/sync/<task_id> — Sync tags on a task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@tags_bp.route('/sync/<int:task_id>', methods=['POST'])
@jwt_required()
def sync(task_id):
    """
    Replace ALL tags on a task with the provided list.

    Laravel equivalent:
      $task->tags()->sync([1, 2, 3]);
      // Removes any existing tags not in the list, adds new ones.

    SQLAlchemy equivalent:
      task.tags = [tag1, tag2, tag3]   ← just reassign the whole list!
      db.session.commit()
    """

    current_user_id = int(get_jwt_identity())
    task = get_accessible_task(task_id, current_user_id)

    if not task:
        return jsonify({'error': 'Task not found or access denied'}), 404

    json_data = request.get_json()
    if not json_data or 'tag_ids' not in json_data:
        return jsonify({'error': 'tag_ids array is required'}), 400

    tag_ids = json_data['tag_ids']
    if not isinstance(tag_ids, list):
        return jsonify({'error': 'tag_ids must be an array'}), 400

    # Fetch all the requested tags
    new_tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    # Validate all requested tag IDs actually exist
    if len(new_tags) != len(tag_ids):
        return jsonify({'error': 'One or more tag IDs do not exist'}), 404

    # SYNC: just reassign the entire relationship list
    # SQLAlchemy handles the diff and updates the pivot table automatically.
    # Laravel: $task->tags()->sync($tagIds);
    task.tags = new_tags
    db.session.commit()

    return jsonify({
        'message': 'Tags synced successfully',
        'task_id': task.id,
        'tags': tags_schema.dump(task.tags)
    }), 200
