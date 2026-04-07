"""
=== app/routes/comments.py ===
Comment routes — CRUD for comments on tasks.

Laravel equivalent: app/Http/Controllers/CommentController.php

Routes:
  GET    /api/comments?task_id=1   → List all comments on a task
  POST   /api/comments             → Add a comment to a task
  PUT    /api/comments/<id>        → Edit your own comment
  DELETE /api/comments/<id>        → Delete your own comment

Authorization rule: you can only edit/delete YOUR OWN comments.
(In Laravel this would be a CommentPolicy)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.task import Task
from app.models.project import Project
from app.models.comment import Comment
from app.schemas.comment import (
    comment_schema, comments_schema,
    comment_create_schema, comment_update_schema
)

comments_bp = Blueprint('comments', __name__)


def user_can_access_task(task_id, user_id):
    """
    Verify the task exists and belongs to a project owned by this user.

    Laravel equivalent:
      $task = Task::whereHas('project', fn($q) => $q->where('user_id', auth()->id()))
                  ->findOrFail($task_id);
    """
    return Task.query.join(Project).filter(
        Task.id == task_id,
        Project.user_id == user_id
    ).first()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/comments?task_id=1
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@comments_bp.route('', methods=['GET'])
@jwt_required()
def index():
    """
    List all comments for a given task.

    Laravel equivalent:
      public function index(Task $task) {
          $this->authorize('view', $task);
          return CommentResource::collection($task->comments()->latest()->get());
      }
    """

    current_user_id = int(get_jwt_identity())
    task_id = request.args.get('task_id', type=int)

    if not task_id:
        return jsonify({'error': 'task_id query parameter is required'}), 400

    # Verify the user can access this task
    task = user_can_access_task(task_id, current_user_id)
    if not task:
        return jsonify({'error': 'Task not found or access denied'}), 404

    comments = Comment.query.filter_by(task_id=task_id)\
                            .order_by(Comment.created_at.asc())\
                            .all()

    return jsonify({
        'comments': comments_schema.dump(comments)
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/comments
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@comments_bp.route('', methods=['POST'])
@jwt_required()
def store():
    """
    Add a new comment to a task.

    Laravel equivalent:
      public function store(StoreCommentRequest $request, Task $task) {
          $comment = $task->comments()->create([
              'body'    => $request->body,
              'user_id' => auth()->id(),
          ]);
          return new CommentResource($comment);
      }
    """

    current_user_id = int(get_jwt_identity())
    json_data = request.get_json()

    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        data = comment_create_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    # Verify the user can access this task
    task = user_can_access_task(data['task_id'], current_user_id)
    if not task:
        return jsonify({'error': 'Task not found or access denied'}), 404

    comment = Comment(
        body=data['body'],
        task_id=data['task_id'],
        user_id=current_user_id
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'message': 'Comment added successfully',
        'comment': comment_schema.dump(comment)
    }), 201


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PUT /api/comments/<id>
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update(comment_id):
    """
    Edit a comment. Only the author can edit their own comment.

    Laravel equivalent (with Policy):
      public function update(UpdateCommentRequest $request, Comment $comment) {
          $this->authorize('update', $comment); // checks comment->user_id == auth()->id()
          $comment->update(['body' => $request->body]);
          return new CommentResource($comment);
      }
    """

    current_user_id = int(get_jwt_identity())
    comment = Comment.query.get(comment_id)

    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    # Authorization: only the author can edit their comment
    # Laravel Policy equivalent: return $comment->user_id === $user->id;
    if comment.user_id != current_user_id:
        return jsonify({'error': 'You can only edit your own comments'}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        data = comment_update_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 422

    comment.body = data['body']
    db.session.commit()

    return jsonify({
        'message': 'Comment updated successfully',
        'comment': comment_schema.dump(comment)
    }), 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DELETE /api/comments/<id>
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def destroy(comment_id):
    """Delete a comment. Only the author can delete their own comment."""

    current_user_id = int(get_jwt_identity())
    comment = Comment.query.get(comment_id)

    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    if comment.user_id != current_user_id:
        return jsonify({'error': 'You can only delete your own comments'}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'message': 'Comment deleted successfully'}), 200
