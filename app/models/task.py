"""
=== app/models/task.py ===
Task model — defines the tasks table.

Laravel equivalent: app/Models/Task.php

A Task belongs to a Project (and indirectly to a User).

RELATIONSHIPS ON THIS MODEL:
  Task --belongsTo-->    Project      (One-to-Many, inverse side)
  Task --hasMany-->      Comment      (One-to-Many)
  Task --belongsToMany-> Tag          (Many-to-Many via task_tags pivot table)

Full hierarchy:
  User → Projects → Tasks → Comments
                          ↕ (via task_tags pivot)
                         Tags
"""

from datetime import datetime, timezone
from app import db
from app.models.tag import task_tags   # Import the pivot table defined in tag.py


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

    # ONE-TO-MANY (belongsTo side)
    # Laravel: return $this->belongsTo(Project::class);
    project = db.relationship('Project', back_populates='tasks')

    # ONE-TO-MANY (hasMany side) → Task hasMany Comments
    # Laravel: return $this->hasMany(Comment::class);
    # cascade='all, delete-orphan' = when a Task is deleted, all its Comments are deleted too
    comments = db.relationship('Comment', back_populates='task', lazy=True, cascade='all, delete-orphan')

    # MANY-TO-MANY → Task belongsToMany Tags (via task_tags pivot table)
    # Laravel: return $this->belongsToMany(Tag::class, 'task_tags');
    #
    # secondary=task_tags  → use the pivot table we imported from tag.py
    # lazy='subquery'      → load tags in a single extra query (more efficient for lists)
    #                        In Laravel terms: eager loading is like ->with('tags')
    tags = db.relationship(
        'Tag',
        secondary=task_tags,   # The pivot table
        back_populates='tasks', # Matching relationship on Tag model
        lazy='subquery'
    )

    def __repr__(self):
        return f'<Task {self.title}>'
