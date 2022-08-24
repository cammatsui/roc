import sys
sys.path.append('..')

import math
import pandas as pd
from datetime import datetime

import add_courses
from roc.models import User, Course, Section, Review, REVIEW_MAX_LENGTH
from roc.forms import GRADES
from roc import db, create_app

USERS_INPUT_PATH = 'data/users.csv'
REVIEWS_INPUT_PATH = 'data/evaluations.csv'
COURSES_INPUT_PATH = 'data/courses.csv'
ADMIN_EMAILS = []
user_new_ids = {};


def init_app_ctx():
    app = create_app()
    app.app_context().push()

def add_users():
    users_df = pd.read_csv(USERS_INPUT_PATH)
    for _, user in users_df.iterrows():
        is_admin = user['email'] in ADMIN_EMAILS
        mig_user = User(
            email=user['email'],
            pwd_hash_deprecated=user['password'],
            date_registered=datetime.fromtimestamp(user['time_added']),
            confirmed=True,
            token=User._get_token(),
            is_admin=is_admin,
        )
        db.session.add(mig_user)
        db.session.commit()
        user_new_ids[user['id']] = mig_user.id
    print(user_new_ids)

def add_reviews():
    reviews_df = pd.read_csv(REVIEWS_INPUT_PATH)
    courses_df = pd.read_csv(COURSES_INPUT_PATH)
    for _, review in reviews_df.iterrows():
        # Find new course id for this review.
        # Get course name by mapping this review's course_id to courses_df.id.
        # Then format that row's id to fit, and query new DB courses by name.
        # Finally, get course id from resulting row.
        course_rows_depr = courses_df.loc[courses_df['id'] == review['course_id']]
        course_name_depr = course_rows_depr.iloc[0]['name_number'].split('-')[1].strip()
        search = "%{}%".format(course_name_depr)
        try:
            new_course = Course.query.filter(Course.name.like(search)).all()[0]
        except:
            #print(f"No courses in new db with name {course_name_depr}")
            continue

        new_course_id = new_course.id

        # Find section id for this review.
        term_code = format_old_semester(review['semester'])
        matching_sections = Section.query.filter(
            Section.course_id==new_course_id,
            Section.term_code==term_code,
        )
        review_section = None
        for section in matching_sections:
            if review['prof_name'].strip() in [prof.name for prof in section.professors]:
                review_section = section
        if review_section is None:
            print(f"No sections with prof {review['prof_name']} / term {term_code} for course {course_name_depr}")
            continue

        # Find author id.
        new_author_id = user_new_ids.get(review['user_id'])
        if new_author_id is None:
            print(f"No author id for this review, old was {review['user_id']}")
            continue

        # Check if grade.
        grade = review['grade'] if review['grade'] in GRADES else None
        text = review['comment']
        if not type(text) is str:
            text = ""
        if len(text) > REVIEW_MAX_LENGTH: continue


        new_review = Review(
            date_published=datetime.fromtimestamp(review['time_added']),
            text=text,
            professor_rating=max(1, math.floor(review['prof_rating'])),
            difficulty_rating=max(1, math.floor(review['difficulty'])),
            workload_rating=max(1, math.floor(review['workload'])),
            interesting_rating=max(1, math.floor(review['interesting'])),
            grade=grade,
            author_id=new_author_id,
            section_id=review_section.id,
        )

        db.session.add(new_review)
        db.session.commit()

def format_old_semester(old_sem_tag):
    year = old_sem_tag[-2:]
    term_char = old_sem_tag[0]
    return term_char + year


def main():
    init_app_ctx()
    db.create_all()
    add_courses.run()
    add_users()
    add_reviews()

if __name__ == '__main__':
    main()
