from decimal import Decimal

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from datetime import timedelta

from .models import *


class SignUpForm(UserCreationForm):
    patronymic = forms.CharField(label='Отчество', widget=forms.TextInput(), max_length=45)

    ROLE_CHOICES = (
        (1, 'Участник'),
        (0, 'Tренер'),
    )

    role = forms.ChoiceField(label='Роль', choices=ROLE_CHOICES, widget=forms.Select(), required=False)

    license_number_trainer = forms.CharField(label='Лицензия', max_length=10, widget=forms.TextInput(), required=False)

    medical_insurance_participants = forms.CharField(label='Страховка', max_length=10, widget=forms.TextInput(),
                                                     required=False)
    weight_participants = forms.DecimalField(label='Вес', max_digits=6, decimal_places=3, widget=forms.NumberInput(),
                                             required=False)
    date_birth_participants = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'})
                                              , required=False)

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'patronymic', 'password1', 'password2', 'role',
                  'license_number_trainer', 'weight_participants', 'date_birth_participants']
        labels = {
            'username': 'Логин'
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        license_number_trainer = cleaned_data.get('license_number_trainer')
        medical_insurance_participants = cleaned_data.get('medical_insurance_participants')
        weight_participants = cleaned_data.get('weight_participants')
        date_birth_participants = cleaned_data.get('date_birth_participants')

        date_birth = self.cleaned_data.get('date_birth_participants')
        if date_birth and date_birth > timezone.now().date():
            self.add_error('date_birth_participants', "Не верная дата рождения")
        if date_birth_participants and date_birth_participants > timezone.now().date() - timedelta(days=365 * 4):
            self.add_error('date_birth_participants', "Не верная дата рождения")

        if weight_participants is not None:
            weight_float = Decimal(weight_participants)
            if weight_float < 25:
                self.add_error('weight_participants',
                               "Не верный вес")

        if role == '0' and not license_number_trainer:
            self.add_error('license_number_trainer', 'Поле "Лицензия" обязательно для тренера')

        if role == '1' and not medical_insurance_participants:
            self.add_error('medical_insurance_participants',
                           'Для участника необходимо Страховку')
        if role == '1' and not weight_participants:
            self.add_error('weight_participants',
                           'Для участника необходимо заполнить Вес"')
        if role == '1' and not date_birth_participants:
            self.add_error('date_birth_participants',
                           'Для участника необходимо заполнить Дату рождения')

        if len(medical_insurance_participants) != 10 and role == '1':
            self.add_error('medical_insurance_participants', "Страховка имеет размер в 10 символов")

        if len(license_number_trainer) != 10 and role == '0':
            self.add_error('license_number_trainer', "Лицензия имеет размер в 10 символов")

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

            expansion_user.medical_insurance_participants = (
                self.cleaned_data.get('medical_insurance_participants', None))

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
        fields = ['name_competition', 'date_event', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'textarea_class'}),
            'date_event': forms.DateInput(attrs={'type': 'date'}),
            'name_competition': forms.Textarea(attrs={'class': 'textarea_class'}),

        }

    def clean(self):
        cleaned_data = super().clean()
        date_event = cleaned_data.get('date_event')

        if date_event and date_event < timezone.now().date():
            self.add_error('date_event', "Не верная дата")


class ProfileForm(forms.ModelForm):


    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name']

    def save(self, commit=True):
        user = super().save(commit=True)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()


class JudgesForm(forms.Form):
    judges = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['judges'].queryset = User.objects.filter(is_staff=True)

    def save(self, commit=True):
        judges = self.cleaned_data['judges']
        for judge in judges:
            CompetitorReferee.objects.create(referee=judge)
        return judges
