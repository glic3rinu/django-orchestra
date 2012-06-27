from django import template

register = template.Library()

@register.filter(name='safe_message')
def safe_message(value):
    "Removes all values of arg from the given string"
    return value.lower()
    
safe_message.is_safe = True



@register.filter(name='payment_app_comment')
def payment_app_comment(bill):
    #TODO: this import is shit: 
    from django.conf import settings
    if 'payment' in settings.INSTALLED_APPS:
        from payment.models import PaymentDetails
        return PaymentDetails.render_bill_payment_comment(bill)
