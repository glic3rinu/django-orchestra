# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import orchestra.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WebApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(validators=[orchestra.core.validators.validate_name], verbose_name='name', max_length=128)),
                ('type', models.CharField(verbose_name='type', choices=[('php', 'PHP'), ('static', 'Static'), ('symbolic-link', 'Symbolic link'), ('webalizer', 'Webalizer'), ('wordpress-php', 'WordPress')], max_length=32)),
                ('data', jsonfield.fields.JSONField(blank=True, verbose_name='data', help_text='Extra information dependent of each service.', default={})),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Account', related_name='webapps')),
            ],
            options={
                'verbose_name_plural': 'Web Apps',
                'verbose_name': 'Web App',
            },
        ),
        migrations.CreateModel(
            name='WebAppOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='name', choices=[(None, '-------'), ('FileSystem', [('public-root', 'Public root')]), ('Process', [('timeout', 'Process timeout'), ('processes', 'Number of processes')]), ('PHP', [('enabled_functions', 'Enabled functions'), ('allow_url_include', 'Allow URL include'), ('allow_url_fopen', 'Allow URL fopen'), ('auto_append_file', 'Auto append file'), ('auto_prepend_file', 'Auto prepend file'), ('date.timezone', 'date.timezone'), ('default_socket_timeout', 'Default socket timeout'), ('display_errors', 'Display errors'), ('extension', 'Extension'), ('magic_quotes_gpc', 'Magic quotes GPC'), ('magic_quotes_runtime', 'Magic quotes runtime'), ('magic_quotes_sybase', 'Magic quotes sybase'), ('max_execution_time', 'Max execution time'), ('max_input_time', 'Max input time'), ('max_input_vars', 'Max input vars'), ('memory_limit', 'Memory limit'), ('mysql.connect_timeout', 'Mysql connect timeout'), ('output_buffering', 'Output buffering'), ('register_globals', 'Register globals'), ('post_max_size', 'Post max size'), ('sendmail_path', 'sendmail_path'), ('session.bug_compat_warn', 'session.bug_compat_warn'), ('session.auto_start', 'session.auto_start'), ('safe_mode', 'Safe mode'), ('suhosin.post.max_vars', 'Suhosin POST max vars'), ('suhosin.get.max_vars', 'Suhosin GET max vars'), ('suhosin.request.max_vars', 'Suhosin request max vars'), ('suhosin.session.encrypt', 'suhosin.session.encrypt'), ('suhosin.simulation', 'Suhosin simulation'), ('suhosin.executor.include.whitelist', 'suhosin.executor.include.whitelist'), ('upload_max_filesize', 'upload_max_filesize'), ('zend_extension', 'Zend extension')])], max_length=128)),
                ('value', models.CharField(max_length=256, verbose_name='value')),
                ('webapp', models.ForeignKey(to='webapps.WebApp', verbose_name='Web application', related_name='options')),
            ],
            options={
                'verbose_name_plural': 'options',
                'verbose_name': 'option',
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
