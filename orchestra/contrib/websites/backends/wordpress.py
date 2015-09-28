import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController


class WordPressURLBackend(ServiceController):
    """
    Configures WordPress site URL with associated website domain.
    """
    verbose_name = _("WordPress URL")
    model = 'websites.Content'
    default_route_match = "content.webapp.type == 'wordpress-php'"
    
    def save(self, content):
        context = self.get_context(content)
        if context['url']:
            self.append(textwrap.dedent("""\
                mysql %(db_name)s -e 'UPDATE wp_options
                                      SET option_value="%(url)s"
                                      WHERE option_id IN (1, 2) AND option_value="http:";'
                """) % context
            )
    
    def delete(self, content):
        context = self.get_context(content)
        self.append(textwrap.dedent("""\
            mysql %(db_name)s -e 'UPDATE wp_options
                                  SET option_value="http:"
                                  WHERE option_id IN (1, 2);'
            """) % context
        )
    
    def get_context(self, content):
        return {
            'url': content.get_absolute_url(),
            'db_name': content.webapp.data.get('db_name'),
        }
