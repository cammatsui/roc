import datetime
from datetime import timedelta

from roc.models import User, Department, Course, Review, Professor
from flask import Blueprint, url_for, redirect, jsonify
from roc.auth import login_required_api

bp = Blueprint('api', __name__, url_prefix='/api')


""" All departments. """
@bp.route('/get-departments')
@login_required_api
def get_departments():
    user = User.get_logged_in()
    if user is None: return redirect(url_for('home'))
    depts = [{'id': dept.id, 'name': dept.name} for dept in Department.get_all()]
    return jsonify({'depts': depts})

""" Get courses for department id. """
@bp.route('/get-courses/<dept_id>')
@login_required_api
def get_courses_for_dept_id(dept_id):
    user = User.get_logged_in()
    if user is None: return redirect(url_for('home'))
    dept = Department.query.filter_by(id=dept_id).first()
    courses = [{'id': course.id, 'name': course.name} for course in dept.courses]

    return jsonify({'courses': courses})

""" Get courses for department id. """
@bp.route('/get-terms/<course_id>')
@login_required_api
def get_terms_for_course(course_id):
    user = User.get_logged_in()
    if user is None: return redirect(url_for('home'))
    course = Course.query.filter_by(id=course_id).first()
    terms = list({sect.term_code for sect in course.sections})

    return jsonify({'terms': terms})

""" Get sections for a course id. """
@bp.route('/get-sections/<course_id>/<term_code>')
@login_required_api
def get_sections_for_course_and_term(course_id, term_code):
    user = User.get_logged_in()
    if user is None: return redirect(url_for('home'))
    course = Course.query.filter_by(id=course_id).first()
    sections = []
    for section in list(filter(lambda sect: sect.term_code == term_code, course.sections)):
        prof_names = ', '.join([prof.name for prof in section.professors])
        sectionObj = {
            'id': section.id,
            'desc': f'{section.section_number}: {prof_names}'
        }
        sections.append(sectionObj)

    return jsonify({'sections': sections})

""" Toggle whether the loggedin user has liked this review. """
@bp.route('/like-toggle/<review_id>')
@login_required_api
def toggle_like_for_review(review_id):
    user = User.get_logged_in()
    if user is None: return jsonify({'status': 'failure'})
    try:
        review = Review.query.filter_by(id=review_id).first()
        review.toggle_user_like(user)
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'failure'})

""" Delete the given review. """
@bp.route('/delete-review/<review_id>')
@login_required_api
def delete_review(review_id):
    user = User.get_logged_in()
    if user is None: return jsonify({'status': 'failure'})
    try:
        review = Review.query.filter_by(id=review_id).first()
        if review.author_id == user.id:
            Review.delete_review(review)
            return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'failure'})

""" Return search results for a query. Searches professor and course names. """
SEARCH_LIMIT = 3
@bp.route('/search/<query>')
def search_query(query):
    try:
        query = f'%{query}%'
        results = []
        courses = Course.query.filter(Course.name.like(query)).limit(SEARCH_LIMIT).all()

        results += [{'name': c.name, 'id': c.id, 'type': 'course', 'reviews': len(c.reviews)} 
            for c in courses]

        profs = Professor.query.filter(Professor.name.like(query)).limit(SEARCH_LIMIT).all()
        results += [{'name': p.name, 'id': p.id, 'type': 'prof', 'reviews': len(p.reviews)}
            for p in profs]
        return jsonify({'status': 'success', 'results': results})
    except:
        return jsonify({'status': 'failure'})

""" Return line chart data for admin page. """
@bp.route('/get-admin-chart-data')
@login_required_api
def get_admin_chart_data():
    user = User.get_logged_in()
    if user is None or not user.is_admin: return jsonify({'status': 'failure'})
    thirty_days_ago = datetime.datetime.today() - timedelta(days=30)
    return jsonify({
        'status': 'success',
        'data': "",
    })
