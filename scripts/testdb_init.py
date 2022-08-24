import sys

sys.path.append('..')

from roc import db
from roc.models import Department, Course, Section, Professor, User, Review
from roc import create_app

""" Add a list of models to the database. """
def add_to_db(models):
    for model in models:
        db.session.add(model)
    db.session.commit()

""" Setup the test database. """
def run():
    app = create_app()
    app.app_context().push()
    
    # Create the test database.
    db.create_all()

    # Create departments.
    math_dept = Department(name="Mathematics", code="MATH")
    stat_dept = Department(name="Statistics", code="STAT")

    departments = [math_dept, stat_dept]
    add_to_db(departments)
    
    # Create courses.
    intro_stat = Course(name="Introduction to Statistics With Modeling", code="135")
    groups = Course(name="Groups, Rings and Fields", code="350")
    intermediate_stat = Course(name="Intermediate Statistics", code="220")

    courses = [intro_stat, groups, intermediate_stat]
    add_to_db(courses)

    # Add courses to departments.
    math_dept.courses += [intro_stat, groups]
    stat_dept.courses += [intro_stat, intermediate_stat]

    # Create sections.
    FALL22 = 'F22'
    intro_stat_1 = Section(section_number=1,  term_code=FALL22, course_id=intro_stat.id)
    intro_stat_2 = Section(section_number=2,  term_code=FALL22, course_id=intro_stat.id)
    groups_1 = Section(section_number=1, term_code=FALL22, course_id=groups.id)
    groups_2 = Section(section_number=2, term_code=FALL22, course_id=groups.id)
    inter_stat_1 = Section(section_number=1,  term_code=FALL22, course_id=intermediate_stat.id)
    inter_stat_2 = Section(section_number=2,  term_code=FALL22, course_id=intermediate_stat.id)

    sections = [intro_stat_1, intro_stat_2, groups_1, groups_2, inter_stat_1, inter_stat_2]
    add_to_db(sections)

    # Create professors.
    elliott = Professor(name="Chris Elliott")
    donges = Professor(name="Kevin Donges")
    daniels = Professor(name="Harris Daniels")

    professors = [elliott, donges, daniels]
    add_to_db(professors)

    # Add professors to departments.
    elliott.departments += [math_dept, stat_dept]
    donges.departments += [stat_dept]
    daniels.departments += [math_dept]

    # Add professors to sections.
    intro_stat_1.professors += [elliott, donges]
    intro_stat_2.professors += [donges]
    groups_1.professors += [elliott]
    groups_2.professors += [daniels]
    inter_stat_1.professors += [donges]
    inter_stat_2.professors += [elliott]

    # Add some users.
    user1 = User.register('user23@amherst.edu', "password1")
    user2 = User.register('user22@amherst.edu', "password2")
    user3 = User.register('user24@amherst.edu', "password3")
    assert(user1 is not None)
    assert(user2 is not None)
    assert(user3 is not None)

    # Add reviews for some sections.
    review1 = Review(
        text="review 1",
        professor_rating=3,
        difficulty_rating=5,
        workload_rating=3,
        interesting_rating=1,
        author_id=user1.id,
        section_id=intro_stat_1.id
    )
    review2 = Review(
        text="review 2",
        professor_rating=5,
        difficulty_rating=4,
        workload_rating=3,
        interesting_rating=2,
        author_id=user3.id,
        section_id=intro_stat_2.id
    )
    review3 = Review(
        text="review 3",
        professor_rating=1,
        difficulty_rating=3,
        workload_rating=5,
        interesting_rating=2,
        author_id=user2.id,
        section_id=groups_1.id
    )
    review4 = Review(
        text="review 4",
        professor_rating=2,
        difficulty_rating=4,
        workload_rating=3,
        interesting_rating=2,
        author_id=user3.id,
        section_id=groups_1.id
    )
    review5 = Review(
        text="review 5",
        professor_rating=4,
        difficulty_rating=5,
        workload_rating=3,
        interesting_rating=4,
        author_id=user2.id,
        section_id=inter_stat_1.id
    )

    # Add likers.
    reviews = [review1, review2, review3, review4, review5]
    add_to_db(reviews)

    review1.likers += [user1, user2]
    review3.likers += [user1, user3]

if __name__ == '__main__':
    run()
