# Generated by Django 5.1.1 on 2024-10-15 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spezspellz', '0013_merge_20241015_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='avatar',
            field=models.FileField(null=True, upload_to='content'),
        ),
    ]
