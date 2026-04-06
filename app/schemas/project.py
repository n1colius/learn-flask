"""
=== app/schemas/project.py ===
Project schemas for validation and serialization.
"""

from marshmallow import Schema, fields, validate


class ProjectSchema(Schema):
    """
    Response schema — what gets returned when you fetch a project.
    Laravel equivalent: ProjectResource
    """

    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    description = fields.String(dump_only=True, allow_none=True)
    status = fields.String(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProjectCreateSchema(Schema):
    """
    Validation for creating a project.

    Laravel equivalent:
      'name' => 'required|string|max:200',
      'description' => 'nullable|string',
      'status' => 'in:active,archived,completed'
    """

    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default=None)  # load_default=None is like nullable
    status = fields.String(
        load_default='active',
        validate=validate.OneOf(['active', 'archived', 'completed'])  # Like 'in:...' rule in Laravel
    )


class ProjectUpdateSchema(Schema):
    """
    Validation for updating a project.
    All fields optional (partial update / PATCH).

    Laravel equivalent: same rules but with 'sometimes' added to each.
    """

    name = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    status = fields.String(validate=validate.OneOf(['active', 'archived', 'completed']))


# Reusable instances
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
project_create_schema = ProjectCreateSchema()
project_update_schema = ProjectUpdateSchema()
