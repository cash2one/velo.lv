# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-26 18:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import easy_thumbnails.fields
import velo.gallery.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('title', models.CharField(max_length=255)),
                ('gallery_date', models.DateField()),
                ('photographer', models.CharField(blank=True, max_length=255)),
                ('folder', models.FilePathField(allow_files=False, allow_folders=True, path='media/gallery/', recursive=True)),
                ('description', models.TextField(blank=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('is_internal', models.BooleanField(default=False)),
                ('is_agency', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-gallery_date', '-id'),
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('description', models.TextField(blank=True)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(blank=True, max_length=255, upload_to=velo.gallery.models._get_image_upload_path)),
                ('md5', models.CharField(blank=True, max_length=32)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_numbered', models.BooleanField(default=False)),
                ('is_processed', models.BooleanField(default=False)),
                ('is_vertical', models.NullBooleanField(default=None)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ('image',),
                'permissions': (('can_assign_numbers', 'Can assign numbers'),),
            },
        ),
        migrations.CreateModel(
            name='PhotoNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('x1', models.FloatField(blank=True, null=True)),
                ('y1', models.FloatField(blank=True, null=True)),
                ('x2', models.FloatField(blank=True, null=True)),
                ('y2', models.FloatField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_photonumber_set', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_photonumber_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('status', models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active'), (-1, 'Deleted')], default=0)),
                ('kind', models.PositiveSmallIntegerField(choices=[(1, 'YouTube'), (2, 'Vimeo')], default=1)),
                ('video_id', models.CharField(max_length=50)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('channel_title', models.CharField(blank=True, max_length=255)),
                ('view_count', models.IntegerField(default=0)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_agency_video', models.BooleanField(default=False)),
                ('ordering', models.IntegerField(default=0)),
                ('image_maxres', models.URLField(blank=True)),
                ('image', models.URLField(blank=True)),
                ('competition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Competition')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_video_set', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_video_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('is_featured', 'ordering', 'title'),
                'permissions': (('can_see_unpublished_video', 'Can see unpublished video'),),
            },
        ),
    ]
