"""
=== app/models/comment.py ===
Comment model — a Task can have many Comments.

Laravel equivalent: app/Models/Comment.php

RELATIONSHIP TYPE: One-to-Many (hasMany / belongsTo)
  Task  --hasMany-->   Comment
  Comment --belongsTo--> Task
  Comment --belongsTo--> User  (who wrote the comment)

This is the same relationship pattern as Project → Tasks,
just one level deeper in the hierarchy:
  User → Projects → Tasks → Comments
"""

from datetime import datetime, timezone
from app import db


class Comment(db.Model):
    __tablename__ = 'comments'

    # ── Columns ─────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)   # The comment text

    # ── Foreign Keys ─────────────────────────────────────────────
    # A comment belongs to a Task
    # Laravel migration: $table->foreignId('task_id')->constrained()->cascadeOnDelete();
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    # A comment belongs to a User (who wrote it)
    # Laravel migration: $table->foreignId('user_id')->constrained();
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ─────────────────────────────────────────────
    # belongsTo Task — Laravel: return $this->belongsTo(Task::class);
    task = db.relationship('Task', back_populates='comments')

    # belongsTo User — Laravel: return $this->belongsTo(User::class);
    user = db.relationship('User', backref='comments')
    # Note: backref='comments' is a shorthand that auto-creates
    # user.comments on the User model (without needing to edit User model).
    # It's equivalent to adding:
    #   comments = db.relationship('Comment', back_populates='user') in User model

    def __repr__(self):
        return f'<Comment {self.id} on Task {self.task_id}>'
