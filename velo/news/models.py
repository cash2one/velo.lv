from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse

from base64 import b32encode
from hashlib import sha1
from random import random
from slugify import slugify

from velo.velo.mixins.models import StatusMixin, TimestampMixin


def notification_slug():
    pk = None
    bad_pk = True
    while bad_pk:
        pk = b32encode(sha1(str(random())).digest()).lower()[:6]
        bad_pk = False
        if not bad_pk:
            try:
                Notification.objects.get(slug=pk)
                bad_pk = True
            except Notification.DoesNotExist:
                bad_pk = False
    return pk


class Notification(StatusMixin, models.Model):
    slug = models.CharField(max_length=6, default=notification_slug)
    title = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.title


class NewsManagerPublished(models.Manager):
    def published(self, competition_ids=None):
        queryset = super(NewsManagerPublished, self).get_queryset().filter(published_on__lte=timezone.now()).order_by('-published_on')
        if competition_ids:
            queryset = queryset.filter(competition_id__in=competition_ids)
        return queryset


class News(StatusMixin, TimestampMixin, models.Model):

    language = models.CharField("Language", max_length=20, db_index=True, default='lv', choices=settings.LANGUAGES)

    title = models.CharField("Title", max_length=255)
    slug = models.SlugField("Slug", unique=True)
    image = models.ForeignKey('gallery.Photo', blank=True, null=True)
    competition = models.ForeignKey('core.Competition', blank=True, null=True, limit_choices_to={'level__lte': 1})
    published_on = models.DateTimeField(default=timezone.now)

    intro_content = RichTextUploadingField()
    content = RichTextUploadingField(blank=True)

    objects = NewsManagerPublished()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.competition:
            return reverse('news:news', args=[self.competition_id, self.slug])
        return reverse('news:news', args=[self.slug])

    def save(self, *args, **kwargs):
        cache.delete(make_template_fragment_key("index_news", [self.language]))
        if not self.slug:
            self.slug = slugify(self.title)
        return super(News, self).save(*args, **kwargs)


class Comment(StatusMixin, TimestampMixin, models.Model):
    news = models.ForeignKey(News)
    content = models.TextField()

    legacy_id = models.IntegerField(null=True, blank=True)
