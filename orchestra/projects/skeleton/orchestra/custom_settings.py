
# DNS
DEFAULT_PRIMARY_NS = 'ns1.pangea.org'
DEFAULT_HOSTMASTER_EMAIL = 'suport.pangea.org'
DEFAULT_DOMAIN_REGISTERS = [{'type':'NS', 'data': 'ns1.pangea.org.'},
                            {'type':'NS', 'data': 'ns2.pangea.org.'},
                            {'type':'NS', 'data': 'ns3.pangea.org.'},
                            {'type':'A', 'data': '192.168.0.103'},
                            {'type':'MX', 'data': '10 mail.pangea.org.'},
                            {'type':'MX', 'data': '20 mail2.pangea.org.'},
                            {'name':'www', 'type':'CNAME', 'data': 'web.pangea.org.'},]
EXTENSIONS = (('org', 'org'),
              ('net', 'net'),
              ('es', 'es'),
              ('cat', 'cat'),
              ('info', 'info'),)
DEFAULT_EXTENSION = 'org'
REGISTER_PROVIDER_CHOICES = (('', 'None'),
                             ('gandi', 'Gandi'),)
DEFAULT_REGISTER_PROVIDER = 'gandi'
DEFAULT_NAME_SERVERS = [{'hostname':'ns1.pangea.org', 'ip': ''},
                        {'hostname':'ns2.pangea.org', 'ip': ''},
                        {'hostname':'ns3.pangea.org', 'ip': ''},]

# Contacts
DEFAULT_LANGUAGE = 'ca'
LANGUAGE_CHOICES = (('ca', 'Catalan'),
                    ('es', 'Spanish'),
                    ('en', 'English'),)

# Web
DEFAULT_VIRTUAL_HOST_CUSTOM_DIRECTIVES = '\
Alias /webalizer /home/httpd/webalizer/{{ self.unique_ident }}\n\
ScriptAlias /cgi-bin/ /home/pangea/{{ self.fcgid.user }}/cgi-bin/'
VIRTUALHOST_IP_CHOICES = (('70.200.179.80', 'web.ucp.org'),)
VIRTUALHOST_IP_DEFAULT = '70.200.179.80'

# System_users
DEFAULT_SYSTEM_USER_BASE_HOMEDIR = '/home/pangea'
