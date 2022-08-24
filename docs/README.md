# Rate Our Courses

## Intro
Rate Our Courses (roc) is a site which allows Amherst College students (users) to write reviews for
Amherst courses and professors. Users can view reviews by course (sorted by department) and by 
professor (also sorted by department). Users can add reviews for course sections and like other 
users' reviews. Users can also delete their own reviews.


## Pages
- `/`: home.
- `/user`: user-related pages. 
    - `/login`: the login page.
    - `/register`: the register page.
    - `/logout`: the logout page.
    - `/verify_account`: link for email verification.
    - `/view`: displays account info, and links to `/view/user`.
- `/view`: pages to view departments, professors, courses, sections, and reviews. all urls redirect
  home if the user is not logged in. all pages also allow the user to sort by various factors.
    - `/departments`: list departments. from each department, the user can navigate to reviews for 
      that department's professors or courses.
    - `/courses`: list a department's courses. also indicates which courses have reviews.
    - `/professors`: list a departments's professors. also indicates which professors have reviews.
    - `/course`: list a course's reviews.
    - `/professor`: list a professor's reviews.
    - `/user`: view the logged-in user's reviews.
    - `/search`: displays courses and professors matching the given search term.
- `/add`: add a review.
