# Generated by Django 5.2.1 on 2025-05-23 07:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='citizenprofile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='officerprofile',
            name='user',
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10, null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('id_number', models.CharField(blank=True, max_length=20, null=True)),
                ('badge_id', models.CharField(blank=True, max_length=50, null=True)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('office_name', models.CharField(blank=True, max_length=100, null=True)),
                ('managed_since', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='AdminProfile',
        ),
        migrations.DeleteModel(
            name='CitizenProfile',
        ),
        migrations.DeleteModel(
            name='OfficerProfile',
        ),
    ]
