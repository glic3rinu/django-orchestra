import copy

from .models import Domain, Record


def domain_for_validation(instance, records):
    """
    Since the new data is not yet on the database, we update it on the fly,
    so when validation calls render_zone() it will use the new provided data
    """
    domain = copy.copy(instance)
    def get_declared_records(records=records):
        for data in records:
            yield Record(type=data['type'], value=data['value'])
    domain.get_declared_records = get_declared_records
    
    if not domain.pk:
        # top domain lookup for new domains
        domain.top = domain.get_parent(top=True)
    if domain.top:
        # is a subdomain
        subdomains = domain.top.subdomains.select_related('top').prefetch_related('records').all()
        subdomains = [sub for sub in subdomains if sub.pk != domain.pk]
        domain.top.get_subdomains = lambda: subdomains + [domain]
    elif not domain.pk:
        # is a new top domain
        subdomains = []
        for subdomain in Domain.objects.filter(name__endswith='.%s' % domain.name):
            subdomain.top = domain
            subdomains.append(subdomain)
        domain.get_subdomains = lambda: subdomains
    return domain
