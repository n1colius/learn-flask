"""
=== app/models/__init__.py ===
This file makes the models folder a Python package and imports all models.

Laravel equivalent: This is like having all your Models auto-discovered.
In Laravel, models live in app/Models/. In Flask, we put them in app/models/.
"""

# Import all models here so they're registered with SQLAlchemy
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
