# Generated by Django 5.1.1 on 2024-10-24 11:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spezspellz', '0020_remove_userinfo_unread_notifications'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=50)),
                ('additional', models.CharField(max_length=50)),
                ('body', models.CharField(max_length=256)),
                ('icon', models.FileField(null=True, upload_to='content')),
                ('is_read', models.BooleanField(default=False)),
                ('bell_clicked', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
