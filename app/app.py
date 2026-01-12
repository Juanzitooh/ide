from flask import Flask

from app.config import Config
from app.routes.health import health_bp
from app.routes.public import public_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(public_bp)
    app.register_blueprint(health_bp)

    return app
