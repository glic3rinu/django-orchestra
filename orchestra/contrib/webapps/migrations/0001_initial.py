# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import orchestra.core.validators
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WebApp',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128, validators=[orchestra.core.validators.validate_name], help_text='The app will be installed in %(home)s/webapps/%(app_name)s', verbose_name='name')),
                ('type', models.CharField(max_length=32, choices=[('php', 'PHP'), ('python', 'Python'), ('static', 'Static'), ('symbolic-link', 'Symbolic link'), ('webalizer', 'Webalizer'), ('wordpress-php', 'WordPress')], verbose_name='type')),
                ('data', jsonfield.fields.JSONField(verbose_name='data', help_text='Extra information dependent of each service.', blank=True, default={})),
                ('account', models.ForeignKey(related_name='webapps', to=settings.AUTH_USER_MODEL, verbose_name='Account')),
            ],
            options={
                'verbose_name': 'Web App',
                'verbose_name_plural': 'Web Apps',
            },
        ),
        migrations.CreateModel(
            name='WebAppOption',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128, choices=[(None, '-------'), ('FileSystem', [('public-root', 'Public root')]), ('Process', [('timeout', 'Process timeout'), ('processes', 'Number of processes')]), ('PHP', [('enable_functions', 'Enable functions'), ('allow_url_include', 'Allow URL include'), ('allow_url_fopen', 'Allow URL fopen'), ('auto_append_file', 'Auto append file'), ('auto_prepend_file', 'Auto prepend file'), ('date.timezone', 'date.timezone'), ('default_socket_timeout', 'Default socket timeout'), ('display_errors', 'Display errors'), ('extension', 'Extension'), ('magic_quotes_gpc', 'Magic quotes GPC'), ('magic_quotes_runtime', 'Magic quotes runtime'), ('magic_quotes_sybase', 'Magic quotes sybase'), ('max_input_time', 'Max input time'), ('max_input_vars', 'Max input vars'), ('memory_limit', 'Memory limit'), ('mysql.connect_timeout', 'Mysql connect timeout'), ('output_buffering', 'Output buffering'), ('register_globals', 'Register globals'), ('post_max_size', 'Post max size'), ('sendmail_path', 'Sendmail path'), ('session.bug_compat_warn', 'Session bug compat warning'), ('session.auto_start', 'Session auto start'), ('safe_mode', 'Safe mode'), ('suhosin.post.max_vars', 'Suhosin POST max vars'), ('suhosin.get.max_vars', 'Suhosin GET max vars'), ('suhosin.request.max_vars', 'Suhosin request max vars'), ('suhosin.session.encrypt', 'Suhosin session encrypt'), ('suhosin.simulation', 'Suhosin simulation'), ('suhosin.executor.include.whitelist', 'Suhosin executor include whitelist'), ('upload_max_filesize', 'Upload max filesize'), ('zend_extension', 'Zend extension')])], verbose_name='name')),
                ('value', models.CharField(max_length=256, verbose_name='value')),
                ('webapp', models.ForeignKey(related_name='options', to='webapps.WebApp', verbose_name='Web application')),
            ],
            options={
                'verbose_name': 'option',
                'verbose_name_plural': 'options',
            },
        ),
        migrations.AlterUniqueTogether(
            name='webappoption',
            unique_together=set([('webapp', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='webapp',
            unique_together=set([('name', 'account')]),
        ),
    ]
