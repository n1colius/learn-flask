"""
=== app/__init__.py ===
This is the APPLICATION FACTORY.

Laravel equivalent: This is like bootstrap/app.php + config/app.php combined.
It creates the Flask app, loads config, and registers all the pieces.

In Python, __init__.py makes a folder into a "package" (importable module).
Think of it like a namespace in PHP.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# These are like Laravel's "facades" — global instances you import anywhere.
# In Laravel you'd do: use Illuminate\Support\Facades\DB;
# In Flask you do: from app import db
db = SQLAlchemy()          # Database ORM (like Eloquent)
migrate = Migrate()        # Migration manager (like artisan migrate)
jwt = JWTManager()         # JWT auth (like Sanctum)


def create_app():
    """
    Factory function that creates and configures the Flask application.

    Laravel equivalent: This is like what happens in bootstrap/app.php —
    it wires up all service providers, middleware, and routes.
    """

    # Create the Flask app instance
    # __name__ tells Flask where to find templates/static files
    app = Flask(__name__)

    # ── Load Configuration ──────────────────────────────────────────
    # Laravel equivalent: config/database.php, config/app.php, etc.
    app.config.from_object('app.config.Config')

    # ── Initialize Extensions ───────────────────────────────────────
    # Laravel equivalent: Registering Service Providers in config/app.php
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ── Register Blueprints (Routes) ───────────────────────────────
    # Laravel equivalent: Route::prefix('api')->group(...) in routes/api.php
    # Blueprints are like route groups with a prefix.
    from app.routes.auth import auth_bp
    from app.routes.projects import projects_bp
    from app.routes.tasks import tasks_bp
    from app.routes.comments import comments_bp
    from app.routes.tags import tags_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(comments_bp, url_prefix='/api/comments')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')

    # ── Register Error Handlers ─────────────────────────────────────
    # Laravel equivalent: app/Exceptions/Handler.php
    from app.errors import register_error_handlers
    register_error_handlers(app)

    return app
