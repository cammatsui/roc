import sys

sys.path.append('..')

import json
from roc.models import *
from roc import db, create_app

# Data should come from scraping script, and will need to be cleaned up.
INPUT_PATH = 'data/courses.json' 

# Format is <course_name>: <course_model> to make sure we don't add cross-listed
# courses multiple times.

def init_app_ctx():
    app = create_app()
    app.app_context().push()

def delete_all():
    User.__table__.drop()
    Review.__table__.drop()
    Section.__table__.drop()
    Course.__table__.drop()
    Department.__table__.drop()
    Professor.__table__.drop()

def main():
    init_app_ctx()
    delete_all()
    db.session.drop_all()
    db.session.commit()
    db.create_all()
    run()

def run():
    with open(INPUT_PATH) as read_file:
        courses = {}
        profs = {}
        data = json.loads(read_file.read())
        for dept in data:
            print(f"Adding dept {dept['dept_name']}")
            dept_model = Department(name=dept['dept_name'], code=dept['dept_code'])
            db.session.add(dept_model)

            for course in dept['courses']:
                if course['course_name'] in courses.keys(): 
                    # We've already seen and inserted this course, thus it's cross-listed. 
                    # Just add department relationship.
                    dept_model.courses.append(courses[course['course_name']])
                    continue
                print(f"    Adding course {course['course_name']}")

                course_model = Course(name=course['course_name'], code=course['course_code'])
                dept_model.courses.append(course_model)
                db.session.add(course_model)
                # Don't remove this commit here. For some reason if we don't commit, all of the
                # created courses have None ids.
                db.session.commit()

                # Construct sections.
                for term in course['terms']:
                    for section in term['sections']:
                        section_model = Section(
                            section_number=section['section_number'],
                            term_code=term['term_code'],
                            course_id=course_model.id,
                        )

                        for prof_name in section['section_professors']:
                            prof_model = profs.get(prof_name, Professor(name=prof_name))
                            prof_model.sections.append(section_model)
                            if dept_model not in prof_model.departments:
                                prof_model.departments.append(dept_model)
                            profs[prof_name] = prof_model

                            db.session.add(prof_model)

                        db.session.add(section_model)

                courses[course['course_name']] = course_model
                db.session.add(course_model)

            db.session.add(dept_model)
            db.session.commit()

if __name__ == '__main__':
    main()
