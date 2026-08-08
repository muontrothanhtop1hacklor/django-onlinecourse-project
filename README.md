# Django Online Course Application

Final project — IBM Django Application Development with SQL and Databases (Week 5 assignment).

A Django web app for an online course platform: courses, lessons, instructors, learners, enrollment, and a multiple-choice exam system with automatic grading.

## Features

- Course catalog with course detail pages (name + lessons, Bootstrap styling)
- User registration / login / logout
- Course enrollment
- Exam system: learners answer multiple-choice questions, submit, and get an auto-graded result
- Django admin site configured with inlines for Lessons, Questions, and Choices

## Project structure

```
onlinecourse/
├── models.py       # Course, Lesson, Instructor, Learner, Enrollment, Question, Choice, Submission
├── admin.py        # Admin site registration + inlines
├── views.py         # submit() and show_exam_result() views (+ standard course/enroll views)
├── urls.py           # URL routing, including submit/ and result/ paths
└── templates/onlinecourse/
    └── course_details_bootstrap.html
```

## Key models

- **Question** — belongs to a Course, has content + grade, and an `is_get_score()` helper to check if all correct choices were selected.
- **Choice** — belongs to a Question, has content + `is_correct` flag.
- **Submission** — links an Enrollment to the set of Choices the learner selected.

## Exam flow

1. Learner opens a course detail page and clicks **Start Exam**.
2. Selected choices are POSTed to `submit(request, course_id)`, which creates a `Submission` tied to the learner's `Enrollment`.
3. `show_exam_result(request, course_id, submission_id)` totals the grade of all correctly selected choices and renders the result page.

## Setup

```bash
git clone <this-repo-url>
cd django-onlinecourse-project
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Screenshots

- `03-admin-site.png` — Django admin site showing Authentication/Authorization and OnlineCourse sections
- `07-final.png` — Mock exam result page showing a passing score
