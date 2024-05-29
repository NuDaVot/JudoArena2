# management/commands/populate_database.py
from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from AppArena.models import ExpansionUser, TrainerParticipant
import random
fake = Faker()

# Список возможных отчеств
patronymics = [
    'Александрович', 'Алексеевич', 'Анатольевич', 'Владимирович', 'Викторович',
    'Дмитриевич', 'Евгеньевич', 'Иванович', 'Михайлович', 'Петрович', 'Сергеевич'
]


class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        self.create_trainers()
        self.create_participants()

    def create_trainers(self, username_prefix='trainer', count=10):
        for i in range(count):
            username = f'{username_prefix}_{i}'
            password = 'your_password'  # замените это на реальный пароль
            first_name = fake.first_name()
            last_name = fake.last_name()
            patronymic = random.choice(patronymics)

            # Создание пользователя Django
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            user.groups.set([1])  # Установка группы "Тренер"
            # Создание профиля ExpansionUser
            expansion_user = ExpansionUser.objects.create(
                user=user,
                patronymic=patronymic,
                license_number_trainer=fake.random_number(digits=10)
                # заполните остальные поля аналогичным образом
            )
            print(f'Created trainer: {username}')

    def create_participants(self):
        trainers = User.objects.filter(groups__name='Тренер')
        for trainer in trainers:
            for category in range(1, 9):  # Диапазон категорий
                for _ in range(10):  # Создание 15 участников для каждой категории
                    username = fake.user_name()
                    password = 'your_password'  # замените это на реальный пароль
                    first_name = fake.first_name()
                    last_name = fake.last_name()
                    patronymic = random.choice(patronymics)
                    birth_date = fake.date_of_birth(minimum_age=14, maximum_age=16)  # Генерация даты рождения
                    weight = random.randint(42, 110)  # Генерация веса
                    insurance_number = fake.random_number(digits=10)  # Генерация номера страховки

                    # Создание пользователя Django
                    user = User.objects.create_user(username=username, password=password, first_name=first_name,
                                                    last_name=last_name)
                    user.groups.set([2])  # Установка группы "Участник"

                    # Создание профиля ExpansionUser
                    expansion_user = ExpansionUser.objects.create(
                        user=user,
                        patronymic=patronymic,
                        medical_insurance_participants=insurance_number,
                        weight_participants=weight,
                        date_birth_participants=birth_date,
                        category_referee=category  # Установка категории
                    )

                    # Создание записи TrainerParticipant
                    TrainerParticipant.objects.create(user_trainer=trainer, user_participant=user)

                    print(f'Created participant: {username}')