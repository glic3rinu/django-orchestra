from django.core.validators import validate_email

from orchestra.settings import Setting, ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL


ISSUES_SUPPORT_EMAILS = Setting('ISSUES_SUPPORT_EMAILS',
    (ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL,),
    validators=[lambda emails: [validate_email(e) for e in emails]],
    help_text="Includes <tt>ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL</tt> by default",
)


ISSUES_NOTIFY_SUPERUSERS = Setting('ISSUES_NOTIFY_SUPERUSERS',
    True
)
