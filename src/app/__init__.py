import os
from flask import Flask, session, send_from_directory
from app.home import home as home_blueprint
from app.settings import settings as settings_blueprint
from app.browser import browser as browser_blueprint
from app.report import report as report_blueprint


"""
This is the frontend of the webapp.
"""


def create_app(config: dict) -> Flask:
    # create an instance of the Flask class
    app = Flask(
        __name__, 
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    )

    # Serve files from the 'Icons' folder
    icons_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Screen_Time_Tracker', 'Icons')
    os.makedirs(icons_dir, exist_ok=True)
    websites_icons_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Screen_Time_Tracker', 'Websites_Icons')
    os.makedirs(icons_dir, exist_ok=True)
    @app.route('/Icons/<path:filename>')
    def serve_icon(filename):
        return send_from_directory(icons_dir, filename)
    @app.route('/Websites_Icons/<path:filename>')
    def serve_website_icon(filename):
        return send_from_directory(websites_icons_dir, filename)



    app.secret_key = os.urandom(24)
    # register the blueprints (each blueprint is responsible for a route)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(settings_blueprint)
    app.register_blueprint(browser_blueprint)
    app.register_blueprint(report_blueprint)
    
    # load user preferences to the session
    @app.before_request
    def load_user_preferences():
        session['settings'] = config

    return app
