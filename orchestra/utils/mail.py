from urllib.parse import urlparse

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import Context


def render_email_template(template, context):
    """
    Renders an email template with this format:
        {% if subject %}Subject{% endif %}
        {% if message %}Email body{% endif %}
    
    context can be a dictionary or a template.Context instance
    """
    if isinstance(context, dict):
        context = Context(context)
    
    if not 'site' in context:
        from orchestra import settings
        url = urlparse(settings.ORCHESTRA_SITE_URL)
        context['site'] = {
            'name': settings.ORCHESTRA_SITE_NAME,
            'scheme': url.scheme,
            'domain': url.netloc,
        }
    subject = render_to_string(template, {'subject': True}, context).strip()
    message = render_to_string(template, {'message': True}, context).strip()
    return subject, message


def send_email_template(template, context, to, email_from=None, html=None, attachments=[]):
    if isinstance(to, str):
        to = [to]
    subject, message = render_email_template(template, context)
    msg = EmailMultiAlternatives(subject, message, email_from, to, attachments=attachments)
    if html:
        subject, html_message = render_email_template(html, context)
        msg.attach_alternative(html_message, "text/html")
    msg.send()
