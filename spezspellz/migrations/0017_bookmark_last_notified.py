# Generated by Django 5.1.1 on 2024-10-17 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spezspellz', '0016_remove_bookmark_last_notified'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookmark',
            name='last_notified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
