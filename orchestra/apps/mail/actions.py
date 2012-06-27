from django.contrib import messages
from django.db import transaction
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from models import VirtualDomain


@transaction.commit_on_success
def create_virtualdomain(name_modeladmin, request, names):
    success, fail = 0, 0
    for name in names:
        try: name.virtualdomain
        except VirtualDomain.DoesNotExist: 
            virtual_domain = VirtualDomain.objects.create(domain=name)
            representation = force_unicode(name)
            name_modeladmin.log_change(request, name, representation)
            success += 1
        else: fail += 1
    if fail: messages.add_message(request, messages.WARNING, _("(%s/%s) names are already virtual" % (fail, (success+fail))))
    if success: messages.add_message(request, messages.INFO, _("Virtual domain support for %s domains has been provided" % success))
create_virtualdomain.short_description = _("Enable Virtual Domain")


@transaction.commit_on_success
def delete_virtualdomain(name_modeladmin, request, names):
    success, fail = 0, 0
    for name in names:
        try: name.virtualdomain
        except VirtualDomain.DoesNotExist: fail +=1
        else:
            representation = force_unicode(name)
            name.virtualdomain.delete()
            name_modeladmin.log_change(request, name, representation)
            success += 1
    if fail: messages.add_message(request, messages.WARNING, _("(%s/%s) names has no related virtual domain" % (fail, (success+fail))))
    if success: messages.add_message(request, messages.INFO, _("Virtual domain support for %s domains has been revoked" % success))           
delete_virtualdomain.short_description = _("Disable Virtual Domain")
