"""
=== app/schemas/task.py ===
Task schemas for validation and serialization.
"""

from marshmallow import Schema, fields, validate


class TaskSchema(Schema):
    """Response schema for tasks."""

    id = fields.Integer(dump_only=True)
    title = fields.String(dump_only=True)
    description = fields.String(dump_only=True, allow_none=True)
    status = fields.String(dump_only=True)
    priority = fields.String(dump_only=True)
    due_date = fields.DateTime(dump_only=True, allow_none=True)
    project_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TaskCreateSchema(Schema):
    """Validation for creating a task."""

    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default=None)
    status = fields.String(
        load_default='todo',
        validate=validate.OneOf(['todo', 'in_progress', 'done'])
    )
    priority = fields.String(
        load_default='medium',
        validate=validate.OneOf(['low', 'medium', 'high'])
    )
    due_date = fields.DateTime(load_default=None)
    project_id = fields.Integer(required=True)


class TaskUpdateSchema(Schema):
    """Validation for updating a task (all fields optional)."""

    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    status = fields.String(validate=validate.OneOf(['todo', 'in_progress', 'done']))
    priority = fields.String(validate=validate.OneOf(['low', 'medium', 'high']))
    due_date = fields.DateTime(allow_none=True)
    project_id = fields.Integer()


# Reusable instances
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
task_create_schema = TaskCreateSchema()
task_update_schema = TaskUpdateSchema()
