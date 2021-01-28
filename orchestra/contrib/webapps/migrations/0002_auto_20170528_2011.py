# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-28 18:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapps', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webapp',
            name='type',
            field=models.CharField(choices=[('moodle-php', 'Moodle'), ('php', 'PHP'), ('python', 'Python'), ('static', 'Static'), ('symbolic-link', 'Symbolic link'), ('webalizer', 'Webalizer'), ('wordpress-php', 'WordPress')], max_length=32, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='webappoption',
            name='name',
            field=models.CharField(choices=[(None, '-------'), ('FileSystem', [('public-root', 'Public root')]), ('Process', [('timeout', 'Process timeout'), ('processes', 'Number of processes')]), ('PHP', [('enable_functions', 'Enable functions'), ('disable_functions', 'Disable functions'), ('allow_url_include', 'Allow URL include'), ('allow_url_fopen', 'Allow URL fopen'), ('auto_append_file', 'Auto append file'), ('auto_prepend_file', 'Auto prepend file'), ('date.timezone', 'date.timezone'), ('default_socket_timeout', 'Default socket timeout'), ('display_errors', 'Display errors'), ('extension', 'Extension'), ('include_path', 'Include path'), ('magic_quotes_gpc', 'Magic quotes GPC'), ('magic_quotes_runtime', 'Magic quotes runtime'), ('magic_quotes_sybase', 'Magic quotes sybase'), ('max_input_time', 'Max input time'), ('max_input_vars', 'Max input vars'), ('memory_limit', 'Memory limit'), ('mysql.connect_timeout', 'Mysql connect timeout'), ('output_buffering', 'Output buffering'), ('register_globals', 'Register globals'), ('post_max_size', 'Post max size'), ('sendmail_path', 'Sendmail path'), ('session.bug_compat_warn', 'Session bug compat warning'), ('session.auto_start', 'Session auto start'), ('safe_mode', 'Safe mode'), ('suhosin.post.max_vars', 'Suhosin POST max vars'), ('suhosin.get.max_vars', 'Suhosin GET max vars'), ('suhosin.request.max_vars', 'Suhosin request max vars'), ('suhosin.session.encrypt', 'Suhosin session encrypt'), ('suhosin.simulation', 'Suhosin simulation'), ('suhosin.executor.include.whitelist', 'Suhosin executor include whitelist'), ('upload_max_filesize', 'Upload max filesize'), ('upload_tmp_dir', 'Upload tmp dir'), ('zend_extension', 'Zend extension')])], max_length=128, verbose_name='name'),
        ),
    ]