from djangoplugins.point import PluginPoint


class DaemonMethod(PluginPoint):
    """ 
    The plugins for this plugin point must provide the following methods:
        def execute(self, daemon, template)
    """
