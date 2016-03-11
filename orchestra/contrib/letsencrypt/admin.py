from orchestra.admin.utils import insertattr
from orchestra.contrib.websites.admin import WebsiteAdmin

from .import actions


insertattr(WebsiteAdmin, 'change_view_actions', actions.letsencrypt)
insertattr(WebsiteAdmin, 'actions', actions.letsencrypt)
