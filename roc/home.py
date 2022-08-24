from flask import render_template, Blueprint, flash

from roc.logger import Logger
from roc.models import User

bp = Blueprint('home', __name__)


""" Home page. """
@bp.route('/')
def home():
    user = User.get_logged_in()
    info = None if user is None else user.id
    Logger.log_event('visit-home-page', info=info)
    return render_template('home.html', user=user)
