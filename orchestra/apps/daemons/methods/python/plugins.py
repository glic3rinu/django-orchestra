from daemons.plugins import DaemonMethod
#from tasks import execute_python
import imp

class Python(DaemonMethod):
    name = 'Python'
    title = 'Execute as python code'

    def execute(self, daemon, template):
        script = {}
        exec(template) in script
        return [script['result']]

