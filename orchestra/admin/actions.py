from functools import partial

from django.contrib import admin
from django.core.mail import send_mass_mail
from django.shortcuts import render
from django.utils.translation import ungettext, ugettext_lazy as _

from .. import settings

from .decorators import action_with_confirmation
from .forms import SendEmailForm


class SendEmail(object):
    """ Form wizard for billing orders admin action """
    short_description = _("Send email")
    form = SendEmailForm
    template = 'admin/orchestra/generic_confirmation.html'
    default_from = settings.ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL
    __name__ = 'semd_email'
    
    def __call__(self, modeladmin, request, queryset):
        """ make this monster behave like a function """
        self.modeladmin = modeladmin
        self.queryset = queryset
        self.opts = modeladmin.model._meta
        app_label = self.opts.app_label
        self.context = {
            'action_name': _("Send email"),
            'action_value': self.__name__,
            'opts': self.opts,
            'app_label': app_label,
            'queryset': queryset,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return self.write_email(request)
    
    def write_email(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied
        initial={
            'email_from': self.default_from,
            'to': ' '.join(self.get_email_addresses())
        }
        form = self.form(initial=initial)
        if request.POST.get('post'):
            form = self.form(request.POST, initial=initial)
            if form.is_valid():
                options = {
                    'email_from': form.cleaned_data['email_from'],
                    'extra_to': form.cleaned_data['extra_to'],
                    'subject': form.cleaned_data['subject'],
                    'message': form.cleaned_data['message'],
                    
                }
                return self.confirm_email(request, **options)
        self.context.update({
            'title': _("Send e-mail to %s") % self.opts.verbose_name_plural,
            'content_title': "",
            'form': form,
            'submit_value': _("Continue"),
        })
        # Display confirmation page
        return render(request, self.template, self.context)
    
    def get_email_addresses(self):
        return self.queryset.values_list('email', flat=True)
    
    def confirm_email(self, request, **options):
        email_from = options['email_from']
        extra_to = options['extra_to']
        subject = options['subject']
        message = options['message']
        # The user has already confirmed
        if request.POST.get('post') == 'email_confirmation':
            emails = []
            num = 0
            for email in self.get_email_addresses():
                emails.append((subject, message, email_from, [email]))
                num += 1
            if extra_to:
                emails.append((subject, message, email_from, extra_to))
            send_mass_mail(emails, fail_silently=False)
            msg = ungettext(
                _("Message has been sent to one %s.") % self.opts.verbose_name_plural,
                _("Message has been sent to %i %s.") % (num, self.opts.verbose_name_plural),
                num
            )
            self.modeladmin.message_user(request, msg)
            return None
        
        form = self.form(initial={
            'email_from': email_from,
            'extra_to': ', '.join(extra_to),
            'subject': subject,
            'message': message
        })
        self.context.update({
            'title': _("Are you sure?"),
            'content_message': _(
                "Are you sure you want to send the following message to the following %s?"
            ) % self.opts.verbose_name_plural,
            'display_objects': ["%s (%s)" % (contact, email) for contact, email in zip(self.queryset, self.get_email_addresses())],
            'form': form,
            'subject': subject,
            'message': message,
            'post_value': 'email_confirmation',
        })
        # Display the confirmation page
        return render(request, self.template, self.context)


def base_disable(modeladmin, request, queryset, disable=True):
    num = 0
    action_name = _("disabled") if disable else _("enabled")
    for obj in queryset:
        obj.disable() if disable else obj.enable()
        modeladmin.log_change(request, obj, action_name.capitalize())
        num += 1
    opts = modeladmin.model._meta
    context = {
        'action_name': action_name,
        'verbose_name': opts.verbose_name,
        'verbose_name_plural': opts.verbose_name_plural,
        'num': num
    }
    msg = ungettext(
        _("Selected %(verbose_name)s and related services has been %(action_name)s.") % context,
        _("%(num)s selected %(verbose_name_plural)s and related services have been %(action_name)s.") % context,
        num)
    modeladmin.message_user(request, msg)


@action_with_confirmation()
def disable(modeladmin, request, queryset):
    return base_disable(modeladmin, request, queryset)
disable.url_name = 'disable'
disable.short_description = _("Disable")


@action_with_confirmation()
def enable(modeladmin, request, queryset):
    return base_disable(modeladmin, request, queryset, disable=False)
enable.url_name = 'enable'
enable.short_description = _("Enable")
