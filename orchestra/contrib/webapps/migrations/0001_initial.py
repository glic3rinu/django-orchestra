# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WebApp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', validators=[orchestra.core.validators.validate_name], help_text='The app will be installed in %(home)s/webapps/%(app_name)s', max_length=128)),
                ('type', models.CharField(verbose_name='type', max_length=32, choices=[('php', 'PHP'), ('python', 'Python'), ('static', 'Static'), ('symbolic-link', 'Symbolic link'), ('webalizer', 'Webalizer'), ('wordpress-php', 'WordPress')])),
                ('data', jsonfield.fields.JSONField(verbose_name='data', blank=True, help_text='Extra information dependent of each service.', default={})),
                ('account', models.ForeignKey(verbose_name='Account', related_name='webapps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Web App',
                'verbose_name_plural': 'Web Apps',
            },
        ),
        migrations.CreateModel(
            name='WebAppOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', max_length=128, choices=[(None, '-------'), ('FileSystem', [('public-root', 'Public root')]), ('Process', [('timeout', 'Process timeout'), ('processes', 'Number of processes')]), ('PHP', [('enable_functions', 'Enable functions'), ('allow_url_include', 'Allow URL include'), ('allow_url_fopen', 'Allow URL fopen'), ('auto_append_file', 'Auto append file'), ('auto_prepend_file', 'Auto prepend file'), ('date.timezone', 'date.timezone'), ('default_socket_timeout', 'Default socket timeout'), ('display_errors', 'Display errors'), ('extension', 'Extension'), ('magic_quotes_gpc', 'Magic quotes GPC'), ('magic_quotes_runtime', 'Magic quotes runtime'), ('magic_quotes_sybase', 'Magic quotes sybase'), ('max_input_time', 'Max input time'), ('max_input_vars', 'Max input vars'), ('memory_limit', 'Memory limit'), ('mysql.connect_timeout', 'Mysql connect timeout'), ('output_buffering', 'Output buffering'), ('register_globals', 'Register globals'), ('post_max_size', 'Post max size'), ('sendmail_path', 'Sendmail path'), ('session.bug_compat_warn', 'Session bug compat warning'), ('session.auto_start', 'Session auto start'), ('safe_mode', 'Safe mode'), ('suhosin.post.max_vars', 'Suhosin POST max vars'), ('suhosin.get.max_vars', 'Suhosin GET max vars'), ('suhosin.request.max_vars', 'Suhosin request max vars'), ('suhosin.session.encrypt', 'Suhosin session encrypt'), ('suhosin.simulation', 'Suhosin simulation'), ('suhosin.executor.include.whitelist', 'Suhosin executor include whitelist'), ('upload_max_filesize', 'Upload max filesize'), ('zend_extension', 'Zend extension')])])),
                ('value', models.CharField(verbose_name='value', max_length=256)),
                ('webapp', models.ForeignKey(verbose_name='Web application', related_name='options', to='webapps.WebApp')),
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
