"""
=== app/schemas/comment.py ===
Comment schemas for validation and serialization.
"""

from marshmallow import Schema, fields, validate


class CommentSchema(Schema):
    """Response schema — what gets returned when fetching comments."""

    id = fields.Integer(dump_only=True)
    body = fields.String(dump_only=True)
    task_id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class CommentCreateSchema(Schema):
    """
    Validation for creating a comment.

    Laravel equivalent:
      'body' => 'required|string|min:1',
      'task_id' => 'required|integer|exists:tasks,id'
    """

    body = fields.String(required=True, validate=validate.Length(min=1))
    task_id = fields.Integer(required=True)


class CommentUpdateSchema(Schema):
    """Validation for editing a comment (only body can change)."""

    body = fields.String(required=True, validate=validate.Length(min=1))


# Reusable instances
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
comment_create_schema = CommentCreateSchema()
comment_update_schema = CommentUpdateSchema()
