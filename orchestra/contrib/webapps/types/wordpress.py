from django.utils.translation import ugettext_lazy as _

from .cms import CMSApp


class WordPressApp(CMSApp):
    name = 'wordpress-php'
    verbose_name = "WordPress"
    help_text = _(
        "Visit http://&lt;domain.lan&gt;/wp-admin/install.php to finish the installation.<br>"
        "A database and database user will automatically be created for this webapp."
    )
    icon = 'orchestra/icons/apps/WordPress.png'
