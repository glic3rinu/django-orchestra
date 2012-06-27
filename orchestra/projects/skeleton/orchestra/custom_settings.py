
# DNS
DNS_DEFAULT_PRIMARY_NS = 'ns1.pangea.org'
DNS_DEFAULT_HOSTMASTER_EMAIL = 'suport.pangea.org'
DNS_DEFAULT_DOMAIN_REGISTERS = [{'type':'NS', 'data': 'ns1.pangea.org.'},
                                {'type':'NS', 'data': 'ns2.pangea.org.'},
                                {'type':'NS', 'data': 'ns3.pangea.org.'},
                                {'type':'A', 'data': '192.168.0.103'},
                                {'type':'MX', 'data': '10 mail.pangea.org.'},
                                {'type':'MX', 'data': '20 mail2.pangea.org.'},
                                {'name':'www', 'type':'CNAME', 'data': 'web.pangea.org.'},]
DNS_EXTENSIONS = (('org', 'org'),
                  ('net', 'net'),
                  ('es', 'es'),
                  ('cat', 'cat'),
                  ('info', 'info'),)
DNS_DEFAULT_EXTENSION = 'org'
DNS_REGISTER_PROVIDER_CHOICES = (('', 'None'),
                                 ('gandi', 'Gandi'),)
DNS_DEFAULT_REGISTER_PROVIDER = 'gandi'
DNS_DEFAULT_NAME_SERVERS = [{'hostname':'ns1.pangea.org', 'ip': ''},
                            {'hostname':'ns2.pangea.org', 'ip': ''},
                            {'hostname':'ns3.pangea.org', 'ip': ''},]

# Contacts
CONTACTS_DEFAULT_LANGUAGE = 'ca'
CONTACTS_LANGUAGE_CHOICES = (('ca', 'Catalan'),
                             ('es', 'Spanish'),
                             ('en', 'English'),)

# Web
WEB_DEFAULT_VIRTUAL_HOST_CUSTOM_DIRECTIVES = '\
Alias /webalizer /home/httpd/webalizer/{{ self.unique_ident }}\n\
ScriptAlias /cgi-bin/ /home/pangea/{{ self.fcgid.user }}/cgi-bin/'
WEB_VIRTUALHOST_IP_CHOICES = (('70.200.179.80', 'web.ucp.org'),)
WEB_VIRTUALHOST_IP_DEFAULT = '70.200.179.80'

# System_users
SYSTEM_USERS_DEFAULT_BASE_HOMEDIR = '/home/pangea'

# Billing 
BILLING_INVOICE_ID_PREFIX = 'F'
BILLING_AMENDMENTINVOICE_ID_PREFIX = 'RF'
BILLING_FEE_ID_PREFIX = 'Q'
BILLING_AMENDMENTFEE_ID_PREFIX = 'RQ'
BILLING_BUDGET_ID_PREFIX = 'BU'
