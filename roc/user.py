from flask import Blueprint, render_template

from roc.models import User
from roc.auth import login_required

bp = Blueprint('user', __name__, url_prefix='/user')


""" User info page. """
@bp.route('/about')
@login_required
def about():
    user = User.get_logged_in()
    page_title = 'Admin Account' if user.is_admin else 'Account'
    return render_template('user/user.html', user=user, title=page_title)
