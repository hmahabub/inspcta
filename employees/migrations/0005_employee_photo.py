# Generated by Django 4.2.20 on 2025-05-05 05:37

from django.db import migrations, models
import employees.models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0004_alter_employee_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="photo",
            field=models.ImageField(
                blank=True,
                help_text="Maximum file size allowed is 500KB",
                null=True,
                upload_to="employee_photos/",
                validators=[employees.models.Employee.validate_image_size],
                verbose_name="Employee Photo",
            ),
        ),
    ]
