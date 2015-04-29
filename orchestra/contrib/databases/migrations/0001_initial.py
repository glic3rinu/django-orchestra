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
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=64, validators=[orchestra.core.validators.validate_name])),
                ('type', models.CharField(default='mysql', choices=[('mysql', 'MySQL'), ('postgres', 'PostgreSQL')], verbose_name='type', max_length=32)),
                ('account', models.ForeignKey(related_name='databases', verbose_name='Account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DatabaseUser',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('username', models.CharField(verbose_name='username', max_length=16, validators=[orchestra.core.validators.validate_name])),
                ('password', models.CharField(verbose_name='password', max_length=256)),
                ('type', models.CharField(default='mysql', choices=[('mysql', 'MySQL'), ('postgres', 'PostgreSQL')], verbose_name='type', max_length=32)),
                ('account', models.ForeignKey(related_name='databaseusers', verbose_name='Account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'DB users',
            },
        ),
        migrations.AddField(
            model_name='database',
            name='users',
            field=models.ManyToManyField(related_name='databases', to='databases.DatabaseUser', verbose_name='users', blank=True),
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
