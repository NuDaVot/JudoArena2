from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.contrib.auth.decorators import login_required
from datetime import date
from datetime import datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import UpdateView
from datetime import date, datetime
from django.db.models import Case, When, IntegerField, Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .utils import group_required

MENU = [{'title': "Добавить соревнование", 'url_name': 'add_competition'},
        {'title': "На главную", 'url_name': 'show_competitions'},
]


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user_form = form.save()
            id_trener = form.cleaned_data['id_trener']
            trener, created = TrainerParticipant.objects.get_or_create(user_trainer=id_trener.user, user_participant=user_form)
            if not created:
                error_message = "Age range already exists."

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


@login_required
@group_required('Секретарь')
def register_refery(request):
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
    return render(request, 'AppArena/register.html', {'form': form, 'title': 'Добавление судьи',
                                                      'name_btn': 'Добавить', 'role': 'Судья'})


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
    today = date.today()
    competitions = Competition.objects.all()

    competitions = competitions.annotate(
        order=Case(
            When(date_event__lte=today, date_end__gte=today, then=0),  # Ongoing
            When(date_event__gt=today, then=1),  # Upcoming
            When(date_event__lt=today, then=2),  # Completed
            output_field=IntegerField(),
        )
    ).order_by('order', 'date_event')
    page_menu = MENU.copy()

    query = request.GET.get('q')
    if query:
        competitions = competitions.filter(name_competition__icontains=query)

    status = request.GET.get('status')
    if status == 'pending':
        competitions = competitions.filter(status_competition=True, date_event__gt=today)
    elif status == 'completed':
        competitions = competitions.filter(status_competition=True, date_event__lt=today)
    elif status == 'ongoing':
        competitions = competitions.filter(Q(date_event__gte=today, date_end__lte=today))
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
@group_required('Секретарь')
def add_competition(request):
    page_menu = MENU.copy()
    if request.method == 'POST':
        form = AddCompetitionForm(request.POST)
        if form.is_valid():
            form.instance.organizer = request.user
            competition = form.save()
            return redirect('choose_judges', competition.slug)
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
    expansion_user = get_object_or_404(ExpansionUser, user_id=id_user)
    groups = user.groups.values_list('name', flat=True)
    if request.method == 'POST':
        form_user = ProfileForm(request.POST, instance=user)
        form_expansion_user = ProfileExpansionForm(request.POST, instance=expansion_user)
        if form_user.is_valid() and form_expansion_user.is_valid():
            form_user.save()
            form_expansion_user.save()
            return redirect('show_competitions')
    else:
        form_user = ProfileForm(instance=user)
        form_expansion_user = ProfileExpansionForm(instance=expansion_user)
    context = {
        'title': "Редактирование профиля",
        'form_user': form_user,
        'form_expansion_user': form_expansion_user,
        'role': list(groups),
    }
    return render(request, 'AppArena/edit_profile.html', context)


@login_required
@group_required('Секретарь')
def reject_application(request, comp_slug, id_category, id_application):
    application = get_object_or_404(Application, id=id_application)
    if request.user.groups.filter(name='Секретарь').exists():
        application.status_application = not application.status_application
        application.save()
        return redirect('category', comp_slug=comp_slug, id_category=id_category)
    else:
        return HttpResponse("Вы не имеете права на удаление соревнования.", status=403)


@login_required
def show_competition(request, comp_slug):
    today = date.today()
    comp = get_object_or_404(Competition, slug=comp_slug)
    categories = Category.objects.filter(id_competition=comp)
    referees = CompetitorReferee.objects.filter(competition=comp).select_related('referee')
    expansion_users = ExpansionUser.objects.filter(user__in=[ref.referee for ref in referees])
    context = {
        'title': f"{comp.name_competition}",
        'comp': comp,
        'categories': categories,
        'role': request.user.groups.all(),
        'today': today,
        'referees': expansion_users,
    }
    return render(request, 'AppArena/competition_view.html', context)


@login_required
@group_required('Секретарь')
def choose_judges(request, comp_slug):
    page_menu = MENU.copy()
    competition = get_object_or_404(Competition, slug=comp_slug)
    previous_url = request.META.get('HTTP_REFERER', '')
    if request.method == 'POST':
        form = JudgesForm(request.POST, competition=competition)
        if form.is_valid():
            judges = form.cleaned_data['judges']

            for judge in judges:
                CompetitorReferee.objects.create(competition=competition, referee=judge.user)

            existing_judges = form.cleaned_data['existing_judges']
            for judge in existing_judges:
                CompetitorReferee.objects.filter(competition=competition, referee=judge.user).delete()
            if 'competitions/' in previous_url:
                return redirect('create_category', competition.slug)
            else:
                return redirect('competition', competition.slug)
    else:
        form = JudgesForm(competition=competition)
    last_name_query = request.GET.get('last_name', '')
    if last_name_query:
        form.fields['judges'].queryset = form.fields['judges'].queryset.filter(
            user__last_name__icontains=last_name_query
        )
        form.fields['existing_judges'].queryset = form.fields['existing_judges'].queryset.filter(
            user__last_name__icontains=last_name_query
        )
    context = {
        'title': f"Добавление судьи на {competition.name_competition}",
        'competition': competition,
        'form': form,
        'menu': page_menu[1:]
    }
    return render(request, 'AppArena/choose_judges.html', context)


@login_required
def category(request, comp_slug, id_category):
    comp = get_object_or_404(Competition, slug=comp_slug)
    category = get_object_or_404(Category, id=id_category)
    query = request.GET.get('q')
    status = request.GET.get('status')
    filters = Q(category_id=category.pk)

    if query:
        filters &= Q(participant__last_name__icontains=query) | Q(trainer__last_name__icontains=query)

    if status:
        filters &= Q(status_application=status)
    if status:
        filters &= Q(status_application=status)

    applications = Application.objects.filter(filters).order_by('-status_application')
    context = {
        'title': "Список участников",
        'applications': applications,
        'comp_slug': comp_slug,
        'category_id': category.pk,
        'comp': comp,
        'title2': f"Участники категории {category.id_weight}кг. {category.id_age}",
    }
    return render(request, 'AppArena/category_view.html', context)


@login_required
@group_required('Секретарь')
def create_category(request, comp_slug):
    competition = get_object_or_404(Competition, slug=comp_slug)

    age_form = AgeForm()
    weight_form = WeightForm()
    category_form = CategoryForm()

    error_message = ''
    if request.method == 'POST':
        if 'add_age' in request.POST:
            age_form = AgeForm(request.POST)
            if age_form.is_valid():
                age_start = age_form.cleaned_data['age_start']
                age_end = age_form.cleaned_data['age_end']
                if age_start:
                    age_start = age_start.replace(month=1, day=1)
                if age_end:
                    age_end = age_end.replace(month=12, day=31)

                if age_start > age_end:
                    error_message = "Дата начала не может быть позже даты окончания"
                elif age_end and age_end > timezone.now().date() - timedelta(days=365 * 4):
                    error_message = "Дата окончания не может быть позже чем на 4 года в будущем"
                else:
                    age, created = Age.objects.get_or_create(age_start=age_start, age_end=age_end)
                    if created:
                        age_form = AgeForm()
                    else:
                        error_message = "Этот возраст уже существует"
        elif 'add_weight' in request.POST:
            weight_form = WeightForm(request.POST)
            if weight_form.is_valid():
                weight_start = weight_form.cleaned_data['weight_start']
                weight_end = weight_form.cleaned_data['weight_end']
                if weight_start < 15:
                    error_message = "Вес начала не может быть менее 15 кг"
                elif weight_start > weight_end:
                    error_message = "Вес начала не может быть больше веса окончания"
                else:
                    weight, created = Weight.objects.get_or_create(weight_start=weight_start, weight_end=weight_end)
                    if created:
                        weight_form = WeightForm()
                    else:
                        error_message = "Этот вес уже существует"

        else:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                id_weight = category_form.cleaned_data['id_weight']
                id_age = category_form.cleaned_data['id_age']

                try:
                    Category.objects.get(id_competition=competition, id_weight=id_weight, id_age=id_age)
                    return render(request, 'AppArena/create_category.html', {
                        'category_form': category_form,
                        'age_form': age_form,
                        'weight_form': weight_form,
                        'error_message': 'Эта категория уже добавлена',
                        'message': '',
                        'comp': competition,
                        'title': f"Добавить категорию на {competition.name_competition}",
                    })
                except ObjectDoesNotExist:
                    category = category_form.save(commit=False)
                    category.id_competition = competition
                    category.save()
                    return render(request, 'AppArena/create_category.html', {
                        'category_form': category_form,
                        'age_form': age_form,
                        'weight_form': weight_form,
                        'error_message': '',
                        'message': 'Успешно добавлена категория',
                        'comp': competition,
                        'title': f"Добавить категорию на {competition.name_competition}",
                    })

    return render(request, 'AppArena/create_category.html', {
        'category_form': category_form,
        'age_form': age_form,
        'weight_form': weight_form,
        'error_message': error_message,
        'message': '',
        'comp': competition,
        'title': f"Добавить категорию на {competition.name_competition}",
    })


@login_required
@group_required('Тренер')
def suitable_participants(request, id_category, id_participant=None):
    category = Category.objects.get(id=id_category)
    logged_in_trainer = request.user

    participant_ids = TrainerParticipant.objects.filter(user_trainer=logged_in_trainer).values_list('user_participant',
                                                                                                    flat=True)
    query = request.GET.get('q')
    if query:
        participants = User.objects.filter(
            last_name__icontains=query,
            id__in=participant_ids,
            expansionuser__date_birth_participants__range=(category.id_age.age_start, category.id_age.age_end),
            expansionuser__weight_participants__range=(category.id_weight.weight_start, category.id_weight.weight_end)
        ).exclude(
            id__in=Application.objects.filter(
                Q(participant__id__in=participant_ids) & Q(category=category)
            ).values_list('participant__id', flat=True)
        )
    else:
        participants = User.objects.filter(
            id__in=participant_ids,
            expansionuser__date_birth_participants__range=(category.id_age.age_start, category.id_age.age_end),
            expansionuser__weight_participants__range=(category.id_weight.weight_start, category.id_weight.weight_end)
        ).exclude(
            id__in=Application.objects.filter(
                Q(participant__id__in=participant_ids) & Q(category=category)
            ).values_list('participant__id', flat=True)
        )


    if id_participant is not None:
        participant = get_object_or_404(User, id=id_participant)
        application, created = Application.objects.get_or_create(trainer=logged_in_trainer, participant=participant, category=category)
        if created:
            application_form = ApplicationForm()
        else:
            error_message = "Ошибка"

    context = {
        'participants': participants,
        'category': category,
        'comp_slug': category.id_competition.slug,
        'title': f"Падача заявки на {category.id_competition.name_competition}",
        'title2': f"Подходящие участники категории {category.id_weight}кг. {category.id_age}",
    }
    return render(request, 'AppArena/suitable_participants.html', context)

@login_required
def meets(request, comp_slug, id_category):
    print(1)
    category = get_object_or_404(Category, id=id_category)
    applications = Application.objects.filter(category_id=category)
    meets = Meet.objects.filter(id_category_id=category)

    context = {
        'title': "Список встреч",
        'applications': applications,
        'meets': meets,
    }
    return render(request, 'AppArena/meets_view.html', context)

