# Generated by Django 5.1.4 on 2024-12-26 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Notio", "0002_remove_note_status_note_tags"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Session",
        ),
    ]
