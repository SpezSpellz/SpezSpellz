# Generated by Django 5.1.1 on 2024-10-28 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spezspellz', '0022_notification_ref_alter_notification_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='comment_reply_notifications',
            field=models.BooleanField(default=True),
        ),
    ]