from __future__ import annotations
import secrets
import string
from flask import session, flash
from datetime import datetime
from hashlib import sha256

from roc import db

RAND_CHAR_CHOICES = string.ascii_letters + string.digits


# ASSOCIATION TABLES
user_review_likes = db.Table(
    'user_review_likes',
    db.Column('user_id', db.ForeignKey('user.id'), primary_key=True),
    db.Column('review_id', db.ForeignKey('review.id'), primary_key=True),
)

section_professor = db.Table(
    'section_professor',
    db.Column('section_id', db.ForeignKey('section.id'), primary_key=True),
    db.Column('professor_id', db.ForeignKey('professor.id'), primary_key=True),
)

professor_department = db.Table(
    'professor_department',
    db.Column('professor_id', db.ForeignKey('professor.id'), primary_key=True),
    db.Column('department_id', db.ForeignKey('department.id'), primary_key=True),
)

course_department = db.Table(
    'course_department',
    db.Column('course_id', db.ForeignKey('course.id'), primary_key=True),
    db.Column('department_id', db.ForeignKey('department.id'), primary_key=True),
)


# MODEL TABLES
PWD_SALT_LENGTH = 8
TOKEN_LENGTH = 64
VALID_YEARS = {f'{i}' for i in range(10, 30)}
AMHERST_EMAIL = "@amherst.edu"
""" Model for a User. """
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd_salt = db.Column(db.String(8))
    pwd_hash = db.Column(db.String(64))
    pwd_hash_deprecated = db.Column(db.String(64))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(TOKEN_LENGTH), nullable=False)
    confirmed = db.Column(db.Boolean(), default=False)
    is_admin = db.Column(db.Boolean(), nullable=False, default=False)

    reviews = db.relationship('Review', backref='author', lazy=True)
    liked_reviews = db.relationship(
        'Review',
        secondary=user_review_likes,
        back_populates='likers'
    )
    

    """ Register a user and return the User, or None if not an Amherst student email. """
    @staticmethod
    def register(email: str, pwd: str, is_admin=False):
        if not User._verify_amherst_email(email): return None
        salt = User._get_salt()
        token = User._get_token()
        pwd_hash = User._get_hashed_pwd(pwd, salt)
        user = User(
            email=email,
            pwd_salt=salt,
            pwd_hash=pwd_hash,
            token=token,
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        return user

    """ Verify that the given email is an Amherst student email. """
    @staticmethod
    def _verify_amherst_email(email: str) -> bool:
        if len(email) < len(AMHERST_EMAIL)+3:
            return False
        return email[-12:] == AMHERST_EMAIL and email[-14:-12] in VALID_YEARS 

    """ Get the currently logged-in user. """
    @staticmethod
    def get_logged_in():
        user_id = session.get('user_id')
        if user_id is None: return None
        return User.query.filter_by(id=user_id).first()
    
    """ Login a user. """
    @staticmethod
    def login(email: str, pwd: str):
        user = User.query.filter_by(email=email).first()
        if user is None: return None
        print(f"Logging in {email}")
        # Check if user is not yet migrated.
        if user.pwd_hash_deprecated:
            if sha256(pwd.encode('utf-8')).hexdigest() != user.pwd_hash_deprecated:
                return None
            # Migrate to salted password.

            user.pwd_salt = User._get_salt()
            user.token = User._get_token()
            user.pwd_hash = User._get_hashed_pwd(pwd, user.pwd_salt)
            user.pwd_hash_deprecated = None
            db.session.commit()

        if user is None: return None
        hashed_pwd = User._get_hashed_pwd(pwd, user.pwd_salt)
        if (user.pwd_hash == hashed_pwd):
            session['user_id'] = user.id
            return User
        return None

    """ Logout the current user. """
    @staticmethod
    def logout():
        if session.get('user_id') is not None:
            session.pop('user_id')

    """ Generate a confirmation token. """
    @staticmethod
    def _get_token() -> str:
        return ''.join(secrets.choice(RAND_CHAR_CHOICES) for _ in range(TOKEN_LENGTH))

    """ Generate a salt for a password hash. """
    @staticmethod
    def _get_salt() -> str:
        return ''.join(secrets.choice(RAND_CHAR_CHOICES) for _ in range(PWD_SALT_LENGTH))

    """ Get the password hash given a password and a salt. """
    @staticmethod
    def _get_hashed_pwd(pwd: str, salt: str) -> str:
        to_hash = pwd + salt
        return sha256(to_hash.encode('utf-8')).hexdigest()

    """ Get formatted date registered. """
    @property
    def registered(self):
        return self.date_registered.strftime('%m/%d/%y')

    """ Reset this user's token. """
    def reset_token(self):
        self.token = User._get_token()
        db.session.commit()

    """ Set this user's password. """
    def set_pwd(self, new_pwd):
        self.pwd_hash = User._get_hashed_pwd(new_pwd, self.pwd_salt) 
        db.session.commit()

    """ Try to confirm the user with the given token and return whether successful. """
    def confirm(self, token):
        if self.token == token:
            self.confirmed = True           
            db.session.commit()
            return True
        return False

    """ Get whether a user has already reviewed a course. """
    def has_reviewed_course(self, course_id):
        return int(course_id) in [review.course_id for review in self.reviews]



REVIEW_MAX_LENGTH = 2000
""" Model for a Review. """
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_published = db.Column(db.DateTime, default=datetime.utcnow)
    text = db.Column(db.String(REVIEW_MAX_LENGTH), nullable=False, default="")
    professor_rating = db.Column(db.Integer(), nullable=False)
    difficulty_rating = db.Column(db.Integer(), nullable=False)
    workload_rating = db.Column(db.Integer(), nullable=False)
    interesting_rating = db.Column(db.Integer(), nullable=False)
    grade = db.Column(db.String(2))

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    likers = db.relationship(
        'User',
        secondary=user_review_likes,
        back_populates='liked_reviews'
    )


    """ Add a review to the database. """
    @staticmethod
    def add_review(
        section_id,
        professor_rating,
        difficulty_rating,
        workload_rating,
        interesting_rating,
        text,
        author,
        grade,
    ):
        review = Review(
            section_id=section_id,
            professor_rating=professor_rating,
            difficulty_rating=difficulty_rating,
            workload_rating=workload_rating,
            interesting_rating=interesting_rating,
            author_id=author.id,
            text=text,
            grade=grade,
        )
        db.session.add(review)
        db.session.commit()

    """ Delete the given review. """
    @staticmethod
    def delete_review(review):
        db.session.delete(review)
        db.session.commit()

    """ Determine whether a given user has liked this review.  """
    def liked_by(self, user: User):
        return len(list(filter(lambda liker: liker.id == user.id, self.likers))) == 1

    """ Toggle a user's like for this review. """
    def toggle_user_like(self, user: User):
        if user is None: return
        if self.liked_by(user):
            self.likers = list(filter(lambda liker: liker.id != user.id, self.likers))
        else:
            self.likers.append(user)
        db.session.commit()

    """ Get the course id for this review. """
    @property
    def course_id(self):
        return self.section.course.id

    """ Get the course for this review. """
    @property
    def course(self):
        return Course.query.filter_by(id=self.course_id).first()

    """ Get the section for this review. """
    @property
    def section(self):
        return Section.query.filter_by(id=self.section_id).first()

    """ Get the professors for the section of this review. """
    @property
    def professors(self):
        return self.section.professors

    """ Get the formatted date published. """
    @property
    def published(self):
        return self.date_published.strftime('%m/%d/%y')
    
    """ Average of the four ratings. """
    @property
    def avg_rating(self):
        return sum([
            self.professor_rating,
            self.difficulty_rating,
            self.interesting_rating,
            self.workload_rating,
        ]) / 4

    """ Number of likes on this review. """
    @property
    def num_likes(self):
        return len(self.likers)


SECTION_NUMBER_LENGTH = 5
""" Model for a course Section. """
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_number = db.Column(db.String(SECTION_NUMBER_LENGTH), nullable=False)
    term_code = db.Column(db.String(4), nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    reviews = db.relationship('Review', backref='section', lazy=True)
    professors = db.relationship(
        'Professor',
        secondary=section_professor,
        back_populates='sections'
    )


    """ Get this section's course. """
    @property
    def course(self):
        return Course.query.filter_by(id=self.course_id).first()


COURSE_NAME_LENGTH = 200
COURSE_CODE_LENGTH = 8
""" Model for a Course. """
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(COURSE_NAME_LENGTH), nullable=False)
    code = db.Column(db.String(COURSE_CODE_LENGTH), nullable=False)

    departments = db.relationship(
        'Department',
        secondary=course_department,
        back_populates='courses',
    )


    """ Get all of the sections for this course. """
    @property
    def sections(self):
        return Section.query.filter_by(course_id=self.id).all()

    """ Get all of the reviews for this course. """
    @property
    def reviews(self):
        reviews = []
        for section in self.sections:
            reviews += section.reviews
        return sorted(reviews, key=lambda review: review.num_likes, reverse=True)

    """ Get the average, average rating for this course. """
    @property
    def avg_rating(self):
        if len(self.reviews) == 0: return 0
        total_rating = sum([review.avg_rating for review in self.reviews])
        return total_rating / len(self.reviews)


DEPARTMENT_NAME_LENGTH = 100
""" Model for a Department. """
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(DEPARTMENT_NAME_LENGTH), nullable=False)
    code = db.Column(db.String(4), nullable=False, unique=True)

    professors = db.relationship(
        'Professor',
        secondary=professor_department,
        back_populates='departments'
    )
    courses = db.relationship(
        'Course',
        secondary=course_department,
        back_populates='departments',
    )


    """ Get all departments. """
    @staticmethod
    def get_all():
        return Department.query.all()

    """ Get professors, sorted by rating. """
    def sorted_professors(self):
        return sorted(self.professors, key=lambda prof: prof.avg_rating, reverse=True)

    """ Get courses, sorted by rating. """
    def sorted_courses(self):
        return sorted(self.courses, key=lambda course: course.avg_rating, reverse=True)


PROFESSOR_NAME_LENGTH = 100
""" Model for a Professor. """
class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(PROFESSOR_NAME_LENGTH), nullable=False)

    sections = db.relationship(
        'Section',
        secondary=section_professor,
        back_populates='professors'
    )
    departments = db.relationship(
        'Department',
        secondary=professor_department,
        back_populates='professors'
    )


    """ Get all reviews for this professor. """
    @property
    def reviews(self):
        reviews = []
        for section in self.sections:
            reviews += section.reviews
        return reviews

    """ Get this professor's average rating across their reviews. """
    @property
    def avg_rating(self):
        if len(self.reviews) == 0: return 0
        total_rating = sum([review.professor_rating for review in self.reviews])
        return total_rating / len(self.reviews)

    """ Equality by ids for professors. """
    def __eq__(self, other):
        if not isinstance(other, Professor): return False
        return self.id == other.id
