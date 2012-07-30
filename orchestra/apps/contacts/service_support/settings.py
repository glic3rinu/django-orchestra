from django.conf import settings

ugettext = lambda s: s

# Provide Contract support to:
CONTACTS_CONTRACTED_MODELS = getattr(settings, 'CONTACTS_CONTRACTED_MODELS', (
            'django.contrib.auth.models.User',
            'dns.names.models.Name', 'dns.zones.models.Zone',
            'system_users.models.SystemGroup', 
            'web.models.VirtualHost',
            'mail.models.VirtualAliase',
            'lists.models.List',
            'vps.models.VPS',
            'human_tasks.models.HumanTask',
            'databases.models.Database', 'databases.models.DBUser',))
