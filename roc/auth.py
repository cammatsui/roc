import functools
from flask import Blueprint, render_template, url_for, redirect, flash, jsonify

from roc.models import User
from roc import DB_URI, TEST_DB_URI 
from flask import current_app
from roc.forms import LoginForm, RegistrationForm, ResetForm, ResetRequestForm

AWS_REGION = 'us-east-1'
bp = Blueprint('auth', __name__, url_prefix='/auth')


""" Login page. """
@bp.route('/login', methods=['GET', 'POST'])
def login():
    user = User.get_logged_in()
    if user is not None: return redirect(url_for('routes.home'))
    page_title = 'Login'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.login(form.email.data, form.password.data)
        if user is None:
            flash(f'Failed to login. Please check your email and password.', 'danger')
        elif not user.confirmed:
            flash(f'Please verify your account via email.', 'danger')
        else:
            flash(f'Logged into account for email {form.email.data}.', 'success')
            return redirect(url_for('routes.home'))
    return render_template('auth/login.html', form=form, title=page_title)

ROC_CONF_SUBJ = 'RateOurCourses: Confirm Account'
ROC_CONF_MSG = 'Click the link below to confirm your account:\n'
""" Register page. """
@bp.route('/register', methods=['GET', 'POST'])
def register():
    user = User.get_logged_in()
    if user is not None: return redirect(url_for('routes.home'))
    page_title = "Register"
    form = RegistrationForm()
    if form.validate_on_submit():
        if len(User.query.filter_by(email=form.email.data).all()) > 0:
            flash(f'An account with that email already exists!', 'danger')
        else: 
            maybe_user = User.register(form.email.data, form.password.data)
            if maybe_user is not None:
                flash(f'Created account for email {form.email.data}.', 'success')
                user = maybe_user
                confirm_url = f'www.rateourcourses.com/confirm/{user.id}/{user.token}'
                send_email([user.email], ROC_CONF_SUBJ, ROC_CONF_MSG+confirm_url)
                return redirect(url_for('routes.home'))
            flash(f'Email must be an Amherst student email.', 'danger')
    return render_template('auth/register.html', form=form, title=page_title)

ROC_RESET_SUBJ = 'RateOurCourses: Reset Password'
ROC_RESET_MSG = 'Click the link below to reset your password for Rate Our Courses:<br>'
""" Request password reset. """
@bp.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    user = User.get_logged_in()
    if user is not None: return redirect(url_for('routes.home'))
    page_title = 'Reset Password'
    form = ResetRequestForm()
    if form.validate_on_submit:
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            user.reset_token()
            reset_url = f'www.rateourcourses.com/{user.id}/{user.token}'
            send_email([user.email], ROC_RESET_SUBJ, ROC_RESET_MSG+reset_url)
            flash(f'Sent password reset email if account exists.')
    return render_template('auth/reset_request.html', form=form, title=page_title)

""" Reset password. """
@bp.route('/reset/<uid>/<token>', methods=['GET', 'POST'])
def reset(uid, token):
    user = User.get_logged_in()
    if user is not None: return redirect(url_for('routes.home'))
    page_title = 'Reset Password'
    user = User.query.filter_by(id=uid).first()
    if user is None: return redirect(url_for('routes.home'))
    if user.token != token:
        flash(
            'This reset email is invalid. Please check your inbox for a newer email.',
            'danger'
        )
    form = ResetForm()
    if form.validate_on_submit():
        user.set_pwd(form.password.data)
        flash('Successfully reset password.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/reset.html', form=form, title=page_title)

""" Confirm a token from an email. """
@bp.route('/confirm/<uid>/<token>')
def confirm(uid, token):
    if User.get_logged_in(): return redirect(url_for('routes.home'))
    user = User.query.filter_by(id=uid).first()
    if user is None: return redirect(url_for('routes.home'))
    if user.confirm(token):
        flash('Account successfully confirmed.', 'success')
    return redirect(url_for('routes.home'))

""" Log out. """
@bp.route('/logout')
def logout():
    user = User.get_logged_in()
    if user is not None: user.logout()
    return redirect(url_for('routes.home'))

""" Decorator for login required. """
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if User.get_logged_in() is None:
            flash('Restricted content. Please login to view this page.', 'danger')
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view

""" Decorator for login required for api. """
def login_required_api(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if User.get_logged_in() is None:
            return jsonify({'status': 'failure'})

        return view(**kwargs)
    return wrapped_view

""" Send an email. """
def send_email(recipients, subject='', text='', html=''):
    # Don't send emails if in test environment.
    if current_app.config[DB_URI] == TEST_DB_URI: return

    import boto3
    ses = boto3.client('ses', region_name=AWS_REGION)
    sender = 'info@rateourcourses.com'

    ses.send_email(
        Source=sender,
        Destination={'ToAddresses': recipients},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Text': {'Data': text},
                'Html': {'Data': html}
            }
        }
    )

