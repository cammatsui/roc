# RoC Data Model

## Relationships
- Users and reviews: reviews have one author and a user can author many reviews.
- Reviews and sections: reviews are for a specific section, so each review has a section and each
  section has many reviews.
- Courses and sections: sections are instances of a course, so each section has a course and each
  course has many sections.
- Courses and departments: courses can be cross-listed across multiple departments, so there is a
  many-to-many relationship between courses and departments.
- Departments and professors: professors can teach courses in multiple departments, so there is a
  many-to-many relationship between departments and professors.
- Sections and professors: there is a many-to-many relationship between sections and professors.


## Models
- `User`
    - `id`: primary key.
    - `email`: must be YY@amherst.edu student email.
    - `pwd_salt`: randomly generated salt for that user.
    - `pwd_hash`: hash of password appended to salt.
    - `date_registered`: datetime registered.  
    - `confirm_token`: confirmation token.
    - `is_confirmed`: whether or not the user has done email confirmation.
- `Review`
    - `id`: primary key.
    - `date_published`: datetime published.
    - `text`: the text of the review itself.
    - `author_id`: the user id of the author of this review.
    - `section_id`: the id of the section this review is for.
- `Section`
    - `id`: primary key.
    - `section_number`: section number, e.g. the "01" in "MATH-121-01".
    - `term_code`: the section's term (an enum).
    - `course_id`: id of this section's course.
- `Course`
    - `id`: primary key.
    - `name`: string, course name.
- `Department`
    - `id`: primary key.
    - `name`: string, department name.
    - `code`: string, 4-character department code, e.g., "MATH".
- `Professor`:
    - `id`: primary key.
    - `name`: the professor's name.

## Association Tables
- `user_review_likes`: records which users like which reviews.
- `section_professor`: records which professors teach which sections.
- `professor_department`: records which professors work in which departments.
- `course_department`: records which courses are taught in which departments.
