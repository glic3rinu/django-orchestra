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
    
    def get_subdomains(replace=None, make_top=False):
        for subdomain in Domain.objects.filter(name__endswith='.%s' % domain.name):
            if replace == subdomain.pk:
                # domain is a subdomain, yield our copy
                yield domain
            else:
                if make_top:
                    subdomain.top = domain
                yield subdomain
    
    if not domain.pk:
        # top domain lookup for new domains
        domain.top = domain.get_top()
    if domain.top:
        # is a subdomains
        domain.top.get_subdomains = partial(get_subdomains, replace=domain.pk)
    elif not domain.pk:
        # is top domain
        domain.get_subdomains = partial(get_subdomains, make_top=True)
    return domain
