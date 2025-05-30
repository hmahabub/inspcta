# Generated by Django 4.2.20 on 2025-04-12 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LV",
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
                    "vessel_name",
                    models.CharField(
                        help_text="Name of vessel/ship/unit",
                        max_length=100,
                        verbose_name="Vessel Name",
                    ),
                ),
                ("code", models.CharField(blank=True, max_length=15, null=True)),
                (
                    "loa",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                (
                    "brdth",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                (
                    "fb",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=6,
                        null=True,
                        verbose_name="LT/FB (Declared)",
                    ),
                ),
                (
                    "light_fpk",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                (
                    "light_apk",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
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
            ],
        ),
        migrations.CreateModel(
            name="MV",
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
                ("date", models.DateField()),
                ("m_vessel", models.CharField(blank=True, max_length=40, null=True)),
                (
                    "co_eff",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                ("consignee", models.CharField(blank=True, max_length=30, null=True)),
                ("cargo", models.CharField(blank=True, max_length=30, null=True)),
                ("survey", models.CharField(blank=True, max_length=30, null=True)),
                (
                    "shrinkage",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                (
                    "load_fb",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                (
                    "density",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                (
                    "cons",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                (
                    "quantity",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=8, null=True
                    ),
                ),
                (
                    "final_quantity",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=8, null=True
                    ),
                ),
                (
                    "tpc",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                (
                    "load_fpk",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                (
                    "load_apk",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=6, null=True
                    ),
                ),
                ("forw_drft", models.CharField(blank=True, max_length=30, null=True)),
                ("aft_drft", models.CharField(blank=True, max_length=30, null=True)),
                ("mid_drft", models.CharField(blank=True, max_length=30, null=True)),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                (
                    "l_vessel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="l_vessel",
                        to="vessel.lv",
                        verbose_name="Lighter Vessel",
                    ),
                ),
            ],
        ),
    ]
