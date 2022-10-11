from ast import Delete
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate, user_logged_in
from django.db import IntegrityError
from django.urls import reverse
from .forms import TaskForm, UserForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # Register user
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'], email=request.POST['email'])
                user.first_name = request.POST['first name']
                user.last_name = request.POST['last name']
                user.save()
                login(request, user)
                return redirect('tasks')
            except ValueError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Please fill the cells'
                })
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exist'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        })

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datacompleted__isnull=True)

    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datacompleted__isnull=False).order_by('-datacompleted')

    return render(request, 'tasks_completed.html', {
        'tasks': tasks,
    })

@login_required
def create_task(request):

    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
            'form': TaskForm,
            'error': 'Please provide valid data'
        })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error':'Error updating task'})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datacompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == "GET":
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })

        else:
            login(request, user)
            return redirect('tasks')

def profile(request, id):
    user = get_object_or_404(User, pk=id)
    user.last_login = timezone.now()
    return render(request, 'profile.html', {'user':user})

def profile_detail(request, id):
    if request.method == 'GET':
        userC = get_object_or_404(User, pk=id)
        form = UserForm(instance=userC)
        return render(request, 'profile_detail.html', {'user':userC, 'form':form})
    else:
        try:
            userC = get_object_or_404(User, pk=id)
            form = UserForm(request.POST, instance=userC)
            form.save()
            return redirect('profile', id=request.user.id)
        except ValueError:
            return render(request, 'profile_detail.html', {'user':userC, 'form':form, 'error':'Error updating your profile'})