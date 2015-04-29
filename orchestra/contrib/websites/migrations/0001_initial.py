# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('webapps', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domains', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('path', models.CharField(verbose_name='path', validators=[orchestra.core.validators.validate_url_path], blank=True, max_length=256)),
                ('webapp', models.ForeignKey(verbose_name='web application', to='webapps.WebApp')),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', validators=[orchestra.core.validators.validate_name], max_length=128)),
                ('protocol', models.CharField(verbose_name='protocol', default='http', choices=[('http', 'HTTP'), ('https', 'HTTPS'), ('http/https', 'HTTP and HTTPS'), ('https-only', 'HTTPS only')], help_text='Select the protocol(s) for this website<br><tt>HTTPS only</tt> performs a redirection from <tt>http</tt> to <tt>https</tt>.', max_length=16)),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('account', models.ForeignKey(verbose_name='Account', related_name='websites', to=settings.AUTH_USER_MODEL)),
                ('contents', models.ManyToManyField(to='webapps.WebApp', through='websites.Content')),
                ('domains', models.ManyToManyField(verbose_name='domains', to='domains.Domain', related_name='websites')),
            ],
        ),
        migrations.CreateModel(
            name='WebsiteDirective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', choices=[(None, '-------'), ('ModSecurity', [('sec-rule-remove', 'SecRuleRemoveById'), ('sec-engine', 'SecRuleEngine Off')]), ('SSL', [('ssl-ca', 'SSL CA'), ('ssl-cert', 'SSL cert'), ('ssl-key', 'SSL key')]), ('HTTPD', [('redirect', 'Redirection'), ('proxy', 'Proxy'), ('error-document', 'ErrorDocumentRoot')]), ('SaaS', [('wordpress-saas', 'WordPress SaaS'), ('dokuwiki-saas', 'DokuWiki SaaS'), ('drupal-saas', 'Drupdal SaaS')])], max_length=128)),
                ('value', models.CharField(verbose_name='value', max_length=256)),
                ('website', models.ForeignKey(verbose_name='web site', related_name='directives', to='websites.Website')),
            ],
        ),
        migrations.AddField(
            model_name='content',
            name='website',
            field=models.ForeignKey(verbose_name='web site', to='websites.Website'),
        ),
        migrations.AlterUniqueTogether(
            name='website',
            unique_together=set([('name', 'account')]),
        ),
        migrations.AlterUniqueTogether(
            name='content',
            unique_together=set([('website', 'path')]),
        ),
    ]
