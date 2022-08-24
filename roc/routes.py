from flask import render_template, Blueprint, flash

from roc.models import User

bp = Blueprint('routes', __name__)


""" Home page. """
@bp.route('/')
def home():
    user = User.get_logged_in()
    info = None if user is None else user.id
    return render_template('home.html', user=user)
