from django.core.management.base import BaseCommand
from web.modules.fcgid.models import FcgidDirective


class Command(BaseCommand):
    def handle(self, **options):
        verbosity = int(options.get('verbosity', 1))
        FcgidDirective(
            name = "FcgidConnectTimeout",
            regex = "^\d+$",
            description = "Maximum period of time the module will wait while trying to connect to a FastCGI application on Windows.").save()
            
        FcgidDirective(
            name = "FcgidIdleTimeout",
            regex = "^\d+$",
            description = "Processes which have not handled a request for this period of time will be terminated. A value of 0 disables the check.").save()
            
        FcgidDirective(            
            name = "FcgidInitialEnv",
            regex = ".+",
            description = "Define environment variables to pass to the FastCGI application. This directive can be used multiple times.").save()

        FcgidDirective(
            name = "FcgidIOTimeout",
            regex = "^\d+$",
            description = "Maximum period of time the module will wait while trying to read from or write to a FastCGI application.").save()

        FcgidDirective(
            name = "FcgidMaxProcessesPerClass",
            regex = "^\d+$",
            description = "Sets the maximum number of processes that can be started for each process class.").save()

        FcgidDirective(
            name = "FcgidProcessLifeTime",
            regex = "^\d+$",
            description = "Idle application processes which have existed for greater than this time will be terminated. A value of 0 disables the check.").save()

        FcgidDirective(            
            name = "FcgidMaxRequestsPerProcess",
            regex = "^\d+$",
            description = "Processes will be terminated after handling the specified number of requests. A value of 0 disables the check.").save()

        FcgidDirective(
            name = "FcgidMinProcessesPerClass",
            regex = "^\d+$",
            description = "Sets the minimum number of processes that will be retained in a process class after finishing requests.").save()

        if verbosity >= 1:
            self.stdout.write("Service prepopulated successfully.\n")
