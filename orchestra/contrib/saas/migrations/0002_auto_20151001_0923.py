# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('saas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='saas',
            name='custom_url',
            field=models.URLField(verbose_name='custom URL', blank=True, help_text='Optional and alternative URL for accessing this service instance. A related website will be automatically configured if needed.'),
        ),
        migrations.AlterField(
            model_name='saas',
            name='service',
            field=models.CharField(choices=[('bscw', 'BSCW'), ('dokuwiki', 'Dowkuwiki'), ('drupal', 'Drupal'), ('gitlab', 'GitLab'), ('moodle', 'Moodle'), ('seafile', 'SeaFile'), ('wordpress', 'WordPress'), ('phplist', 'phpList')], verbose_name='service', max_length=32),
        ),
    ]
