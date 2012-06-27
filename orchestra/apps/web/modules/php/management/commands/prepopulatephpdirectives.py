from django.core.management.base import BaseCommand
from web.modules.php.models import PHPDirective


class Command(BaseCommand):
    def handle(self, **options):
        verbosity = int(options.get('verbosity', 1))
        PHPDirective(            
            name = "auto_append_file",
            regex = "^.+$",
            description = "Specifies the name of a file that is automatically parsed after the main file. The special value none disables auto-appending.").save()
            
        PHPDirective(            
            name = "allow_url_include",
            regex = "^(on|On|Off|off)$",
            description = "This option allows the use of URL-aware fopen wrappers.").save()
            
        PHPDirective(           
            name = "memory_limit",
            regex = "^(\d+M|-1)$",
            description = "This sets the maximum amount of memory in bytes that a script is allowed to allocate. Note that to have no memory limit, set this directive to -1.").save()
            
        PHPDirective(            
            name = "post_max_size",
            regex = "^(\d+M|-1)$",
            description = "Sets max size of post data allowed. This setting also affects file upload.").save()
            
        PHPDirective(
            name = "upload_max_filesize",
            regex = "^(\d+M|-1)$",
            description = "The maximum size of an uploaded file.").save()

        PHPDirective(
            name = "display_errors",
            regex = "^(on|On|Off|off)$",
            description = "This determines whether errors should be printed to the screen as part of the output or if they should be hidden from the user.").save()

        PHPDirective(
            name = "disable_functions",
            regex = "^.+$",
            description = "This directive allows you to disable certain functions for security reasons. It takes on a comma-delimited list of function names.").save()

        PHPDirective(
            name = "register_globals",
            regex = "^(on|On|Off|off)$",
            description = "Whether or not to register the EGPCS (Environment, GET, POST, Cookie, Server) variables as global variables.").save()

        PHPDirective(
            name = "default_socket_timeout",
            regex = "^\d+$",
            description = "Default timeout (in seconds) for socket based streams.").save()

        PHPDirective(            
            name = "mysql.connect_timeout",
            regex = "^\d+$",
            description = "Connect timeout in seconds. On Linux this timeout is also used for waiting for the first answer from the server").save()

        PHPDirective(            
            name = "suhosin.session.encrypt",
            regex = "^(on|On|Off|off)$",
            description = "Flag that decides if the transparent session encryption is activated or not.").save()

        PHPDirective(            
            name = "suhosin.request.max_vars",
            regex = "^\d+$", 
            description = "Defines the maximum number of variables that may be registered through the COOKIE, the URL or through a POST request.").save()
            
        PHPDirective(            
            name = "suhosin.post.max_vars",
            regex = "^\d+$",             
            description = "Defines the maximum number of variables that may be registered through a POST request.").save()

        PHPDirective(            
            name = "suhosin.simulation",
            regex = "^(on|On|Off|off)$",
            description = "If you fear that Suhosin breaks your application, you can activate Suhosin's simulation mode with this flag.").save()

        if verbosity >= 1:
            self.stdout.write("Service prepopulated successfully.\n")
