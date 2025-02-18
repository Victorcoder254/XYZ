# Generated by Django 5.1.6 on 2025-02-18 01:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_jobdescription_salary_range_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CPCJobFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minimum_salary', models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='Minimum salary for job listings', max_digits=10, null=True)),
                ('allowed_employment_types', models.JSONField(blank=True, help_text='Specific employment types allowed (JSON array)', null=True)),
                ('allowed_job_categories', models.JSONField(blank=True, help_text='Specific job categories allowed (JSON array)', null=True)),
                ('custom_job_categories', models.JSONField(blank=True, help_text='Enter custom job categories (JSON array)', null=True)),
                ('cpc_profile', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='job_filter', to='core.cpcprofile')),
            ],
        ),
    ]
