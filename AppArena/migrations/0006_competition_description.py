# Generated by Django 5.0.6 on 2024-05-26 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppArena', '0005_alter_expansionuser_medical_insurance_participants'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
