from flask import Flask

from app.config import Config
from app.core.auth import get_current_user
from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.public import public_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(health_bp)

    @app.context_processor
    def inject_user():
        return {"current_user": get_current_user()}

    return app
