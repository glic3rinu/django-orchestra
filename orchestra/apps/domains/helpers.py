import copy

from .models import Domain, Record


def domain_for_validation(instance, records):
    """ Create a fake zone in order to generate the whole zone file and check it """
    domain = copy.copy(instance)
    if not domain.pk:
        domain.top = domain.get_top()
    def get_records():
        for data in records:
            yield Record(type=data['type'], value=data['value'])
    domain.get_records = get_records
    if domain.top:
        subdomains = domain.get_topsubdomains().exclude(pk=instance.pk)
        domain.top.get_subdomains = lambda: list(subdomains) + [domain]
    elif not domain.pk:
        subdomains = []
        for subdomain in Domain.objects.filter(name__endswith=domain.name):
            subdomain.top = domain
            subdomains.append(subdomain)
        domain.get_subdomains = lambda: subdomains
    return domain
