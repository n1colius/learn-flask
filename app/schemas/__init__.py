"""
=== app/schemas/__init__.py ===
Marshmallow schemas for request validation and response serialization.

Laravel equivalents combined:
  - Form Request classes (validation): app/Http/Requests/StoreUserRequest.php
  - API Resources (serialization): app/Http/Resources/UserResource.php

In Laravel, these are TWO separate concepts. In Flask + Marshmallow,
ONE schema handles BOTH validation and serialization. Pretty neat!
"""

from app.schemas.user import UserSchema, UserLoginSchema, UserRegisterSchema
from app.schemas.project import ProjectSchema, ProjectCreateSchema, ProjectUpdateSchema
from app.schemas.task import TaskSchema, TaskCreateSchema, TaskUpdateSchema
