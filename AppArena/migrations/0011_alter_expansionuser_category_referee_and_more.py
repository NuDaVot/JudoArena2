# Generated by Django 5.0.6 on 2024-05-29 20:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppArena', '0010_trainerparticipant'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='expansionuser',
            name='category_referee',
            field=models.IntegerField(blank=True, null=True, verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='meet',
            name='id_blue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blue_meets', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='meet',
            name='id_white',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='white_meets', to=settings.AUTH_USER_MODEL),
        ),
    ]
