# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-18 09:38
from __future__ import unicode_literals

from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('staticpage', '0004_auto_20160414_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticpage',
            name='content_md',
            field=markdownx.models.MarkdownxField(blank=True),
        ),
    ]
