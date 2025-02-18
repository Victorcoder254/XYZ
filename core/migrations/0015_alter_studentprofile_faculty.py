# Generated by Django 5.1.6 on 2025-02-18 15:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_studentprofile_academic_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='faculty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_profile', to='core.faculty'),
        ),
    ]
