# Generated by Django 5.1.1 on 2024-10-17 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spezspellz', '0017_bookmark_last_notified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookmark',
            name='last_notified',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='last_notified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
