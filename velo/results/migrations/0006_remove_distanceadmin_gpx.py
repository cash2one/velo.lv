# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-13 08:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0005_auto_20160408_2011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='distanceadmin',
            name='gpx',
        ),
    ]
