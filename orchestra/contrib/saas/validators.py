from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.apps import isinstalled


def validate_website_saas_directives(app):
    def validator(enabled, app=app):
        if enabled and isinstalled('orchestra.contrib.websites'):
            from orchestra.contrib.websites import settings
            if app not in settings.WEBSITES_SAAS_DIRECTIVES:
                raise ValidationError(_("Allow custom URL is enabled for '%s', "
                                        "but has no associated WEBSITES_SAAS_DIRECTIVES" % app))
    return validator
