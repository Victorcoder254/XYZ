# Generated by Django 5.1.6 on 2025-02-16 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_jobapplication_additional_info_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplication',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='core.student'),
        ),
    ]
