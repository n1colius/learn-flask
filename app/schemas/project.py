"""
=== app/schemas/project.py ===
Project schemas for validation and serialization.
"""

from app import ma
from marshmallow import fields, validate


class ProjectSchema(ma.Schema):
    """
    Response schema — what gets returned when you fetch a project.
    Laravel equivalent: ProjectResource
    """

    class Meta:
        fields = ('id', 'name', 'description', 'status', 'user_id', 'created_at', 'updated_at')


class ProjectCreateSchema(ma.Schema):
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


class ProjectUpdateSchema(ma.Schema):
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
