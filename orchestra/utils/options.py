import sys
import urlparse

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import Context


def send_email_template(template, context, to, email_from=None, html=None):
    """
    Renders an email template with this format:
        {% if subject %}Subject{% endif %}
        {% if message %}Email body{% endif %}

    context can be a dictionary or a template.Context instance
    """

    if isinstance(context, dict):
        context = Context(context)
    if type(to) in [str, unicode]:
        to = [to]

    if not 'site' in context:
        from orchestra import settings
        url = urlparse.urlparse(settings.SITE_URL)
        context['site'] = {
            'name': settings.SITE_NAME,
            'scheme': url.scheme,
            'domain': url.netloc,
        }
    
    #subject cannot have new lines
    subject = render_to_string(template, {'subject': True}, context).strip()
    message = render_to_string(template, {'message': True}, context)
    msg = EmailMultiAlternatives(subject, message, email_from, to)
    if html:
        html_message = render_to_string(html, {'message': True}, context)
        msg.attach_alternative(html_message, "text/html")
    msg.send()


def running_syncdb():
    return 'migrate' in sys.argv or 'syncdb' in sys.argv
