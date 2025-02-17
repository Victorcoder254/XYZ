# Generated by Django 5.1.6 on 2025-02-17 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_customquestion_options_customquestion_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobdescription',
            name='salary_range',
        ),
        migrations.AddField(
            model_name='jobdescription',
            name='maximum_pay',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Maximum annual salary', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='jobdescription',
            name='minimum_pay',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Minimum annual salary', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='jobdescription',
            name='job_category',
            field=models.CharField(blank=True, help_text='Select from common categories or enter your own', max_length=100, null=True),
        ),
    ]
