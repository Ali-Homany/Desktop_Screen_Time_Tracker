import os
from flask import Flask
from app.charts import charts as charts_blueprint
from app.home import home as home_blueprint


def create_app() -> Flask:
    app = Flask(
        __name__, 
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    )

    app.secret_key = os.urandom(24)

    app.register_blueprint(home_blueprint)
    app.register_blueprint(charts_blueprint)

    return app
