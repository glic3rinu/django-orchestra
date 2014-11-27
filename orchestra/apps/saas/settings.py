from django.conf import settings


SAAS_ENABLED_SERVICES = getattr(settings, 'SAAS_ENABLED_SERVICES', (
    'orchestra.apps.saas.services.moodle.MoodleService',
    'orchestra.apps.saas.services.bscw.BSCWService',
    'orchestra.apps.saas.services.gitlab.GitLabService',
    'orchestra.apps.saas.services.phplist.PHPListService',
))
