import pytest
import sys

sys.path.append('..')

from roc import db
from roc.models import Department, Course, Section, Professor, User, Review
from scripts import testdb_init
from roc import create_app


""" Setup the test database with mock data. """
@pytest.fixture
def setup_db(request):

    testdb_init.run()

    def teardown_db():
        db.session.query(User).delete()
        db.session.query(Department).delete()
        db.session.query(Professor).delete()
        db.session.query(Course).delete()
        db.session.query(Section).delete()
        db.session.query(Review).delete()
        db.session.commit()

    request.addfinalizer(teardown_db)
    
def test_get_reviews_from_courses(setup_db):
    # Get departments
    depts = Department.get_all()
    math_dept = Department.query.filter_by(code="MATH").first()
    stat_dept = Department.query.filter_by(code="STAT").first()
    assert(contains_model_once(depts, math_dept))
    assert(contains_model_once(depts, stat_dept))

    # Get courses
    intro_stat = Course.query.filter_by(name="Introduction to Statistics With Modeling").first()
    groups = Course.query.filter_by(name="Groups, Rings and Fields").first()
    inter_stat = Course.query.filter_by(name="Intermediate Statistics").first()
    assert(contains_model_once(math_dept.courses, intro_stat))
    assert(contains_model_once(math_dept.courses, groups))
    assert(contains_model_once(stat_dept.courses, intro_stat))
    assert(contains_model_once(stat_dept.courses, inter_stat))

    # Assert course sections
    assert(len(intro_stat.sections) == 2)
    assert(len(groups.sections) == 2)
    assert(len(inter_stat.sections) == 2)
    assert(unique_ids(intro_stat.sections))
    assert(unique_ids(groups.sections))
    assert(unique_ids(inter_stat.sections))

    # Assert reviews
    reviews = [Review.query.filter_by(text=f'review {i}').first() for i in range(1,6)]
    assert(contains_model_once(intro_stat.reviews, reviews[0]))
    assert(contains_model_once(intro_stat.reviews, reviews[1]))
    assert(unique_ids(intro_stat.reviews))

    assert(contains_model_once(groups.reviews, reviews[2]))
    assert(contains_model_once(groups.reviews, reviews[3]))
    assert(unique_ids(groups.reviews))

    assert(contains_model_once(inter_stat.reviews, reviews[4]))
    assert(unique_ids(inter_stat.reviews))

def test_get_reviews_from_professors(setup_db):
    # Get departments
    depts = Department.get_all()
    math_dept = Department.query.filter_by(code="MATH").first()
    stat_dept = Department.query.filter_by(code="STAT").first()
    assert(contains_model_once(depts, math_dept))
    assert(contains_model_once(depts, stat_dept))

    # Get professors
    donges = Professor.query.filter_by(name="Kevin Donges").first()
    elliott = Professor.query.filter_by(name="Chris Elliott").first()
    daniels = Professor.query.filter_by(name="Harris Daniels").first()
    assert(contains_model_once(math_dept.professors, elliott))
    assert(contains_model_once(math_dept.professors, daniels))
    assert(contains_model_once(stat_dept.professors, elliott))
    assert(contains_model_once(stat_dept.professors, donges))

    # Assert professor sections
    assert(len(donges.sections) == 3)
    assert(len(elliott.sections) == 3)
    assert(len(daniels.sections) == 1)
    assert(unique_ids(donges.sections))
    assert(unique_ids(elliott.sections))
    assert(unique_ids(daniels.sections))

    # Assert reviews
    reviews = [Review.query.filter_by(text=f'review {i}').first() for i in range(1,6)]
    assert(contains_model_once(donges.reviews, reviews[0]))
    assert(contains_model_once(donges.reviews, reviews[1]))
    assert(contains_model_once(donges.reviews, reviews[4]))
    assert(unique_ids(donges.reviews))

    assert(contains_model_once(elliott.reviews, reviews[0]))
    assert(contains_model_once(elliott.reviews, reviews[2]))
    assert(unique_ids(elliott.reviews))

def contains_model_once(model_lst, model):
    return len(list(filter(lambda mod: mod.id == model.id, model_lst))) == 1

def unique_ids(model_lst):
    return len({model.id for model in model_lst}) == len(model_lst)

