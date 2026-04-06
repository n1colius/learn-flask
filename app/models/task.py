"""
=== app/models/task.py ===
Task model — defines the tasks table.

Laravel equivalent: app/Models/Task.php

A Task belongs to a Project (and indirectly to a User).
"""

from datetime import datetime, timezone
from app import db


class Task(db.Model):
    __tablename__ = 'tasks'

    # ── Columns ─────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='todo')
    priority = db.Column(db.String(10), nullable=False, default='medium')  # low, medium, high
    due_date = db.Column(db.DateTime, nullable=True)

    # Foreign Key — this task belongs to a project
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ───────────────────────────────────────────
    # belongsTo — Laravel: return $this->belongsTo(Project::class);
    project = db.relationship('Project', back_populates='tasks')

    def __repr__(self):
        return f'<Task {self.title}>'
