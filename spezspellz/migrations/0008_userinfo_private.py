# Generated by Django 5.1.1 on 2024-10-12 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spezspellz', '0007_alter_attachment_file_alter_spell_thumbnail_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='private',
            field=models.BooleanField(default=False),
        ),
    ]
