"""
=== app/models/tag.py ===
Tag model — Tasks can have many Tags, and Tags can belong to many Tasks.

Laravel equivalent: app/Models/Tag.php

RELATIONSHIP TYPE: Many-to-Many (belongsToMany)
  Task --belongsToMany--> Tag
  Tag  --belongsToMany--> Task

This requires a PIVOT TABLE (junction table) in between:
  tasks  <--  task_tags  -->  tags
  (id)       (task_id)        (id)
             (tag_id)

Laravel migration equivalent:
  Schema::create('task_tags', function (Blueprint $table) {
      $table->foreignId('task_id')->constrained()->cascadeOnDelete();
      $table->foreignId('tag_id')->constrained()->cascadeOnDelete();
      $table->primary(['task_id', 'tag_id']);
  });

Laravel Model equivalent:
  // In Task model:
  public function tags() {
      return $this->belongsToMany(Tag::class, 'task_tags');
  }

  // In Tag model:
  public function tasks() {
      return $this->belongsToMany(Task::class, 'task_tags');
  }

KEY CONCEPT — SQLAlchemy Many-to-Many:
  Step 1: Define a "association table" (the pivot table) using db.Table()
  Step 2: Reference it in db.relationship() using the 'secondary' parameter

  The pivot table here is called 'task_tags'.
  In Laravel you'd call it the "intermediate table" or "pivot table".
"""

from app import db

# ── Step 1: Define the Pivot Table ──────────────────────────────
#
# db.Table() creates a simple table with NO model class —
# it's just a join table, same as in Laravel where pivot tables
# usually don't have their own Model (unless you use ->withPivot()).
#
# Laravel migration equivalent:
#   $table->foreignId('task_id')->constrained()->cascadeOnDelete();
#   $table->foreignId('tag_id')->constrained()->cascadeOnDelete();
#
task_tags = db.Table(
    'task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id',  db.Integer, db.ForeignKey('tags.id',  ondelete='CASCADE'), primary_key=True)
    # Both columns together form the composite primary key (like primary(['task_id', 'tag_id']) in Laravel)
)


class Tag(db.Model):
    __tablename__ = 'tags'

    # ── Columns ─────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # e.g. "bug", "feature", "urgent"
    color = db.Column(db.String(7), nullable=True)                # Hex color e.g. "#FF5733"

    # Tags are global (not per-user), just like labels in GitHub Issues.

    # ── Step 2: Define the Many-to-Many Relationship ────────────
    # 'secondary=task_tags' tells SQLAlchemy to use that pivot table.
    # Laravel equivalent (in Tag model):
    #   public function tasks() {
    #       return $this->belongsToMany(Task::class, 'task_tags');
    #   }
    tasks = db.relationship(
        'Task',
        secondary=task_tags,       # The pivot table
        back_populates='tags'      # The matching relationship on Task model
    )

    def __repr__(self):
        return f'<Tag {self.name}>'
