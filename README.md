# Flask Task Management API

A real-world REST API built with Flask — designed for Laravel developers learning Python.

Every file has comments mapping Flask concepts to their Laravel equivalents.

## Quick Start

```bash
# 1. Create virtual environment (like a project-specific "vendor" folder)
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# 3. Install dependencies (like "composer install")
pip install -r requirements.txt

# 4. Seed the database with sample data (like "php artisan db:seed")
python seed.py

# 5. Run the server (like "php artisan serve")
python run.py
```

The API will be running at `http://localhost:5000`

## Project Structure (Laravel Comparison)

```
learn-flask/
├── run.py                    # Entry point (like "php artisan serve")
├── seed.py                   # Database seeder (like "php artisan db:seed")
├── requirements.txt          # Dependencies (like composer.json)
├── .env                      # Environment variables (same as Laravel)
│
├── app/
│   ├── __init__.py           # App factory (like bootstrap/app.php)
│   ├── config.py             # Configuration (like config/*.php)
│   ├── errors.py             # Error handlers (like app/Exceptions/Handler.php)
│   │
│   ├── models/               # Database models (like app/Models/)
│   │   ├── user.py           # User — hasMany Projects, hasMany Comments
│   │   ├── project.py        # Project — belongsTo User, hasMany Tasks
│   │   ├── task.py           # Task — belongsTo Project, hasMany Comments, belongsToMany Tags
│   │   ├── comment.py        # Comment — belongsTo Task, belongsTo User
│   │   └── tag.py            # Tag — belongsToMany Tasks (via task_tags pivot table)
│   │
│   ├── schemas/              # Validation + Serialization (like FormRequests + Resources)
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   ├── comment.py
│   │   └── tag.py
│   │
│   └── routes/               # Route handlers (like Controllers + routes/api.php)
│       ├── auth.py           # Auth routes (register, login, me)
│       ├── projects.py       # Project CRUD
│       ├── tasks.py          # Task CRUD
│       ├── comments.py       # Comment CRUD (nested under tasks)
│       └── tags.py           # Tag CRUD + attach/detach/sync (Many-to-Many)
│
└── migrations/               # Auto-generated migration files (like database/migrations/)
    └── versions/             # Each file = one migration (auto-created by flask db migrate)
```

### Database Relationships

```
User
 ├── hasMany ──────────────→ Project
 │                              └── hasMany ──→ Task
 │                                              ├── hasMany ──────→ Comment ←── belongsTo ── User
 │                                              └── belongsToMany → Tag
 │                                                    (via task_tags pivot table)
 └── hasMany ──────────────→ Comment
```

## API Endpoints

### Auth
| Method | Endpoint             | Description        | Auth Required |
|--------|---------------------|--------------------|---------------|
| POST   | `/api/auth/register` | Register new user  | No            |
| POST   | `/api/auth/login`    | Login, get token   | No            |
| GET    | `/api/auth/me`       | Get current user   | Yes           |

### Projects
| Method | Endpoint               | Description        | Auth Required |
|--------|------------------------|--------------------|---------------|
| GET    | `/api/projects`        | List your projects | Yes           |
| POST   | `/api/projects`        | Create project     | Yes           |
| GET    | `/api/projects/<id>`   | Get one project    | Yes           |
| PUT    | `/api/projects/<id>`   | Update project     | Yes           |
| DELETE | `/api/projects/<id>`   | Delete project     | Yes           |

### Tasks
| Method | Endpoint            | Description    | Auth Required |
|--------|---------------------|----------------|---------------|
| GET    | `/api/tasks`        | List tasks     | Yes           |
| POST   | `/api/tasks`        | Create task    | Yes           |
| GET    | `/api/tasks/<id>`   | Get one task   | Yes           |
| PUT    | `/api/tasks/<id>`   | Update task    | Yes           |
| DELETE | `/api/tasks/<id>`   | Delete task    | Yes           |

### Comments
| Method | Endpoint               | Description                    | Auth Required |
|--------|------------------------|--------------------------------|---------------|
| GET    | `/api/comments?task_id=1` | List comments on a task     | Yes           |
| POST   | `/api/comments`        | Add a comment to a task        | Yes           |
| PUT    | `/api/comments/<id>`   | Edit your own comment          | Yes           |
| DELETE | `/api/comments/<id>`   | Delete your own comment        | Yes           |

### Tags (CRUD)
| Method | Endpoint            | Description        | Auth Required |
|--------|---------------------|--------------------|---------------|
| GET    | `/api/tags`         | List all tags      | Yes           |
| POST   | `/api/tags`         | Create a tag       | Yes           |
| PUT    | `/api/tags/<id>`    | Update a tag       | Yes           |
| DELETE | `/api/tags/<id>`    | Delete a tag       | Yes           |

### Tags (Many-to-Many — attach / detach / sync)
| Method | Endpoint                              | Description                        | Auth Required |
|--------|---------------------------------------|------------------------------------|---------------|
| POST   | `/api/tags/<tag_id>/attach/<task_id>` | Attach a tag to a task             | Yes           |
| DELETE | `/api/tags/<tag_id>/detach/<task_id>` | Detach a tag from a task           | Yes           |
| POST   | `/api/tags/sync/<task_id>`            | Replace all tags on a task (sync)  | Yes           |
| GET    | `/api/tags/task/<task_id>`            | List all tags on a task            | Yes           |

### Query Parameters (Filtering & Pagination)
```
GET /api/projects?status=active&page=1&per_page=10
GET /api/tasks?project_id=1&status=todo&priority=high&page=1&per_page=10
GET /api/comments?task_id=1
```

## Testing with curl

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "password123"}'

# Use the returned access_token for authenticated requests:
curl http://localhost:5000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Create a project
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name": "My New Project", "description": "A cool project"}'

# Create a task
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"title": "First task", "project_id": 1, "priority": "high"}'
```

## Migrations

Flask uses **Flask-Migrate** (built on top of Alembic) for migrations. The key difference from Laravel is where the schema lives:

| | Laravel | Flask |
|---|---|---|
| **Schema defined in** | Migration files (written manually) | **Model files** (`models/*.py`) |
| **Migration files are** | Written by you | **Auto-generated** from your models |
| **Source of truth** | The migration files | The Python model classes |

> In Laravel: you write the migration → build the model to match.
> In Flask: you write the model → generate the migration from it.

### Command Cheat Sheet

| Laravel | Flask | What it does |
|---|---|---|
| *(run once, like `git init`)* | `flask db init` | Set up the `migrations/` folder — **run only once ever** |
| `php artisan make:migration` | `flask db migrate -m "message"` | Auto-generate a migration file from model changes |
| `php artisan migrate` | `flask db upgrade` | Apply pending migrations to the database |
| `php artisan migrate:rollback` | `flask db downgrade` | Undo the last migration |
| `php artisan migrate:status` | `flask db history` | See full migration history |

### First-Time Setup with Migrations (recommended for real projects)

```bash
# 1. Delete the DB created by seed.py (if it exists)
del instance\app.db        # Windows
# rm instance/app.db       # Mac/Linux

# 2. Initialize the migrations folder (only ever run this ONCE per project)
flask db init

# 3. Auto-generate migration files from your model definitions
flask db migrate -m "initial tables users projects tasks tags comments"

# 4. Apply the migrations — this creates the actual database tables
flask db upgrade

# 5. Seed with sample data
python seed.py
```

### Day-to-Day Workflow — Adding a New Column

**In Laravel** you create the migration manually, then update the model.
**In Flask** you update the model first, then auto-generate the migration.

Example — adding `avatar_url` to the User model:

**Step 1 — Edit the model** (`app/models/user.py`):
```python
# Just add the new column to the class
avatar_url = db.Column(db.String(255), nullable=True)
```

**Step 2 — Auto-generate the migration:**
```bash
flask db migrate -m "add avatar_url to users"
```
Flask-Migrate detects the change and writes the migration file automatically.

**Step 3 — Apply it:**
```bash
flask db upgrade
```

### What a Generated Migration File Looks Like

After `flask db migrate`, a file is created in `migrations/versions/`. You rarely need to edit it:

```python
# migrations/versions/abc123_add_avatar_url_to_users.py

def upgrade():
    # Like the up() method in Laravel
    op.add_column('users', sa.Column('avatar_url', sa.String(255), nullable=True))

def downgrade():
    # Like the down() method in Laravel
    op.drop_column('users', 'avatar_url')
```

### `db.create_all()` vs `flask db upgrade`

| Method | Used in | When to use |
|---|---|---|
| `db.create_all()` | `seed.py` | Quick dev/learning setup — no history tracked |
| `flask db upgrade` | Production workflow | Tracks every change with full version history |

`db.create_all()` only creates **missing** tables — it won't detect column changes or deletions. For anything beyond local learning, always use `flask db upgrade`.

---

## Key Concepts: Laravel → Flask

| Laravel                     | Flask                              |
|-----------------------------|------------------------------------|
| `php artisan serve`         | `python run.py`                    |
| `composer install`          | `pip install -r requirements.txt`  |
| `php artisan migrate`       | `flask db upgrade` or `db.create_all()` |
| `php artisan db:seed`       | `python seed.py`                   |
| Routes in `routes/api.php`  | Blueprints in `app/routes/`        |
| Controllers                 | Route functions in Blueprints      |
| Eloquent ORM                | SQLAlchemy ORM                     |
| Form Requests (validation)  | Marshmallow Schemas                |
| API Resources (serialization)| Marshmallow Schemas (same!)       |
| Middleware                  | Decorators (`@jwt_required()`)     |
| Service Providers           | `init_app()` pattern               |
| `.env` file                 | `.env` file (same!)                |
| `$request->all()`           | `request.get_json()`               |
| `$request->query('key')`   | `request.args.get('key')`          |
| `response()->json()`        | `jsonify()`                        |
| `Hash::make()`              | `bcrypt.hashpw()`                  |
| `Auth::attempt()`           | Manual check + `create_access_token()` |
| `auth()->user()`            | `get_jwt_identity()` + query       |
