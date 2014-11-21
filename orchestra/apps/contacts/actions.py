from django.contrib import admin, messages
from django.core.mail import send_mass_mail
from django.shortcuts import render
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.utils import change_url

from .forms import SendEmailForm


class SendEmail(object):
    """ Form wizard for billing orders admin action """
    short_description = _("Send email")
    form = SendEmailForm
    template = 'admin/orchestra/generic_confirmation.html'
    __name__ = 'semd_email'
    
    def __call__(self, modeladmin, request, queryset):
        """ make this monster behave like a function """
        self.modeladmin = modeladmin
        self.queryset = queryset
        opts = modeladmin.model._meta
        app_label = opts.app_label
        self.context = {
            'action_name': _("Send email"),
            'action_value': self.__name__,
            'opts': opts,
            'app_label': app_label,
            'queryset': queryset,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return self.write_email(request)
    
    def write_email(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied
        form = self.form()
        if request.POST.get('post'):
            form = self.form(request.POST)
            if form.is_valid():
                options = {
                    'email_from': form.cleaned_data['email_from'],
                    'cc': form.cleaned_data['cc'],
                    'bcc': form.cleaned_data['bcc'],
                    'subject': form.cleaned_data['subject'],
                    'message': form.cleaned_data['message'],
                    
                }
                return self.confirm_email(request, **options)
        opts = self.modeladmin.model._meta
        app_label = opts.app_label
        self.context.update({
            'title': _("Send e-mail to contacts"),
            'content_title': "",
            'form': form,
            'submit_value': _("Continue"),
        })
        # Display confirmation page
        return render(request, self.template, self.context)
    
    def confirm_email(self, request, **options):
        num = len(self.queryset)
        email_from = options['email_from']
        bcc = options['bcc']
        to = options['cc']
        subject = options['subject']
        message = options['message']
        # The user has already confirmed
        if request.POST.get('post') == 'email_confirmation':
            for contact in self.queryset.all():
                to.append(contact.email)
            send_mass_mail(subject, message, email_from, to, bcc)
            msg = ungettext(
                _("Message has been sent to %s.") % str(contact),
                _("Message has been sent to %i contacts.") % num,
                num
            )
            self.modeladmin.message_user(request, msg)
            return None
        
        form = self.form(initial={
            'subject': subject,
            'message': message
        })
        self.context.update({
            'title': _("Are you sure?"),
            'content_message': _(
                "Are you sure you want to send the following message to the following contacts?"),
            'display_objects': ["%s (%s)" % (contact, contact.email) for contact in self.queryset],
            'form': form,
            'subject': subject,
            'message': message,
            'post_value': 'email_confirmation',
        })
        # Display the confirmation page
        return render(request, self.template, self.context)
