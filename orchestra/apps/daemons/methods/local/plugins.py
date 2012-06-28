from daemons.plugins import DaemonMethod
from tasks import execute_local

class Local(DaemonMethod):
    name = 'Local'
    title = 'Run local script'

    def execute(self, daemon, template):
        execute_local.delay(script)
