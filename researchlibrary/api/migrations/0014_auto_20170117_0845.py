# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-17 08:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("api", "0013_auto_20160915_1518")]

    operations = [
        migrations.AlterField(
            model_name="resource",
            name="resource_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("CATALOG", "Database or catalog"),
                    ("LEGAL_DOCUMENT", "Government report or legal document"),
                    ("MAGAZINE_ARTICLE", "Magazine article"),
                    ("JOURNAL_ARTICLE", "Journal article"),
                    ("PRESENTATION", "Presentation"),
                    ("STUDY_REPORT", "Project or study report"),
                    ("SCHOLARLY_BOOK", "Scholarly book"),
                    ("TEXTBOOK", "Textbook"),
                    ("THESIS", "Thesis or dissertation"),
                    ("WEBSITE", "Website"),
                    ("WORKING_PAPER", "Working paper"),
                    ("STUDY", "Study"),
                    ("CASESTUDY", "Case study"),
                    ("QUASI_EXPERIMENT", "Quasi-experiment"),
                    ("RCT", "Randomized controlled trial"),
                    ("RESEARCH_SUMMARY", "Literature review"),
                    ("METASTUDY", "Meta-analysis"),
                    ("SYSTEMATIC_REVIEW", "Systematic review"),
                    ("OPINION_PIECE", "Opinion piece"),
                    ("HISTORICAL_DOCUMENT", "Historical document"),
                    ("ENCYCLOPEDIA_ARTICLE", "Encyclopedia entry"),
                    ("BOOK", "Nonfiction book"),
                    ("NEWS_ARTICLE", "Newspaper article"),
                    ("BLOG_ARTICLE", "Blog post"),
                    ("OTHER", "Other"),
                ],
                max_length=30,
            ),
        )
    ]
