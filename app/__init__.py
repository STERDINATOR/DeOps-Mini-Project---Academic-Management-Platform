"""Application factory for Academic Management Platform."""

import os
from flask import Flask
from database.db import get_db
from app.routes.api import api_bp
from app.routes.web import web_bp


def create_app(test_config=None) -> Flask:
    """Create and configure the Flask application."""
    base_dir = os.path.abspath(os.path.dirname(__file__))
    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    app = Flask(
        __name__,
        template_folder=templates_dir,
        static_folder=static_dir
    )

    app.config.from_mapping(
        SECRET_KEY="devops-academic-platform-secret-key",
        JSON_SORT_KEYS=False
    )

    if test_config is not None:
        app.config.update(test_config)

    # Initialize the database singleton
    get_db()

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    return app
