"""
=== seed.py ===
Database seeder — creates sample data for testing.

Laravel equivalent: database/seeders/DatabaseSeeder.php
Run with: python seed.py (like "php artisan db:seed")

This script:
1. Creates all tables (like running migrations)
2. Inserts sample data (like seeders)
"""

from app import create_app, db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.comment import Comment
from app.models.tag import Tag

app = create_app()

with app.app_context():
    # ── Create all tables ───────────────────────────────────────
    # Laravel: php artisan migrate
    # This reads all your model definitions and creates matching tables.
    print('Creating database tables...')
    db.create_all()

    # ── Check if data already exists ────────────────────────────
    if User.query.first():
        print('Database already has data. Skipping seed.')
        print('To reset: delete the instance/app.db file and run again.')
    else:
        # ── Create sample users ─────────────────────────────────
        print('Seeding users...')
        user1 = User(name='John Doe', email='john@example.com')
        user1.set_password('password123')

        user2 = User(name='Jane Smith', email='jane@example.com')
        user2.set_password('password123')

        db.session.add_all([user1, user2])
        db.session.commit()  # Commit so users get their IDs

        # ── Create sample projects ──────────────────────────────
        print('Seeding projects...')
        project1 = Project(
            name='E-Commerce Backend',
            description='REST API for an online store',
            status='active',
            user_id=user1.id
        )
        project2 = Project(
            name='Blog Platform',
            description='Content management system API',
            status='active',
            user_id=user1.id
        )
        project3 = Project(
            name='Mobile App API',
            description='Backend for the mobile application',
            status='active',
            user_id=user2.id
        )

        db.session.add_all([project1, project2, project3])
        db.session.commit()

        # ── Create sample tasks ─────────────────────────────────
        print('Seeding tasks...')
        task1 = Task(title='Set up authentication',   description='Implement JWT auth',        status='done',        priority='high',   project_id=project1.id)
        task2 = Task(title='Create product endpoints',description='CRUD for products',          status='in_progress', priority='high',   project_id=project1.id)
        task3 = Task(title='Add payment integration', description='Stripe API integration',     status='todo',        priority='medium', project_id=project1.id)
        task4 = Task(title='Write API documentation', description='OpenAPI/Swagger docs',       status='todo',        priority='low',    project_id=project1.id)
        task5 = Task(title='Create post endpoints',   description='CRUD for blog posts',        status='done',        priority='high',   project_id=project2.id)
        task6 = Task(title='Add comment system',      description='Nested comments API',        status='in_progress', priority='medium', project_id=project2.id)
        task7 = Task(title='User onboarding flow',    description='Welcome screens API',        status='todo',        priority='high',   project_id=project3.id)
        task8 = Task(title='Push notifications',      description='Firebase integration',       status='todo',        priority='medium', project_id=project3.id)

        db.session.add_all([task1, task2, task3, task4, task5, task6, task7, task8])
        db.session.commit()

        # ── Create sample tags ──────────────────────────────────
        # Tags are global — not owned by any user, just like GitHub labels.
        print('Seeding tags...')
        tag_bug      = Tag(name='bug',      color='#E74C3C')  # red
        tag_feature  = Tag(name='feature',  color='#3498DB')  # blue
        tag_urgent   = Tag(name='urgent',   color='#E67E22')  # orange
        tag_backend  = Tag(name='backend',  color='#9B59B6')  # purple
        tag_frontend = Tag(name='frontend', color='#2ECC71')  # green
        tag_docs     = Tag(name='docs',     color='#95A5A6')  # grey

        db.session.add_all([tag_bug, tag_feature, tag_urgent, tag_backend, tag_frontend, tag_docs])
        db.session.commit()

        # ── Attach tags to tasks (Many-to-Many) ─────────────────
        # Laravel equivalent: $task->tags()->attach([$tagId1, $tagId2]);
        # SQLAlchemy: append to the relationship list, then commit.
        print('Attaching tags to tasks...')

        task1.tags = [tag_backend, tag_feature]       # JWT setup → backend + feature
        task2.tags = [tag_backend, tag_feature]       # Product CRUD → backend + feature
        task3.tags = [tag_backend, tag_urgent]        # Stripe → backend + urgent
        task4.tags = [tag_docs]                       # Docs → docs
        task5.tags = [tag_backend, tag_feature]       # Blog posts → backend + feature
        task6.tags = [tag_backend, tag_feature]       # Comments → backend + feature
        task7.tags = [tag_frontend, tag_feature]      # Onboarding → frontend + feature
        task8.tags = [tag_backend, tag_urgent]        # Push notifs → backend + urgent

        db.session.commit()

        # ── Create sample comments ──────────────────────────────
        # Comments belong to a Task AND a User.
        print('Seeding comments...')
        comments = [
            Comment(body='Authentication is done, tested with Postman.',  task_id=task1.id, user_id=user1.id),
            Comment(body='Should we add refresh tokens too?',              task_id=task1.id, user_id=user2.id),
            Comment(body='Yes, lets add refresh tokens in a follow-up.',   task_id=task1.id, user_id=user1.id),
            Comment(body='Working on GET /products and POST /products.',   task_id=task2.id, user_id=user1.id),
            Comment(body='Remember to add pagination to the list endpoint.',task_id=task2.id, user_id=user2.id),
            Comment(body='Stripe test keys are in the .env.example file.', task_id=task3.id, user_id=user1.id),
            Comment(body='Great progress! The blog API looks clean.',      task_id=task5.id, user_id=user2.id),
        ]

        db.session.add_all(comments)
        db.session.commit()

        print('\nDatabase seeded successfully!')
        print(f'  Users:    {User.query.count()}')
        print(f'  Projects: {Project.query.count()}')
        print(f'  Tasks:    {Task.query.count()}')
        print(f'  Tags:     {Tag.query.count()}')
        print(f'  Comments: {Comment.query.count()}')
        print()
        print('Test credentials:')
        print('  Email: john@example.com  |  Password: password123')
        print('  Email: jane@example.com  |  Password: password123')
