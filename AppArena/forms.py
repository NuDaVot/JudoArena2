from decimal import Decimal

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.models import User, Group
from datetime import timedelta

from .models import *

from django import forms
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    patronymic = forms.CharField(label='Отчество', widget=forms.TextInput(), max_length=45)

    ROLE_CHOICES = (
        (1, 'Участник'),
        (0, 'Tренер'),
    )

    role = forms.ChoiceField(label='Роль', choices=ROLE_CHOICES, widget=forms.Select(), required=False)
    license_number_trainer = forms.CharField(label='Лицензия', max_length=10, widget=forms.TextInput(), required=False)
    medical_insurance_participants = forms.CharField(label='Номер страхования жизни', max_length=10,
                                                     widget=forms.TextInput(), required=False)
    weight_participants = forms.DecimalField(label='Вес', max_digits=6, decimal_places=3, widget=forms.NumberInput(),
                                             required=False)
    date_birth_participants = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}),
                                              required=False)
    consent = forms.BooleanField(label='Даю согласие на обработку персональных данных', required=True)

    id_trener = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='Тренер'), label='Тренер', required=False)

    class Meta:
        model = User
        fields = [
            'username', 'last_name', 'first_name', 'patronymic', 'password1', 'password2', 'role',
            'license_number_trainer', 'weight_participants', 'date_birth_participants', 'consent', 'id_trener'
        ]
        labels = {
            'username': 'Логин'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_trener'].empty_label = 'Выберите тренера'
        trainer_group = Group.objects.get(name="Тренер")
        all_trainer = User.objects.filter(groups=trainer_group)
        expansion_users = ExpansionUser.objects.filter(user__in=all_trainer)
        self.fields['id_trener'].queryset = expansion_users

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        license_number_trainer = cleaned_data.get('license_number_trainer')
        medical_insurance_participants = cleaned_data.get('medical_insurance_participants')
        weight_participants = cleaned_data.get('weight_participants')
        date_birth_participants = cleaned_data.get('date_birth_participants')
        id_trener = cleaned_data.get('id_trener')

        date_birth = self.cleaned_data.get('date_birth_participants')
        if date_birth and date_birth > timezone.now().date():
            self.add_error('date_birth_participants', "Не верная дата рождения")
        if date_birth_participants and date_birth_participants > timezone.now().date() - timedelta(days=365 * 4):
            self.add_error('date_birth_participants', "Не верная дата рождения")

        if date_birth_participants and date_birth_participants < timezone.now().date() - timedelta(days=365 * 120):
            self.add_error('date_birth_participants', "Не верная дата рождения")

        if weight_participants is not None:
            weight_float = Decimal(weight_participants)
            if weight_float < 25:
                self.add_error('weight_participants', "Не верный вес")
            if weight_float > 500:
                self.add_error('weight_participants', "Не верный вес")

        if role == '0' and not license_number_trainer:
            self.add_error('license_number_trainer', 'Поле "Лицензия" обязательно для тренера')

        if role == '1' and not medical_insurance_participants:
            self.add_error('medical_insurance_participants', 'Для участника необходимо Страховку')
        if role == '1' and not id_trener:
            self.add_error('id_trener', 'Для участника необходимо выбрать тренера')
        if role == '1' and not weight_participants:
            self.add_error('weight_participants', 'Для участника необходимо заполнить Вес')
        if role == '1' and not date_birth_participants:
            self.add_error('date_birth_participants', 'Для участника необходимо заполнить Дату рождения')

        if role == '1' and medical_insurance_participants and len(medical_insurance_participants) != 10:
            self.add_error('medical_insurance_participants', "Страховка имеет размер в 10 символов")

        if role == '0' and license_number_trainer and len(license_number_trainer) != 10:
            self.add_error('license_number_trainer', "Лицензия имеет размер в 10 символов")

        consent = cleaned_data.get('consent')
        if not consent:
            self.add_error('consent', 'Для регистрации необходимо дать согласие на обработку персональных данных')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=True)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        expansion_user = ExpansionUser(
            user=user,
            patronymic=self.cleaned_data['patronymic'],
        )
        print(self.cleaned_data['role'])
        if self.cleaned_data['role'] == '1':
            user.groups.add(2)
            expansion_user.medical_insurance_participants = self.cleaned_data.get('medical_insurance_participants',
                                                                                  None)
            expansion_user.weight_participants = self.cleaned_data.get('weight_participants', None)
            expansion_user.date_birth_participants = self.cleaned_data.get('date_birth_participants', None)
        else:
            user.groups.add(1)
            expansion_user.license_number_trainer = self.cleaned_data.get('license_number_trainer', None)

        expansion_user.save()
        user.save()
        return user


class SignInForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

        # login.html на 13стр кастыль
        # labels = {
        #     'username': 'Логин',
        # }


class AddCompetitionForm(forms.ModelForm):

    class Meta:
        model = Competition
        fields = ['name_competition', 'date_event', 'address', 'description', 'date_end', 'organizer']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'textarea_class'}),
            'address': forms.Textarea(attrs={'class': 'textarea_class'}),
            'date_event': forms.DateInput(attrs={'type': 'date'}),
            'date_end': forms.DateInput(attrs={'type': 'date'}),
            'name_competition': forms.Textarea(attrs={'class': 'textarea_class'}),

        }

    def clean(self):
        cleaned_data = super().clean()
        date_event = cleaned_data.get('date_event')

        if date_event and date_event < timezone.now().date():
            self.add_error('date_event', "Не верная дата")

        date_end = cleaned_data.get('date_end')

        if date_end and date_end < timezone.now().date():
            self.add_error('date_end', "Не верная дата")
    def __init__(self, *args, **kwargs):
        super(AddCompetitionForm, self).__init__(*args, **kwargs)
        self.fields['organizer'].empty_label = 'Выберите судьбю'
        trainer_group = Group.objects.get(name="Судья")
        all_judges = User.objects.filter(groups=trainer_group)
        expansion_users = ExpansionUser.objects.filter(user__in=all_judges)
        self.fields['organizer'].queryset = expansion_users


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name']


class ProfileExpansionForm(forms.ModelForm):

    class Meta:
        model = ExpansionUser
        fields = ['patronymic', 'medical_insurance_participants',
                  'weight_participants']


class ProfileTrainerParticipant(forms.ModelForm):
    user_trainer = forms.ModelChoiceField(
        queryset=ExpansionUser.objects.filter(user__in=User.objects.filter(groups=Group.objects.get(name="Тренер"))),
        label='Тренер',
    )

    class Meta:
        model = TrainerParticipant
        fields = ['user_trainer']


class JudgesForm(forms.Form):

    judges = forms.ModelMultipleChoiceField(
        queryset=ExpansionUser.objects.select_related('user').all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Добавить судью'
    )
    existing_judges = forms.ModelMultipleChoiceField(
        queryset=ExpansionUser.objects.select_related('user').all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Исключить судью'
    )

    def __init__(self, *args, **kwargs):
        competition = kwargs.pop('competition', None)
        super().__init__(*args, **kwargs)

        judges_group = Group.objects.get(name="Судья")
        all_judges = User.objects.filter(groups=judges_group)
        expansion_users = ExpansionUser.objects.filter(user__in=all_judges)

        if competition:
            existing_judges_qs = User.objects.filter(competitorreferee__competition_id=competition)
            existing_expansion_users_qs = ExpansionUser.objects.filter(user__in=existing_judges_qs)
            self.fields['existing_judges'].queryset = existing_expansion_users_qs
            self.fields['judges'].queryset = expansion_users.exclude(user__in=existing_judges_qs)
        else:
            self.fields['judges'].queryset = expansion_users


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['id_weight', 'id_age']
        labels = {
            'id_weight': 'Весовая категория',
            'id_age': 'Возрастная категория',
        }

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['id_weight'].empty_label = 'Выберите категорию'
        self.fields['id_age'].empty_label = 'Выберите возраст'
        self.fields['id_age'].queryset = Age.objects.all()
        self.fields['id_weight'].queryset = Weight.objects.all()


class AgeForm(forms.ModelForm):
    class Meta:
        model = Age
        fields = ['age_start', 'age_end']
        widgets = {
            'age_start': forms.DateInput(attrs={'type': 'date'}),
            'age_end': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'age_start': 'Начало',
            'age_end': 'Конец',
        }

    def clean_age_start(self):
        age_start = self.cleaned_data['age_start']
        if age_start:
            return age_start.replace(month=1, day=1)
        return age_start

    def clean_age_end(self):
        age_end = self.cleaned_data['age_end']
        if age_end:
            return age_end.replace(month=12, day=31)
        return age_end


class WeightForm(forms.ModelForm):
    class Meta:
        model = Weight
        fields = ['weight_start', 'weight_end']
        widgets = {
            'weight_start': forms.NumberInput(attrs={'type': 'number'}),
            'weight_end': forms.NumberInput(attrs={'type': 'number'}),
        }
        labels = {
            'weight_start': 'Начало',
            'weight_end': 'Конец',
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['trainer', 'participant', 'category']


class MeetForm(forms.ModelForm):
    class Meta:
        model = Meet
        fields = ['id_judge', 'duration', 'assessments', 'result']
        labels = {
            'id_judge': 'Судья',
            'duration': 'Продолжительность (минуты)',
            'assessments': 'Оценки',
            'result': 'Результат',
        }
        widgets = {
            'assessments': forms.Textarea(attrs={'rows': 1}),
        }

    def __init__(self, *args, **kwargs):
        super(MeetForm, self).__init__(*args, **kwargs)
        self.fields['id_judge'].empty_label = 'Выберите судьбю'
        trainer_group = Group.objects.get(name="Судья")
        all_judges = User.objects.filter(groups=trainer_group)
        competitor_referees = CompetitorReferee.objects.filter(referee__in=all_judges)
        expansion_users = ExpansionUser.objects.filter(user__in=competitor_referees.values('referee'))
        self.fields['id_judge'].queryset = expansion_users

