# Generated by Django 5.1.7 on 2025-04-05 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linenotify', '0002_contact_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='message',
            field=models.TextField(blank=True, null=True),
        ),
    ]
