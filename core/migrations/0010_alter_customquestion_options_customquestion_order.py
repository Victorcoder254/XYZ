# Generated by Django 5.1.6 on 2025-02-17 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_customquestion_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customquestion',
            options={'ordering': ['-order']},
        ),
        migrations.AddField(
            model_name='customquestion',
            name='order',
            field=models.IntegerField(blank=True, default=0, help_text='Order in which questions should appear', null=True),
        ),
    ]
