# Generated by Django 5.1.6 on 2025-02-18 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_excelsheetupload_faculty_studentprofile_faculty_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='academic_year',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
