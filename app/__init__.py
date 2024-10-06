import os
from flask import Flask, session
from app.home import home as home_blueprint
from app.settings import settings as settings_blueprint


def create_app(config: dict) -> Flask:
    app = Flask(
        __name__, 
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    )

    app.secret_key = os.urandom(24)

    app.register_blueprint(home_blueprint)
    app.register_blueprint(settings_blueprint)
    
    @app.before_request
    def load_user_preferences():
        session['settings'] = config

    return app
