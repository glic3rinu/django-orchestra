from django.conf import settings

ugettext = lambda s: s

DNS_EXTENSIONS = getattr(settings, 'DNS_EXTENSIONS', (('com', 'com'),
                                                      ('org', 'org'),
                                                      ('edu', 'edu'),
                                                      ('gov', 'gov'),
                                                      ('uk', 'uk'),
                                                      ('net', 'net'),
                                                      ('ca', 'ca'),
                                                      ('de', 'de'),
                                                      ('jp', 'jp'),
                                                      ('fr', 'fr'),
                                                      ('au', 'au'),
                                                      ('us', 'us'),
                                                      ('ru', 'ru'),
                                                      ('ch', 'ch'),
                                                      ('it', 'it'),
                                                      ('nl', 'nl'),
                                                      ('se', 'se'),
                                                      ('no', 'no'),
                                                      ('es', 'es'),))

DNS_DEFAULT_EXTENSION = getattr(settings, 'DNS_DEFAULT_EXTENSION', 'org')

DNS_REGISTER_PROVIDER_CHOICES = getattr(settings, 'DNS_REGISTER_PROVIDER_CHOICES', (('', 'None'),
                                                                            ('gandi', 'Gandi'),))

DNS_DEFAULT_REGISTER_PROVIDER = getattr(settings, 'DNS_DEFAULT_REGISTER_PROVIDER', 'gandi')

DNS_DEFAULT_NAME_SERVERS = getattr(settings, 'DNS_DEFAULT_NAME_SERVERS', [{'hostname':'ns1.orchestra.org', 'ip': ''},])

