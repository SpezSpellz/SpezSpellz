# Generated by Django 5.1.1 on 2024-10-03 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spezspellz', '0002_alter_spell_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spell',
            name='thumbnail',
            field=models.FileField(max_length=5001216, null=True, upload_to=''),
        ),
    ]
