import textwrap

from orchestra.contrib.orchestration import ServiceController


class MoodleWWWRootController(ServiceController):
    """
    Configures Moodle site WWWRoot, without it Moodle refuses to work.
    """
    verbose_name = "Moodle WWWRoot (required)"
    model = 'websites.Content'
    default_route_match = "content.webapp.type == 'moodle-php'"
    
    def save(self, content):
        context = self.get_context(content)
        self.append(textwrap.dedent("""\
            sed -i "s#wwwroot\s*= '.*#wwwroot    = '%(url)s';#" %(app_path)s/config.php
            """) % context
        )
    
    def get_context(self, content):
        return {
            'url': content.get_absolute_url(),
            'app_path': content.webapp.get_path(),
        }
