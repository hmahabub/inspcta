# Generated by Django 4.2.20 on 2025-04-12 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0002_sale_task_delete_salesentry"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="bl_qtn",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name="sale",
            name="buyer",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="sale",
            name="cargo",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name="sale",
            name="date_of_ins",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name="sale",
            name="ins_qtn",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name="sale",
            name="job_order_no",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="sale",
            name="plc_of_ins",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name="sale",
            name="shipper",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
