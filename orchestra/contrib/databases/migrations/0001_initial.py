# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import orchestra.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(validators=[orchestra.core.validators.validate_name], verbose_name='name', max_length=64)),
                ('type', models.CharField(max_length=32, verbose_name='type', choices=[('mysql', 'MySQL')], default='mysql')),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Account', related_name='databases')),
            ],
        ),
        migrations.CreateModel(
            name='DatabaseUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('username', models.CharField(validators=[orchestra.core.validators.validate_name], verbose_name='username', max_length=16)),
                ('password', models.CharField(verbose_name='password', max_length=256)),
                ('type', models.CharField(max_length=32, verbose_name='type', choices=[('mysql', 'MySQL')], default='mysql')),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Account', related_name='databaseusers')),
            ],
            options={
                'verbose_name_plural': 'DB users',
            },
        ),
        migrations.AddField(
            model_name='database',
            name='users',
            field=models.ManyToManyField(to='databases.DatabaseUser', verbose_name='users', blank=True, related_name='databases'),
        ),
        migrations.AlterUniqueTogether(
            name='databaseuser',
            unique_together=set([('username', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='database',
            unique_together=set([('name', 'type')]),
        ),
    ]
