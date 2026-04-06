"""
=== app/errors.py ===
Global error handlers.

Laravel equivalent: app/Exceptions/Handler.php
In Laravel, you customize how exceptions are rendered in the render() method.
In Flask, you register error handlers that catch specific HTTP status codes.
"""

from flask import jsonify


def register_error_handlers(app):
    """
    Register error handlers with the Flask app.

    In Laravel, this is done in Handler.php:
      public function render($request, Throwable $exception) {
          if ($exception instanceof NotFoundHttpException) {
              return response()->json(['error' => 'Not found'], 404);
          }
      }

    In Flask, we use decorators to register handlers for each status code.
    """

    @app.errorhandler(400)
    def bad_request(error):
        """Handles validation errors and bad requests."""
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handles authentication failures."""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Handles authorization failures (authenticated but not allowed)."""
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handles 'resource not found' errors."""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handles wrong HTTP method (e.g., POST to a GET-only route)."""
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'This HTTP method is not allowed for this endpoint'
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handles unexpected server errors."""
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
