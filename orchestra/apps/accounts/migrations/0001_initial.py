# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'INDIVIDUAL', max_length=32, verbose_name='type', choices=[(b'INDIVIDUAL', 'Individual'), (b'ASSOCIATION', 'Association'), (b'CUSTOMER', 'Customer'), (b'COMPANY', 'Company'), (b'PUBLICBODY', 'Public body')])),
                ('language', models.CharField(default=b'en', max_length=2, verbose_name='language', choices=[(b'en', 'English')])),
                ('register_date', models.DateTimeField(auto_now_add=True, verbose_name='register date')),
                ('comments', models.TextField(max_length=256, verbose_name='comments', blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(related_name=b'accounts', verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
