from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.contrib.auth.decorators import login_required
from datetime import date
from datetime import datetime

MENU = [{'title': "Добавить соревнование", 'url_name': 'add_competition'},
        {'title': "На главную", 'url_name': 'show_competitions'},
]


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('show_competitions')

    else:
        logout(request)
        form = SignUpForm()
    return render(request, 'AppArena/register.html', {'form': form, 'title': "Регистрация", 'name_btn': 'Зарегистрироваться'})


def user_login(request):
    if request.method == 'POST':
        form = SignInForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('show_competitions')
    else:
        logout(request)
        form = SignInForm()
    return render(request, 'AppArena/login.html', {'form': form, 'title': "Авторизация"})


@login_required
def show_competitions(request):
    competitions = Competition.objects.all()
    page_menu = MENU.copy()
    today = date.today()

    query = request.GET.get('q')
    if query:
        competitions = competitions.filter(name_competition__icontains=query)

    status = request.GET.get('status')
    if status == 'pending':
        competitions = competitions.filter(status_competition=True, date_event__gt=today)
    elif status == 'completed':
        competitions = competitions.filter(status_competition=True, date_event__lt=today)
    elif status == 'ongoing':
        competitions = competitions.filter(status_competition=True, date_event=today)
    elif status == 'not_scheduled':
        competitions = competitions.filter(status_competition=False)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        competitions = competitions.filter(date_event__range=[start_date, end_date])

    context = {
        'title': 'Список соревнований',
        'competitions': competitions,
        'menu': page_menu[:1],
        'today': today
    }
    return render(request, 'AppArena/competitions.html', context)


@login_required
def add_competition(request):
    page_menu = MENU.copy()
    if request.method == 'POST':
        form = AddCompetitionForm(request.POST)
        if form.is_valid():
            form.instance.organizer = request.user
            form.save()
            return redirect('show_competitions')
    else:
        form = AddCompetitionForm()
    context = {
        'title': "Добавление соревнования",
        'form': form,
        'menu': page_menu[1:]
    }
    return render(request, 'AppArena/add_competition.html', context)


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def edit_profile(request, id_user):
    user = get_object_or_404(User, pk=id_user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('show_competitions')
    else:
        form = ProfileForm(instance=user)
    context = {
        'title': "Редактирование профеля",
        'form': form,
    }
    return render(request, 'AppArena/edit_profile.html', context)


def delete_competition(request, comp_slug):
    comp = get_object_or_404(Competition, slug=comp_slug)
    if request.user.groups.filter(name='referee').exists():
        comp.status_competition = not comp.status_competition
        comp.save()
        return redirect('show_competitions')
    else:
        return HttpResponse("Вы не имеете права на удаление соревнования.", status=403)


def show_competition(request, comp_slug):
    comp = get_object_or_404(Competition, slug=comp_slug)
    categories = Category.objects.filter(id_competition=comp)
    context = {
        'title': f"{comp.name_competition}",
        'comp': comp,
        'categories': categories,
        'role': request.user.groups.all()

    }
    return render(request, 'AppArena/competition_view.html', context)


def choose_judges(request, comp_slug):
    competition = get_object_or_404(Competition, slug=comp_slug)
    if request.method == 'POST':
        form = JudgesForm(request.POST)
        if form.is_valid():
            judges = form.cleaned_data['judges']
            for judge in judges:
                CompetitorReferee.objects.create(competition=competition, referee=judge)
            return redirect('show_competitions')
    else:
        form = JudgesForm()
    return render(request, 'AppArena/choose_judges.html', {'form': form, 'competition': competition})


def category(request, comp_slug, category_slug):
    comp = get_object_or_404(Competition, slug=comp_slug)
    category = get_object_or_404(Category, slug=category_slug)
    applications = Application.objects.filter(id_category_id=category.pk)
    print(applications)
    context = {
        'title': "Список участников",
        'applications': applications,
        'comp_slug': comp_slug,
        'category_slug': category_slug
    }
    return render(request, 'AppArena/category_view.html', context)