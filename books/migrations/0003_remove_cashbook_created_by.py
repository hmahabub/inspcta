# Generated by Django 4.2.20 on 2025-04-14 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0002_rename_reference_bankbook_particulars_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cashbook",
            name="created_by",
        ),
    ]
