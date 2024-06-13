from django.db import models
from django.urls import reverse
from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify
from .utils import unique_slugify


class ExpansionUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patronymic = models.CharField(max_length=45, verbose_name='Отчество')

    category_referee = models.IntegerField(null=True, blank=True, verbose_name='Категория')

    license_number_trainer = models.CharField(max_length=10, null=True, blank=True, verbose_name='Лицензия')

    medical_insurance_participants = models.CharField(max_length=10, null=True, blank=True, verbose_name='Номер страхования жизни')
    weight_participants = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name='Вес')
    date_birth_participants = models.DateField(null=True, blank=True, verbose_name='Дата рождения')

    def __str__(self):
        if self.date_birth_participants is None:
            return f'{self.user.last_name} {self.user.first_name[:1]}. {self.patronymic[:1]}.'
        else:
            return f'{self.user.last_name} {self.user.first_name[:1]}.  {self.patronymic[:1]}. {self.date_birth_participants}'


class TrainerParticipant(models.Model):
    user_trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer')
    user_participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participant')


class Competition(models.Model):
    name_competition = models.CharField(max_length=100, verbose_name='Название')
    date_event = models.DateField(verbose_name='Дата проведения')
    address = models.CharField(max_length=127, verbose_name='Адрес')
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    status_competition = models.BooleanField(default=True, verbose_name='Статус')
    organizer = models.ForeignKey(ExpansionUser, on_delete=models.CASCADE, verbose_name='Организатор')
    slug = models.SlugField(max_length=255, unique=True,
                            verbose_name='Уникальное название')
    date_end = models.DateField(verbose_name='Дата завершения')

    def __str__(self):
        return self.name_competition

    def get_absolute_url(self):
        return reverse('competition', kwargs={'competition_id': self.pk})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name_competition)
            print(self.slug)
        super().save(*args, **kwargs)


class CompetitorReferee(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    referee = models.ForeignKey(User, on_delete=models.CASCADE)


class Age(models.Model):
    age_start = models.DateField()
    age_end = models.DateField()

    def __str__(self):
        return f"{self.age_start} - {self.age_end}"


class Weight(models.Model):
    weight_start = models.DecimalField(max_digits=6, decimal_places=3)
    weight_end = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return f"{self.weight_start} - {self.weight_end}"


class Category(models.Model):
    id_competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    id_weight = models.ForeignKey(Weight, on_delete=models.CASCADE)
    id_age = models.ForeignKey(Age, on_delete=models.CASCADE)

    def __str__(self):
        return f"Category {self.id} - Competition {self.id_competition} - Weight {self.id_weight} - Age {self.id_age}"

    def get_absolute_url(self):
        return reverse('category', kwargs={'category_id': self.pk})


class Application(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer_applications')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participant_applications')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status_application = models.BooleanField(default=False)

    def __str__(self):
        return (f"Application {self.id} - Participant {self.participant.last_name} - Category {self.category} - "
                f"Trainer {self.trainer.last_name}")

    def get_absolute_url(self):
        return reverse('application', kwargs={'application_id': self.pk})


class Meet(models.Model):
    id_white = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_meets', null=True, blank=True)
    id_blue = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blue_meets', null=True, blank=True)
    sequence_number = models.IntegerField(null=True, blank=True)
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    id_judge = models.ForeignKey(ExpansionUser, related_name='judge_meets', on_delete=models.CASCADE, null=True, blank=True)
    duration = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    assessments = models.TextField(null=True, blank=True)
    result = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Meet sequence_number {self.sequence_number} - White {self.id_white} - Blue {self.id_blue} - Category {self.id_category}"

    def get_absolute_url(self):
        return reverse('meet', kwargs={'meet_id': self.pk})
