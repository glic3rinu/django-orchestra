import copy
from functools import partial

from .models import Domain, Record


def domain_for_validation(instance, records):
    """
    Since the new data is not yet on the database, we update it on the fly,
    so when validation calls render_zone() it will use the new provided data
    """
    domain = copy.copy(instance)
    def get_records():
        for data in records:
            yield Record(type=data['type'], value=data['value'])
    domain.get_records = get_records
    
    if not domain.pk:
        # top domain lookup for new domains
        domain.top = domain.get_top()
    if domain.top:
        # is a subdomain
        subdomains = [sub for sub in domain.top.subdomains.all() if sub.pk != domain.pk]
        domain.top.get_subdomains = lambda: subdomains + [domain]
    elif not domain.pk:
        # is a new top domain
        subdomains = []
        for subdomain in Domain.objects.filter(name__endswith='.%s' % domain.name):
            subdomain.top = domain
            subdomains.append(subdomain)
        domain.get_subdomains = lambda: subdomains
    return domain
