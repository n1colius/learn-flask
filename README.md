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
│   │   ├── user.py           # User model
│   │   ├── project.py        # Project model (belongsTo User, hasMany Tasks)
│   │   └── task.py           # Task model (belongsTo Project)
│   │
│   ├── schemas/              # Validation + Serialization (like FormRequests + Resources)
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   │
│   └── routes/               # Route handlers (like Controllers + routes/api.php)
│       ├── auth.py           # Auth routes (register, login, me)
│       ├── projects.py       # Project CRUD
│       └── tasks.py          # Task CRUD
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

### Query Parameters (Filtering & Pagination)
```
GET /api/projects?status=active&page=1&per_page=10
GET /api/tasks?project_id=1&status=todo&priority=high&page=1&per_page=10
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
