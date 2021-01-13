from collections import defaultdict
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.websites.models import Website, WebsiteDirective, Content
from orchestra.contrib.websites.validators import validate_domain_protocol
from orchestra.contrib.orchestration.models import Server
from orchestra.utils.python import AttrDict


def full_clean(obj, exclude=None):
    try:
        obj.full_clean(exclude=exclude)
    except ValidationError as e:
        raise ValidationError({
            'custom_url': _("Error validating related %s: %s") % (type(obj).__name__, e),
        })


def clean_custom_url(saas):
    instance = saas.instance
    instance.custom_url = instance.custom_url.strip()
    url = urlparse(instance.custom_url)
    if not url.path:
        instance.custom_url += '/'
        url = urlparse(instance.custom_url)
    try:
        protocol, valid_protocols = saas.PROTOCOL_MAP[url.scheme]
    except KeyError:
        raise ValidationError({
            'custom_url': _("%s scheme not supported (http/https)") % url.scheme,
        })
    account = instance.account
    # get or create website
    try:
        website = Website.objects.get(
            protocol__in=valid_protocols,
            domains__name=url.netloc,
            account=account,
        )
    except Website.DoesNotExist:
        # get or create domain
        Domain = Website.domains.field.rel.to
        try:
            domain = Domain.objects.get(name=url.netloc)
        except Domain.DoesNotExist:
            raise ValidationError({
                'custom_url': _("Domain %s does not exist.") % url.netloc,
            })
        if domain.account != account:
            raise ValidationError({
                'custom_url': _("Domain %s does not belong to account %s, it's from %s.") % 
                    (url.netloc, account, domain.account),
            })
        # Create new website for custom_url
        # Changed by daniel: hardcode target_server to web.pangea.lan, consider putting it into settings.py
        tgt_server = Server.objects.get(name='web.pangea.lan')
        website = Website(name=url.netloc, protocol=protocol, account=account, target_server=tgt_server)
        full_clean(website)
        try:
            validate_domain_protocol(website, domain, protocol)
        except ValidationError as e:
            raise ValidationError({
                'custom_url': _("Error validating related %s: %s") % (type(website).__name__, e),
            })
    # get or create directive
    try:
        directive = website.directives.get(name=saas.get_directive_name())
    except WebsiteDirective.DoesNotExist:
        directive = WebsiteDirective(name=saas.get_directive_name(), value=url.path)
    if not directive.pk or directive.value != url.path:
        directive.value = url.path
        if website.pk:
            directive.website = website
            full_clean(directive)
            # Adaptation of orchestra.websites.forms.WebsiteDirectiveInlineFormSet.clean()
            locations = set(
                Content.objects.filter(website=website).values_list('path', flat=True)
            )
            values = defaultdict(list)
            directives = WebsiteDirective.objects.filter(website=website)
            for wdirective in directives.exclude(pk=directive.pk):
                fdirective = AttrDict({
                    'name': wdirective.name,
                    'value': wdirective.value
                })
                try:
                    wdirective.directive_instance.validate_uniqueness(fdirective, values, locations)
                except ValidationError as err:
                    raise ValidationError({
                        'custom_url': _("Another directive with this URL path exists (%s)." % err)
                    })
        else:
            full_clean(directive, exclude=('website',))
    return directive


def create_or_update_directive(saas):
    instance = saas.instance
    url = urlparse(instance.custom_url)
    protocol, valid_protocols = saas.PROTOCOL_MAP[url.scheme]
    account = instance.account
    # get or create website
    try:
        website = Website.objects.get(
            protocol__in=valid_protocols,
            domains__name=url.netloc,
            account=account,
        )
    except Website.DoesNotExist:
        Domain = Website.domains.field.rel.to
        domain = Domain.objects.get(name=url.netloc)
        # Create new website for custom_url
        tgt_server = Server.objects.get(name='web.pangea.lan')
        website = Website(name=url.netloc, protocol=protocol, account=account, target_server=tgt_server)
        website.save()
        website.domains.add(domain)
    # get or create directive
    try:
        directive = website.directives.get(name=saas.get_directive_name())
    except WebsiteDirective.DoesNotExist:
        directive = WebsiteDirective(name=saas.get_directive_name(), value=url.path)
    if not directive.pk or directive.value != url.path:
        directive.value = url.path
        directive.website = website
        directive.save()
    return directive


def update_directive(saas):
    saas.instance.custom_url = saas.instance.custom_url.strip()
    url = urlparse(saas.instance.custom_url)
