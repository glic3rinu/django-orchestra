# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=64, validators=[orchestra.core.validators.validate_name], verbose_name='name')),
                ('type', models.CharField(max_length=32, default='mysql', choices=[('mysql', 'MySQL')], verbose_name='type')),
                ('account', models.ForeignKey(verbose_name='Account', to=settings.AUTH_USER_MODEL, related_name='databases')),
            ],
        ),
        migrations.CreateModel(
            name='DatabaseUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('username', models.CharField(max_length=16, validators=[orchestra.core.validators.validate_name], verbose_name='username')),
                ('password', models.CharField(max_length=256, verbose_name='password')),
                ('type', models.CharField(max_length=32, default='mysql', choices=[('mysql', 'MySQL')], verbose_name='type')),
                ('account', models.ForeignKey(verbose_name='Account', to=settings.AUTH_USER_MODEL, related_name='databaseusers')),
            ],
            options={
                'verbose_name_plural': 'DB users',
            },
        ),
        migrations.AddField(
            model_name='database',
            name='users',
            field=models.ManyToManyField(verbose_name='users', related_name='databases', to='databases.DatabaseUser'),
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
