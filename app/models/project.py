"""
=== app/models/project.py ===
Project model — defines the projects table.

Laravel equivalent: app/Models/Project.php

A Project belongs to a User and has many Tasks.
This is the same relationship pattern you'd use in Laravel:
  User --hasMany--> Project --hasMany--> Task
"""

from datetime import datetime, timezone
from app import db


class Project(db.Model):
    __tablename__ = 'projects'

    # ── Columns ─────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)  # nullable=True is like ->nullable() in Laravel migration
    status = db.Column(
        db.String(20),
        nullable=False,
        default='active'  # Like $table->string('status')->default('active')
    )

    # ── Foreign Key ─────────────────────────────────────────────
    # Laravel migration: $table->foreignId('user_id')->constrained();
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ───────────────────────────────────────────
    # belongsTo relationship — Laravel: return $this->belongsTo(User::class);
    user = db.relationship('User', back_populates='projects')

    # hasMany relationship — Laravel: return $this->hasMany(Task::class);
    # cascade='all, delete-orphan' means: when a project is deleted,
    # all its tasks are deleted too (like cascadeOnDelete() in Laravel)
    tasks = db.relationship('Task', back_populates='project', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.name}>'
