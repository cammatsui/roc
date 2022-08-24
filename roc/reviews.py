from flask import render_template, Blueprint, redirect, url_for, flash, request

from roc.models import User, Department, Review, Course, Professor
from roc.forms import ReviewForm
from roc.auth import login_required

bp = Blueprint('reviews', __name__, url_prefix='/reviews')


""" List departments. Can click on courses or professors from each department. """
@bp.route('/departments')
@login_required
def departments():
    page_title = 'Departments'
    depts = Department.get_all()
    user = User.get_logged_in()
    return render_template('reviews/departments.html', user=user, departments=depts, title=page_title)

""" List courses in a department. """
@bp.route('/courses/<department_id>')
@login_required
def courses(department_id):
    dept = Department.query.filter_by(id=department_id).first()
    if dept is None: return redirect(url_for('home'))
    page_title = f'{dept.name} Courses'
    user = User.get_logged_in()
    return render_template('reviews/department_courses.html', user=user, department=dept, title=page_title)

""" List professors in a department. """
@bp.route('/profs/<department_id>')
@login_required
def professors(department_id):
    dept = Department.query.filter_by(id=department_id).first()
    if dept is None: return redirect(url_for('home'))
    page_title = f'{dept.name} Professors'
    user = User.get_logged_in()
    return render_template('reviews/department_profs.html', user=user, department=dept, title=page_title)

""" List a professor's reviews. """
@bp.route('/prof/<prof_id>')
@login_required
def professor_reviews(prof_id):
    prof = Professor.query.filter_by(id=prof_id).first()
    if prof is None: return redirect(url_for('home'))
    page_title = f'Reviews for Professor {prof.name}'
    user = User.get_logged_in()
    return render_template('reviews/prof_reviews.html', user=user, professor=prof, title=page_title)

""" List a course's reviews. """
@bp.route('/course/<course_id>')
@login_required
def course_reviews(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None: return redirect(url_for('home'))
    page_title = f'Reviews for {course.name}'
    user = User.get_logged_in()
    return render_template('reviews/course_reviews.html', user=user, course=course, title=page_title)

""" User reviews page. """
@bp.route('/my-reviews')
@login_required
def user_reviews():
    user = User.get_logged_in()
    page_title = 'My Reviews'
    return render_template('reviews/user_reviews.html', user=user, title=page_title)

""" Add a review. """
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_review():
    user = User.get_logged_in()
    if user is None: return redirect(url_for('auth.login'))
    page_title = 'Add Review'
    form = ReviewForm()
    if form.validate_on_submit and request.method == 'POST' :
        if user.has_reviewed_course(form.course.data):
            flash('You have already reviewed this course.', 'danger')
        else:
            grade = None if form.grade.data == '' else form.grade.data
            Review.add_review(
                form.section.data,
                form.professor_rating.data,
                form.difficulty_rating.data,
                form.workload_rating.data,
                form.interesting_rating.data,
                form.text.data,
                user,
                grade
            )
            flash(f'Successfully added review.', 'success')
    return render_template('reviews/add_review.html', user=user, form=form, title=page_title)
