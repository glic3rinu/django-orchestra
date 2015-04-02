# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapps', '0002_webapp_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webapp',
            name='type',
            field=models.CharField(max_length=32, verbose_name='type', choices=[(b'dokuwiki-mu', b'DokuWiki (SaaS)'), (b'drupal-mu', b'Drupdal (SaaS)'), (b'php4-fcgid', b'PHP 4 FCGID'), (b'php5.2-fcgid', b'PHP 5.2 FCGID'), (b'php5.3-fcgid', b'PHP 5.3 FCGID'), (b'php5.4-fpm', b'PHP 5.4 FPM'), (b'static', b'Static'), (b'symbolic-link', b'Symbolic link'), (b'webalizer', b'Webalizer'), (b'wordpress', b'WordPress'), (b'wordpress-mu', b'WordPress (SaaS)')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='webappoption',
            name='name',
            field=models.CharField(max_length=128, verbose_name='name', choices=[(None, b'-------'), (b'FileSystem', [(b'public-root', 'Public root')]), (b'Process', [(b'timeout', 'Process timeout'), (b'processes', 'Number of processes')]), (b'PHP', [(b'enabled_functions', 'Enabled functions'), (b'allow_url_include', 'Allow URL include'), (b'allow_url_fopen', 'Allow URL fopen'), (b'auto_append_file', 'Auto append file'), (b'auto_prepend_file', 'Auto prepend file'), (b'date.timezone', 'date.timezone'), (b'default_socket_timeout', 'Default socket timeout'), (b'display_errors', 'Display errors'), (b'extension', 'Extension'), (b'magic_quotes_gpc', 'Magic quotes GPC'), (b'magic_quotes_runtime', 'Magic quotes runtime'), (b'magic_quotes_sybase', 'Magic quotes sybase'), (b'max_execution_time', 'Max execution time'), (b'max_input_time', 'Max input time'), (b'max_input_vars', 'Max input vars'), (b'memory_limit', 'Memory limit'), (b'mysql.connect_timeout', 'Mysql connect timeout'), (b'output_buffering', 'Output buffering'), (b'register_globals', 'Register globals'), (b'post_max_size', 'zend_extension'), (b'sendmail_path', 'sendmail_path'), (b'session.bug_compat_warn', 'session.bug_compat_warn'), (b'session.auto_start', 'session.auto_start'), (b'safe_mode', 'Safe mode'), (b'suhosin.post.max_vars', 'Suhosin POST max vars'), (b'suhosin.get.max_vars', 'Suhosin GET max vars'), (b'suhosin.request.max_vars', 'Suhosin request max vars'), (b'suhosin.session.encrypt', 'suhosin.session.encrypt'), (b'suhosin.simulation', 'Suhosin simulation'), (b'suhosin.executor.include.whitelist', 'suhosin.executor.include.whitelist'), (b'upload_max_filesize', 'upload_max_filesize'), (b'post_max_size', 'zend_extension')])]),
            preserve_default=True,
        ),
    ]
