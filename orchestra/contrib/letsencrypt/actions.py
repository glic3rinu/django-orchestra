from django.contrib import messages, admin
from django.template.response import TemplateResponse
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.contrib.orchestration import Operation, helpers

from .helpers import is_valid_domain, read_live_lineages, configure_cert
from .forms import LetsEncryptForm


def letsencrypt(modeladmin, request, queryset):
    wildcards = set()
    domains = set()
    queryset = queryset.prefetch_related('domains')
    for website in queryset:
        for domain in website.domains.all():
            if domain.name.startswith('*.'):
                wildcards.add(domain.name)
            else:
                domains.add(domain.name)
    form = LetsEncryptForm(domains, wildcards, initial={'domains': '\n'.join(domains)})
    action_value = 'letsencrypt'
    if request.POST.get('post') == 'generic_confirmation':
        form = LetsEncryptForm(domains, wildcards, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            domains = set(cleaned_data['domains'])
            operations = []
            for website in queryset:
                website_domains = [d.name for d in website.domains.all()]
                encrypt_domains = set()
                for domain in domains:
                    if is_valid_domain(domain, website_domains, wildcards):
                        encrypt_domains.add(domain)
                website.encrypt_domains = encrypt_domains
                operations.extend(Operation.create_for_action(website, 'encrypt'))
                modeladmin.log_change(request, request.user, _("Encrypted!"))
            if not operations:
                messages.error(request, _("No backend operation has been executed."))
            else:
                logs = Operation.execute(operations)
                helpers.message_user(request, logs)
                live_lineages = read_live_lineages(logs)
                errors = 0
                successes = 0
                no_https = 0
                for website in queryset:
                    try:
                        configure_cert(website, live_lineages)
                    except LookupError:
                        errors += 1
                        messages.error(request, _("No lineage found for website %s") % website.name)
                    else:
                        if website.protocol == website.HTTP:
                            no_https += 1
                        website.save(update_fields=('name',))
                    successes += 1
                context = {
                    'name': website.name,
                    'errors': errors,
                    'successes': successes,
                    'no_https': no_https
                }
                if errors:
                    msg = ungettext(
                        _("No lineages found for websites {name}."),
                        _("No lineages found for {errors} websites."),
                        errors)
                    messages.error(request, msg % context)
                if successes:
                    msg = ungettext(
                        _("{name} website has successfully been encrypted."),
                        _("{successes} websites have been successfully encrypted."),
                        successes)
                    messages.success(request, msg.format(**context))
                if no_https:
                    msg = ungettext(
                        _("{name} website does not have HTTPS protocol enabled."),
                        _("{no_https} websites do not have HTTPS protocol enabled."),
                        no_https)
                    messages.warning(request, msg.format(**context))
                return
    opts = modeladmin.model._meta
    app_label = opts.app_label
    context = {
        'title': _("Let's encrypt!"),
        'action_name': _("Encrypt"),
        'action_value': action_value,
        'queryset': queryset,
        'opts': opts,
        'obj': website if len(queryset) == 1 else None,
        'app_label': app_label,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'form': form,
    }
    return TemplateResponse(request, 'admin/orchestra/generic_confirmation.html',
        context, current_app=modeladmin.admin_site.name)
letsencrypt.short_description = "Let's encrypt!"
