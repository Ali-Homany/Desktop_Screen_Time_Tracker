from flask import Blueprint, render_template


home = Blueprint('home', __name__)

# Route for the index page
@home.route('/', methods=['GET'])
def index():
    # Render the index page with the empty graph initially
    return render_template('index.html')
