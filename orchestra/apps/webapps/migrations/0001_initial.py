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
            name='WebApp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='name', validators=[orchestra.core.validators.validate_name])),
                ('type', models.CharField(max_length=32, verbose_name='type', choices=[(b'dokuwiki-mu', b'DokuWiki (SaaS)'), (b'drupal-mu', b'Drupdal (SaaS)'), (b'php4-fcgi', b'PHP 4 FCGI'), (b'php5.2-fcgi', b'PHP 5.2 FCGI'), (b'php5.5-fpm', b'PHP 5.5 FPM'), (b'static', b'Static'), (b'symlink', b'Symbolic link'), (b'webalizer', b'Webalizer'), (b'wordpress', b'WordPress'), (b'wordpress-mu', b'WordPress (SaaS)')])),
                ('account', models.ForeignKey(related_name='webapps', verbose_name='Account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Web App',
                'verbose_name_plural': 'Web Apps',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WebAppOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='name', choices=[(b'PHP-allow_url_fopen', 'PHP - allow_url_fopen'), (b'PHP-allow_url_include', 'PHP - Allow URL include'), (b'PHP-auto_append_file', 'PHP - Auto append file'), (b'PHP-auto_prepend_file', 'PHP - Auto prepend file'), (b'PHP-date.timezone', 'PHP - date.timezone'), (b'PHP-default_socket_timeout', 'PHP - Default socket timeout'), (b'PHP-display_errors', 'PHP - Display errors'), (b'PHP-extension', 'PHP - Extension'), (b'PHP-magic_quotes_gpc', 'PHP - Magic quotes GPC'), (b'PHP-magic_quotes_runtime', 'PHP - Magic quotes runtime'), (b'PHP-magic_quotes_sybase', 'PHP - Magic quotes sybase'), (b'PHP-max_execution_time', 'PHP - Max execution time'), (b'PHP-max_input_time', 'PHP - Max input time'), (b'PHP-max_input_vars', 'PHP - Max input vars'), (b'PHP-memory_limit', 'PHP - Memory limit'), (b'PHP-mysql.connect_timeout', 'PHP - Mysql connect timeout'), (b'PHP-output_buffering', 'PHP - output_buffering'), (b'PHP-post_max_size', 'PHP - Post max size'), (b'PHP-register_globals', 'PHP - Register globals'), (b'PHP-safe_mode', 'PHP - Safe mode'), (b'PHP-sendmail_path', 'PHP - sendmail_path'), (b'PHP-session.auto_start', 'PHP - session.auto_start'), (b'PHP-session.bug_compat_warn', 'PHP - session.bug_compat_warn'), (b'PHP-suhosin.executor.include.whitelist', 'PHP - suhosin.executor.include.whitelist'), (b'PHP-suhosin.get.max_vars', 'PHP - Suhosin GET max vars'), (b'PHP-suhosin.post.max_vars', 'PHP - Suhosin POST max vars'), (b'PHP-suhosin.request.max_vars', 'PHP - Suhosin request max vars'), (b'PHP-suhosin.session.encrypt', 'PHP - suhosin.session.encrypt'), (b'PHP-suhosin.simulation', 'PHP - Suhosin simulation'), (b'PHP-upload_max_filesize', 'PHP - upload_max_filesize'), (b'PHP-zend_extension', 'PHP - zend_extension'), (b'php-enabled_functions', 'PHP - Enabled functions'), (b'processes', 'Number of processes'), (b'public-root', 'Public root'), (b'timeout', 'Process timeout')])),
                ('value', models.CharField(max_length=256, verbose_name='value')),
                ('webapp', models.ForeignKey(related_name='options', verbose_name='Web application', to='webapps.WebApp')),
            ],
            options={
                'verbose_name': 'option',
                'verbose_name_plural': 'options',
            },
            bases=(models.Model,),
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
