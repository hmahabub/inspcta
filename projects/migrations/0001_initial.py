# Generated by Django 4.2.20 on 2025-04-08 16:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("employees", "0001_initial"),
        ("clients", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OperationalCost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "expenditure_type",
                    models.CharField(
                        choices=[
                            ("REGULAR", "Regular"),
                            ("PROVISIONAL", "Provisional"),
                            ("OPERATIONAL", "Operational"),
                        ],
                        max_length=20,
                        verbose_name="Type of Expenditure",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0.01)],
                    ),
                ),
                ("date", models.DateField()),
                ("description", models.TextField()),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("CASH", "Cash"),
                            ("BANK", "Bank Transfer"),
                            ("BKASH", "bKash"),
                            ("CHECK", "Check"),
                        ],
                        max_length=10,
                    ),
                ),
                ("receipt_number", models.CharField(blank=True, max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("escort", models.IntegerField(default=0)),
                ("mariner", models.IntegerField(default=0)),
                ("equipment", models.IntegerField(default=0)),
                ("speedboat", models.IntegerField(default=0)),
                ("others", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ["-date"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RegularEmployeeProjectCost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "expenditure_type",
                    models.CharField(
                        choices=[
                            ("REGULAR", "Regular"),
                            ("PROVISIONAL", "Provisional"),
                            ("OPERATIONAL", "Operational"),
                        ],
                        max_length=20,
                        verbose_name="Type of Expenditure",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0.01)],
                    ),
                ),
                ("date", models.DateField()),
                ("description", models.TextField()),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("CASH", "Cash"),
                            ("BANK", "Bank Transfer"),
                            ("BKASH", "bKash"),
                            ("CHECK", "Check"),
                        ],
                        max_length=10,
                    ),
                ),
                ("receipt_number", models.CharField(blank=True, max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("ot_hours", models.IntegerField(default=0)),
                ("ot_rate", models.IntegerField(default=50)),
                ("conveyance", models.IntegerField(default=0)),
                ("boat_fee", models.IntegerField(default=0)),
                ("fooding_fee", models.IntegerField(default=0)),
                ("hotel_fee", models.IntegerField(default=0)),
                ("night_allownce", models.IntegerField(default=0)),
                ("others", models.IntegerField(default=0)),
                ("paid_in_advance", models.IntegerField(default=0)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="project_costs_regular",
                        to="employees.employee",
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProvisionaryEmployeeProjectCost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "expenditure_type",
                    models.CharField(
                        choices=[
                            ("REGULAR", "Regular"),
                            ("PROVISIONAL", "Provisional"),
                            ("OPERATIONAL", "Operational"),
                        ],
                        max_length=20,
                        verbose_name="Type of Expenditure",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0.01)],
                    ),
                ),
                ("date", models.DateField()),
                ("description", models.TextField()),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("CASH", "Cash"),
                            ("BANK", "Bank Transfer"),
                            ("BKASH", "bKash"),
                            ("CHECK", "Check"),
                        ],
                        max_length=10,
                    ),
                ),
                ("receipt_number", models.CharField(blank=True, max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("fixed_amount", models.IntegerField(default=0)),
                ("ot_hours", models.IntegerField(default=0)),
                ("ot_rate", models.IntegerField(default=50)),
                ("conveyance", models.IntegerField(default=0)),
                ("boat_fee", models.IntegerField(default=0)),
                ("fooding_fee", models.IntegerField(default=0)),
                ("hotel_fee", models.IntegerField(default=0)),
                ("night_allownce", models.IntegerField(default=0)),
                ("others", models.IntegerField(default=0)),
                ("paid_in_advance", models.IntegerField(default=0)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="project_costs_provisionary",
                        to="employees.employee",
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "project_number",
                    models.CharField(
                        help_text="Unique project identifier (e.g., PROJ-2023-001)",
                        max_length=20,
                        unique=True,
                        verbose_name="Project Number",
                    ),
                ),
                (
                    "vessel_name",
                    models.CharField(
                        help_text="Name of vessel/ship/unit",
                        max_length=100,
                        verbose_name="Vessel Name",
                    ),
                ),
                (
                    "starting",
                    models.DateField(
                        help_text="Planned commencement date", verbose_name="Start Date"
                    ),
                ),
                (
                    "ending",
                    models.DateField(
                        help_text="Planned completion date", verbose_name="End Date"
                    ),
                ),
                (
                    "actual_end",
                    models.DateField(
                        blank=True,
                        help_text="Actual completion date",
                        null=True,
                        verbose_name="Actual End Date",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PLANNING", "Planning"),
                            ("ONGOING", "Ongoing"),
                            ("ON_HOLD", "On Hold"),
                            ("COMPLETED", "Completed"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="PLANNING",
                        max_length=10,
                        verbose_name="Status",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="projects",
                        to="clients.client",
                        verbose_name="Client",
                    ),
                ),
            ],
            options={
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
                "ordering": ["-starting", "project_number"],
                "indexes": [
                    models.Index(
                        fields=["project_number"], name="projects_pr_project_338cf3_idx"
                    ),
                    models.Index(
                        fields=["vessel_name"], name="projects_pr_vessel__aafb0a_idx"
                    ),
                    models.Index(
                        fields=["status"], name="projects_pr_status_f023cb_idx"
                    ),
                    models.Index(
                        fields=["starting", "ending"],
                        name="projects_pr_startin_3fc15f_idx",
                    ),
                ],
            },
        ),
    ]
