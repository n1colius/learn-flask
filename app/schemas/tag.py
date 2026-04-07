"""
=== app/schemas/tag.py ===
Tag schemas for validation and serialization.
"""

from marshmallow import Schema, fields, validate


class TagSchema(Schema):
    """Response schema for a tag."""

    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    color = fields.String(dump_only=True, allow_none=True)


class TagCreateSchema(Schema):
    """
    Validation for creating a tag.

    Laravel equivalent:
      'name'  => 'required|string|max:50|unique:tags',
      'color' => 'nullable|string|regex:/^#[0-9A-Fa-f]{6}$/'
    """

    name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    color = fields.String(
        load_default=None,
        validate=validate.Regexp(
            r'^#[0-9A-Fa-f]{6}$',
            error='Color must be a valid hex code like #FF5733'
        )
    )


class TagUpdateSchema(Schema):
    """Validation for updating a tag."""

    name = fields.String(validate=validate.Length(min=1, max=50))
    color = fields.String(
        allow_none=True,
        validate=validate.Regexp(
            r'^#[0-9A-Fa-f]{6}$',
            error='Color must be a valid hex code like #FF5733'
        )
    )


# Reusable instances
tag_schema = TagSchema()
tags_schema = TagSchema(many=True)
tag_create_schema = TagCreateSchema()
tag_update_schema = TagUpdateSchema()
