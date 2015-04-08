# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('systemusers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemuser',
            name='account',
            field=models.ForeignKey(related_name='systemusers', to=settings.AUTH_USER_MODEL, default=1, verbose_name='Account'),
            preserve_default=False,
        ),
    ]
