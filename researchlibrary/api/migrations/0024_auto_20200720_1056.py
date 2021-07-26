# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-07-20 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("api", "0023_auto_20200506_0950")]

    operations = [
        migrations.AddField(
            model_name="category",
            name="is_visible",
            field=models.CharField(
                choices=[("TRUE", "Yes"), ("FALSE", "No"), ("UNSET", "Unset")],
                default="TRUE",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="resource",
            name="is_visible",
            field=models.CharField(
                choices=[("TRUE", "Yes"), ("FALSE", "No"), ("UNSET", "Unset")],
                default="TRUE",
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name="resource",
            name="url",
            field=models.URLField(blank=True, default="", max_length=2000, verbose_name="URL"),
        ),
    ]