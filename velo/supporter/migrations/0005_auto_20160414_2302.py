# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-14 23:02
from __future__ import unicode_literals

from django.db import migrations
import velo.supporter.models


def migrate_data_back(apps, schema_editor):
    pass


def migrate_data(apps, schema_editor):

    velo.supporter.models.Supporter.objects.all().update(is_agency_supporter=False)

    obj = velo.supporter.models.Logo.objects.create(supporter_id=35, svg_logo="supporter/ldz.svg")
    velo.supporter.models.Supporter.objects.filter(id=35).update(default_svg=obj, is_agency_supporter=True)

    obj = velo.supporter.models.Logo.objects.create(supporter_id=2, svg_logo="supporter/seb.svg")
    velo.supporter.models.Supporter.objects.filter(id=2).update(default_svg=obj, is_agency_supporter=True)

    obj = velo.supporter.models.Logo.objects.create(supporter_id=43, svg_logo="supporter/toyota.svg")
    velo.supporter.models.Supporter.objects.filter(id=43).update(default_svg=obj, is_agency_supporter=True)



class Migration(migrations.Migration):

    dependencies = [
        ('supporter', '0004_supporter_default_svg'),
    ]

    operations = [
        migrations.RunPython(migrate_data, migrate_data_back),
    ]
