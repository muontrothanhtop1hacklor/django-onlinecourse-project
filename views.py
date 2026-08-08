from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
import logging

from .models import Course, Enrollment, Question, Choice, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except User.DoesNotExist:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name,
                                              last_name=last_name, password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# <HINT> Create a submit view to create an exam submission record for a course enrollment,
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission_id = submission.id
    return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result', args=(course_id, submission_id,)))


# <HINT> A example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers


# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choices = submission.choices.all()
    total_score = 0
    for choice in choices:
        if choice.is_correct:
            total_score += choice.question.grade
    context['course'] = course
    context['grade'] = total_score
    context['choices'] = choices
    context['submission'] = submission

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
