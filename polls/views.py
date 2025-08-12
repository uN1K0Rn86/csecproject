from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
import re

from .models import Question, Choice, VUser


def index(request):
    # Django authetication on next line:
    # if not request.user.is_authenticated:
    if not request.session.get('vuser_id'):
        return redirect('polls:login')
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list, 'admin': request.COOKIES.get('is_admin') == 'true'}
    return render(request, 'polls/index.html', context)

def add_poll(request):
    if request.method == "POST":
        question_text = request.POST.get('question_text')
        choices_text = request.POST.get('choices_text')
        if question_text and choices_text:
            question = Question.objects.create(question_text=question_text, pub_date=datetime.now())
            choices = [c.strip() for c in choices_text.split(',') if c.strip()]
            for choice_text in choices:
                Choice.objects.create(question=question, choice_text=choice_text, votes=0)
            return HttpResponseRedirect(reverse('polls:index'))
        else:
            error_message = "Please provide both a question and choices."
            return render(request, 'polls/add_poll.html', {'error_message': error_message})
    return HttpResponseRedirect(reverse('polls:index'))

def delete(request, question_id):
    if request.method == "POST":
        question = get_object_or_404(Question, pk=question_id)
        question.delete()
        return redirect('polls:index')

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

@csrf_exempt
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    
def search(request):
    results = []
    if request.method == "POST":
        search_text = request.POST.get('search')
        # SQL injection vulnerability: unsanitized user input in raw SQL
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT id, question_text, pub_date FROM polls_question WHERE question_text LIKE '%{search_text}%'")
            rows = cursor.fetchall()
        for row in rows:
            results.append(Question(id=row[0], question_text=row[1], pub_date=row[2]))

        # Safe Django ORM query on the next line
        # results = Question.objects.filter(question_text__icontains=search_text)

    return render(request, 'polls/search.html', {'results': results})

def register(request):
    # Password validation:
    # def is_strong_password(password):
    #     return (
    #         re.search(r"\d", password) and
    #         re.search(r"[^\w\s]", password)
    #     )

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            # Django authetication on next line:
            # if User.objects.filter(username=username).exists():
            if VUser.objects.filter(username=username).exists():
                return render(request, "polls/register.html", {"error": "Username already exists."})
            # user = User.objects.create_user(username=username, password=password)

            # Password validation:
            # if len(password) < 8:
            #     return render(request, "polls/register.html", {"error": "Password must be at least 8 characters."})
            # if not is_strong_password(password):
            #     return render(request, "polls/register.html", {"error": "Please make sure the password contains at least 1 number and 1 special character."})
            user = VUser.objects.create(username=username, password=password)
            return redirect("polls:login")
        else:
            return render(request, "polls/register.html", {"error": "Please provide both username and password."})
    return render(request, "polls/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # Django authetication
        # user = authenticate(request, username=username, password=password)
        # if user is not None:
        #     auth_login(request, user)
        #     return redirect("polls:index")
        # else:
        #     return render(request, "polls/login.html", {"error": "Invalid credentials."})
        try:
            user = VUser.objects.get(username=username, password=password)
            response = redirect("polls:index")
            response.set_cookie('is_admin', 'true' if username == 'admin' else 'false')
            request.session['vuser_id'] = user.id
            return response
        except VUser.DoesNotExist:
            return render(request, "polls/login.html", {"error": "Invalid credentials."})
    return render(request, "polls/login.html")

def logout_view(request):
    # Django authetication
    # auth_logout(request)
    request.session.flush()
    return redirect('polls:login')