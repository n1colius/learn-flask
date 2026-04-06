"""
=== app/models/user.py ===
User model — defines the users table.

Laravel equivalent: app/Models/User.php

KEY CONCEPT — SQLAlchemy vs Eloquent:
  Laravel (Eloquent):
    class User extends Model {
        protected $fillable = ['name', 'email', 'password'];
    }

  Flask (SQLAlchemy):
    class User(db.Model):
        name = db.Column(db.String(100), nullable=False)

The main difference: In Eloquent, columns are defined in migrations.
In SQLAlchemy, columns are defined RIGHT HERE in the model class.
The model IS the schema definition. (Migrations are auto-generated from this.)
"""

from datetime import datetime, timezone
from app import db
import bcrypt


class User(db.Model):
    # ── Table name ──────────────────────────────────────────────
    # Laravel: protected $table = 'users';
    __tablename__ = 'users'

    # ── Columns ─────────────────────────────────────────────────
    # Laravel migration equivalent:
    #   $table->id();
    #   $table->string('name');
    #   $table->string('email')->unique();
    #   $table->string('password');
    #   $table->timestamps();

    id = db.Column(db.Integer, primary_key=True)  # Auto-increment by default
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # created_at and updated_at — like Laravel's $table->timestamps()
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ───────────────────────────────────────────
    # Laravel equivalent:
    #   public function projects() {
    #       return $this->hasMany(Project::class);
    #   }
    #
    # 'back_populates' is like defining the inverse relationship.
    # 'lazy=True' means projects are loaded only when you access user.projects
    # (like Laravel's lazy loading vs eager loading with ->with('projects'))
    projects = db.relationship('Project', back_populates='user', lazy=True)

    # ── Methods ─────────────────────────────────────────────────

    def set_password(self, password):
        """
        Hash the password before storing.
        Laravel equivalent: Hash::make($password)
        """
        self.password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        """
        Verify a password against the hash.
        Laravel equivalent: Hash::check($password, $this->password)
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password.encode('utf-8')
        )

    def __repr__(self):
        """
        String representation for debugging.
        Like Laravel's __toString() or when you dd($user).
        """
        return f'<User {self.email}>'
