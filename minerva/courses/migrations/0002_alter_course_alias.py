# Generated by Django 5.1.4 on 2024-12-08 22:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='alias',
            field=models.CharField(max_length=16, unique=True, validators=[django.core.validators.RegexValidator(message='Alias must contain only lowercase letters, numbers, underscores (_), or hyphens (-), without spaces.', regex='^[a-z0-9_-]+$')]),
        ),
    ]