"""Flask application factory.

Boilerplate -- registers blueprints and starts the app. The only exercise
touching this file is DAST-3 (security headers) -- see REQUIREMENTS.md.
"""
import os

from flask import Flask

from app.config import Config
from app.db import init_db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db()

    from app.routes.health import bp as health_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.files import bp as files_bp
    from app.routes.admin import bp as admin_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(admin_bp)

    # TODO (DAST-3): this app currently sends no security headers at all
    # (no Content-Security-Policy, no X-Content-Type-Options, no
    # Strict-Transport-Security). Leave it that way until a DAST scan
    # flags it -- then add an `after_request` hook here.
    # See REQUIREMENTS.md#DAST-3.

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
