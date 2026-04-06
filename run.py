"""
=== run.py ===
This is the entry point of the application.
Laravel equivalent: "php artisan serve"
You run this with: python run.py

In Laravel, index.php bootstraps everything. Here, run.py does the same.
"""

from app import create_app

# create_app() is a "factory function" — it builds and configures the Flask app.
# Laravel equivalent: the bootstrap/app.php file that wires everything together.
app = create_app()

if __name__ == '__main__':
    # host='0.0.0.0' makes it accessible from other machines (like --host in artisan serve)
    # debug=True auto-reloads on code changes (like Laravel's hot reload)
    app.run(host='0.0.0.0', port=5000, debug=True)
