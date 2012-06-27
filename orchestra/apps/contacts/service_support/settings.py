from django.conf import settings

ugettext = lambda s: s

# Provide Contract support
CONTRACTED_MODELS = (
    'django.contrib.auth.models.User',
    'dns.models.Name', 'dns.models.Zone',
    'system_users.models.SystemGroup', 
    'web.models.VirtualHost',
    'mail.models.VirtualAliase',
    'lists.models.List',
    'vps.models.VPS',
    'jobs.models.Job',
    'databases.models.Database', 'databases.models.DBUser',
)
