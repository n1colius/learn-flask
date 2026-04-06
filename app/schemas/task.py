"""
=== app/schemas/task.py ===
Task schemas for validation and serialization.
"""

from app import ma
from marshmallow import fields, validate


class TaskSchema(ma.Schema):
    """Response schema for tasks."""

    class Meta:
        fields = ('id', 'title', 'description', 'status', 'priority', 'due_date',
                  'project_id', 'created_at', 'updated_at')


class TaskCreateSchema(ma.Schema):
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


class TaskUpdateSchema(ma.Schema):
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
