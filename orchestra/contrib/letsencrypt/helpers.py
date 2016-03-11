import os


def is_valid_domain(domain, existing, wildcards):
    if domain in existing:
        return True
    for wildcard in wildcards:
        if domain.startswith(wildcard.lstrip('*')) and domain.count('.') == wildcard.count('.'):
            return True
    return False


def read_live_lineages(logs):
    live_lineages = {}
    for log in logs:
        reading = False
        for line in log.stdout.splitlines():
            line = line.strip()
            if line == '</live-lineages>':
                break
            if reading:
                live_lineages[line.split('/')[-1]] = line
            elif line == '<live-lineages>':
                reading = True
    return live_lineages


def configure_cert(website, live_lineages):
    for domain in website.domains.all():
        try:
            path = live_lineages[domain.name]
        except KeyError:
            pass
        else:
            maps = (
                ('ssl-ca', os.path.join(path, 'chain.pem')),
                ('ssl-cert', os.path.join(path, 'cert.pem')),
                ('ssl-key', os.path.join(path, 'privkey.pem')),
            )
            for directive, path in maps:
                try:
                    directive = website.directives.get(name=directive)
                except website.directives.model.DoesNotExist:
                    directive = website.directives.model(name=directive, website=website)
                directive.value = path
                directive.save()
            return
    raise LookupError("Lineage not found")
