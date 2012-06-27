# DNS
DEFAULT_PRIMARY_NS = getattr(settings, 'DEFAULT_PRIMARY_NS', 'ns1.pangea.org')
DEFAULT_HOSTMASTER_EMAIL = getattr(settings, 'DEFAULT_HOSTMASTER_EMAIL', 'suport.pangea.org')
DEFAULT_DOMAIN_REGISTERS = getattr(settings, 'DEFAULT_DOMAIN_REGISTERS', [{'type':'NS', 'data': 'ns1.pangea.org.'},
                                                                          {'type':'NS', 'data': 'ns2.pangea.org.'},
                                                                          {'type':'NS', 'data': 'ns3.pangea.org.'},
                                                                          {'type':'A', 'data': '192.168.0.103'},
                                                                          {'type':'MX', 'data': '10 mail.pangea.org.'},
                                                                          {'type':'MX', 'data': '20 mail2.pangea.org.'},
                                                                          {'name':'www', 'type':'CNAME', 'data': 'web.pangea.org.'},])
EXTENSIONS = getattr(settings, 'EXTENSIONS', (('org', 'org'),
                                              ('net', 'net'),
                                              ('es', 'es'),
                                              ('cat', 'cat'),
                                              ('info', 'info'),))
DEFAULT_EXTENSION = getattr(settings, 'DEFAULT_EXTENSION', 'org')
REGISTER_PROVIDER_CHOICES = getattr(settings, 'REGISTER_PROVIDER_CHOICES', (('', 'None'),
                                                                            ('gandi', 'Gandi'),))
DEFAULT_REGISTER_PROVIDER = getattr(settings, 'DEFAULT_REGISTER_PROVIDER', 'gandi')
DEFAULT_NAME_SERVERS = getattr(settings, 'DEFAULT_NAME_SERVERS', [{'hostname':'ns1.pangea.org', 'ip': ''},
                                                                  {'hostname':'ns2.pangea.org', 'ip': ''},
                                                                  {'hostname':'ns3.pangea.org', 'ip': ''},])

# Contacts
DEFAULT_LANGUAGE = getattr(settings, 'DEFAULT_LANGUAGE', 'ca')
LANGUAGE_CHOICES = getattr(settings, 'LANGUAGE_CHOICES', (('ca', ugettext('Catalan')),
                                                          ('es', ugettext('Spanish')),
                                                          ('en', ugettext('English')),))
