# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('number', models.CharField(verbose_name='number', blank=True, unique=True, max_length=16)),
                ('type', models.CharField(verbose_name='type', choices=[('INVOICE', 'Invoice'), ('AMENDMENTINVOICE', 'Amendment invoice'), ('FEE', 'Fee'), ('AMENDMENTFEE', 'Amendment Fee'), ('PROFORMA', 'Pro forma')], max_length=16)),
                ('created_on', models.DateField(verbose_name='created on', auto_now_add=True)),
                ('closed_on', models.DateField(verbose_name='closed on', null=True, blank=True)),
                ('is_open', models.BooleanField(verbose_name='open', default=True)),
                ('is_sent', models.BooleanField(verbose_name='sent', default=False)),
                ('due_on', models.DateField(verbose_name='due on', null=True, blank=True)),
                ('updated_on', models.DateField(verbose_name='updated on', auto_now=True)),
                ('total', models.DecimalField(default=0, decimal_places=2, max_digits=12)),
                ('comments', models.TextField(verbose_name='comments', blank=True)),
                ('html', models.TextField(verbose_name='HTML', blank=True)),
                ('account', models.ForeignKey(verbose_name='account', related_name='bill', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='BillContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='name', blank=True, help_text='Account full name will be used when left blank.', max_length=256)),
                ('address', models.TextField(verbose_name='address')),
                ('city', models.CharField(verbose_name='city', default='Barcelona', max_length=128)),
                ('zipcode', models.CharField(verbose_name='zip code', validators=[django.core.validators.RegexValidator('^[0-9A-Z]{3,10}$', 'Enter a valid zipcode.')], max_length=10)),
                ('country', models.CharField(verbose_name='country', default='ES', choices=[('TR', 'Turkey'), ('BV', 'Bouvet Island'), ('EE', 'Estonia'), ('CO', 'Colombia'), ('MW', 'Malawi'), ('JM', 'Jamaica'), ('GF', 'French Guiana'), ('NR', 'Nauru'), ('DK', 'Denmark'), ('SY', 'Syrian Arab Republic'), ('PH', 'Philippines'), ('TF', 'French Southern Territories'), ('GH', 'Ghana'), ('AM', 'Armenia'), ('PY', 'Paraguay'), ('VE', 'Venezuela (Bolivarian Republic of)'), ('EG', 'Egypt'), ('CU', 'Cuba'), ('VI', 'Virgin Islands (U.S.)'), ('KN', 'Saint Kitts and Nevis'), ('RU', 'Russian Federation'), ('RO', 'Romania'), ('MD', 'Moldova (the Republic of)'), ('GB', 'United Kingdom of Great Britain and Northern Ireland'), ('JP', 'Japan'), ('OM', 'Oman'), ('AE', 'United Arab Emirates'), ('BM', 'Bermuda'), ('VG', 'Virgin Islands (British)'), ('CD', 'Congo (the Democratic Republic of the)'), ('GY', 'Guyana'), ('IQ', 'Iraq'), ('DJ', 'Djibouti'), ('MU', 'Mauritius'), ('UG', 'Uganda'), ('ID', 'Indonesia'), ('KP', "Korea (the Democratic People's Republic of)"), ('CA', 'Canada'), ('MS', 'Montserrat'), ('SA', 'Saudi Arabia'), ('SZ', 'Swaziland'), ('NZ', 'New Zealand'), ('TO', 'Tonga'), ('IM', 'Isle of Man'), ('AZ', 'Azerbaijan'), ('PG', 'Papua New Guinea'), ('LB', 'Lebanon'), ('PR', 'Puerto Rico'), ('HM', 'Heard Island and McDonald Islands'), ('GR', 'Greece'), ('CR', 'Costa Rica'), ('PA', 'Panama'), ('BG', 'Bulgaria'), ('SS', 'South Sudan'), ('PE', 'Peru'), ('BY', 'Belarus'), ('FK', 'Falkland Islands  [Malvinas]'), ('PF', 'French Polynesia'), ('MP', 'Northern Mariana Islands'), ('HN', 'Honduras'), ('SI', 'Slovenia'), ('GU', 'Guam'), ('PL', 'Poland'), ('CW', 'Curaçao'), ('BF', 'Burkina Faso'), ('PT', 'Portugal'), ('ZM', 'Zambia'), ('TZ', 'Tanzania, United Republic of'), ('WF', 'Wallis and Futuna'), ('DM', 'Dominica'), ('GT', 'Guatemala'), ('PS', 'Palestine, State of'), ('TN', 'Tunisia'), ('BE', 'Belgium'), ('SX', 'Sint Maarten (Dutch part)'), ('FJ', 'Fiji'), ('FO', 'Faroe Islands'), ('BH', 'Bahrain'), ('BL', 'Saint Barthélemy'), ('DE', 'Germany'), ('NU', 'Niue'), ('SV', 'El Salvador'), ('BS', 'Bahamas'), ('MK', 'Macedonia (the former Yugoslav Republic of)'), ('SL', 'Sierra Leone'), ('SN', 'Senegal'), ('EH', 'Western Sahara'), ('TD', 'Chad'), ('NA', 'Namibia'), ('FI', 'Finland'), ('GW', 'Guinea-Bissau'), ('MT', 'Malta'), ('KY', 'Cayman Islands'), ('UM', 'United States Minor Outlying Islands'), ('LC', 'Saint Lucia'), ('GD', 'Grenada'), ('GM', 'Gambia'), ('HU', 'Hungary'), ('DZ', 'Algeria'), ('JO', 'Jordan'), ('ZW', 'Zimbabwe'), ('CY', 'Cyprus'), ('GL', 'Greenland'), ('UY', 'Uruguay'), ('MA', 'Morocco'), ('GP', 'Guadeloupe'), ('MY', 'Malaysia'), ('FR', 'France'), ('RE', 'Réunion'), ('MV', 'Maldives'), ('MN', 'Mongolia'), ('MO', 'Macao'), ('AU', 'Australia'), ('CX', 'Christmas Island'), ('VN', 'Viet Nam'), ('AS', 'American Samoa'), ('TK', 'Tokelau'), ('GS', 'South Georgia and the South Sandwich Islands'), ('KG', 'Kyrgyzstan'), ('AO', 'Angola'), ('TV', 'Tuvalu'), ('NI', 'Nicaragua'), ('QA', 'Qatar'), ('LT', 'Lithuania'), ('VA', 'Holy See'), ('PK', 'Pakistan'), ('GQ', 'Equatorial Guinea'), ('RS', 'Serbia'), ('KR', 'Korea (the Republic of)'), ('ER', 'Eritrea'), ('KW', 'Kuwait'), ('IR', 'Iran (Islamic Republic of)'), ('SK', 'Slovakia'), ('SE', 'Sweden'), ('TL', 'Timor-Leste'), ('AG', 'Antigua and Barbuda'), ('SD', 'Sudan'), ('BR', 'Brazil'), ('TM', 'Turkmenistan'), ('AI', 'Anguilla'), ('SR', 'Suriname'), ('MX', 'Mexico'), ('GE', 'Georgia'), ('KE', 'Kenya'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('VC', 'Saint Vincent and the Grenadines'), ('MF', 'Saint Martin (French part)'), ('CC', 'Cocos (Keeling) Islands'), ('GI', 'Gibraltar'), ('ME', 'Montenegro'), ('MC', 'Monaco'), ('ZA', 'South Africa'), ('IS', 'Iceland'), ('KM', 'Comoros'), ('KI', 'Kiribati'), ('HT', 'Haiti'), ('BO', 'Bolivia (Plurinational State of)'), ('CH', 'Switzerland'), ('MR', 'Mauritania'), ('GA', 'Gabon'), ('KZ', 'Kazakhstan'), ('BN', 'Brunei Darussalam'), ('YT', 'Mayotte'), ('IL', 'Israel'), ('YE', 'Yemen'), ('SO', 'Somalia'), ('TJ', 'Tajikistan'), ('CZ', 'Czech Republic'), ('SC', 'Seychelles'), ('RW', 'Rwanda'), ('SG', 'Singapore'), ('SB', 'Solomon Islands'), ('AX', 'Åland Islands'), ('PN', 'Pitcairn'), ('NF', 'Norfolk Island'), ('AR', 'Argentina'), ('BD', 'Bangladesh'), ('GN', 'Guinea'), ('AF', 'Afghanistan'), ('VU', 'Vanuatu'), ('NL', 'Netherlands'), ('LA', "Lao People's Democratic Republic"), ('BW', 'Botswana'), ('BA', 'Bosnia and Herzegovina'), ('ST', 'Sao Tome and Principe'), ('GG', 'Guernsey'), ('BJ', 'Benin'), ('IT', 'Italy'), ('EC', 'Ecuador'), ('LY', 'Libya'), ('FM', 'Micronesia (Federated States of)'), ('AW', 'Aruba'), ('MG', 'Madagascar'), ('UZ', 'Uzbekistan'), ('AD', 'Andorra'), ('HK', 'Hong Kong'), ('PW', 'Palau'), ('PM', 'Saint Pierre and Miquelon'), ('AT', 'Austria'), ('LK', 'Sri Lanka'), ('LR', 'Liberia'), ('ET', 'Ethiopia'), ('US', 'United States of America'), ('CV', 'Cabo Verde'), ('SJ', 'Svalbard and Jan Mayen'), ('IO', 'British Indian Ocean Territory'), ('BB', 'Barbados'), ('CK', 'Cook Islands'), ('NC', 'New Caledonia'), ('BI', 'Burundi'), ('TT', 'Trinidad and Tobago'), ('CG', 'Congo'), ('CM', 'Cameroon'), ('KH', 'Cambodia'), ('TG', 'Togo'), ('CL', 'Chile'), ('CF', 'Central African Republic'), ('IN', 'India'), ('NP', 'Nepal'), ('TC', 'Turks and Caicos Islands'), ('MM', 'Myanmar'), ('MQ', 'Martinique'), ('LI', 'Liechtenstein'), ('JE', 'Jersey'), ('SM', 'San Marino'), ('MZ', 'Mozambique'), ('UA', 'Ukraine'), ('LV', 'Latvia'), ('MH', 'Marshall Islands'), ('AL', 'Albania'), ('TW', 'Taiwan (Province of China)'), ('DO', 'Dominican Republic'), ('ES', 'Spain'), ('IE', 'Ireland'), ('WS', 'Samoa'), ('HR', 'Croatia'), ('AQ', 'Antarctica'), ('ML', 'Mali'), ('NE', 'Niger'), ('BZ', 'Belize'), ('TH', 'Thailand'), ('CN', 'China'), ('BQ', 'Bonaire, Sint Eustatius and Saba'), ('NG', 'Nigeria'), ('LU', 'Luxembourg'), ('BT', 'Bhutan'), ('NO', 'Norway'), ('CI', "Côte d'Ivoire"), ('LS', 'Lesotho')], max_length=20)),
                ('vat', models.CharField(verbose_name='VAT number', max_length=64)),
                ('account', models.OneToOneField(verbose_name='account', related_name='billcontact', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BillLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('description', models.CharField(verbose_name='description', max_length=256)),
                ('rate', models.DecimalField(verbose_name='rate', decimal_places=2, max_digits=12, null=True, blank=True)),
                ('quantity', models.DecimalField(verbose_name='quantity', decimal_places=2, max_digits=12)),
                ('verbose_quantity', models.CharField(verbose_name='Verbose quantity', max_length=16)),
                ('subtotal', models.DecimalField(verbose_name='subtotal', decimal_places=2, max_digits=12)),
                ('tax', models.DecimalField(verbose_name='tax', decimal_places=2, max_digits=2)),
                ('order_billed_on', models.DateField(verbose_name='order billed', null=True, blank=True)),
                ('order_billed_until', models.DateField(verbose_name='order billed until', null=True, blank=True)),
                ('created_on', models.DateField(verbose_name='created', auto_now_add=True)),
                ('amended_line', models.ForeignKey(verbose_name='amended line', blank=True, null=True, related_name='amendment_lines', to='bills.BillLine')),
                ('bill', models.ForeignKey(verbose_name='bill', related_name='lines', to='bills.Bill')),
                ('order', models.ForeignKey(help_text='Informative link back to the order', blank=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.Order', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BillSubline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('description', models.CharField(verbose_name='description', max_length=256)),
                ('total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('type', models.CharField(verbose_name='type', default='OTHER', choices=[('VOLUME', 'Volume'), ('COMPENSATION', 'Compensation'), ('OTHER', 'Other')], max_length=16)),
                ('line', models.ForeignKey(verbose_name='bill line', related_name='sublines', to='bills.BillLine')),
            ],
        ),
        migrations.CreateModel(
            name='AmendmentFee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='AmendmentInvoice',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='ProForma',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
    ]
