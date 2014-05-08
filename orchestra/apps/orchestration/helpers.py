from django.contrib import messages
from django.core.mail import mail_admins
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _


def send_report(method, args, log):
    backend = method.im_class().get_name()
    server = args[0]
    subject = '[Orchestra] %s execution %s on %s'
    subject = subject % (backend, log.state, server)
    separator = "\n%s\n\n" % ('~ '*40,)
    message = separator.join([
        "[EXIT CODE] %s" % log.exit_code,
        "[STDERR]\n%s" % log.stderr,
        "[STDOUT]\n%s" % log.stdout,
        "[SCRIPT]\n%s" % log.script,
        "[TRACEBACK]\n%s" % log.traceback,
    ])
    html_message = '\n\n'.join([
        '<h4 style="color:#505050;">Exit code %s</h4>' % log.exit_code,
        '<h4 style="color:#505050;">Stderr</h4>'
            '<pre style="margin-left:20px;font-size:11px">%s</pre>' % escape(log.stderr),
        '<h4 style="color:#505050;">Stdout</h4>'
            '<pre style="margin-left:20px;font-size:11px">%s</pre>' % escape(log.stdout),
        '<h4 style="color:#505050;">Script</h4>'
            '<pre style="margin-left:20px;font-size:11px">%s</pre>' % escape(log.script),
        '<h4 style="color:#505050;">Traceback</h4>'
            '<pre style="margin-left:20px;font-size:11px">%s</pre>' % escape(log.traceback),
    ])
    mail_admins(subject, message, html_message=html_message)


def message_user(request, logs):
    total = len(logs)
    successes = [ log for log in logs if log.state == log.SUCCESS ]
    successes = len(successes)
    errors = total-successes
    if errors:
        msg = 'backends have' if errors > 1 else 'backend has'
        msg = _("%d out of %d {0} fail to executed".format(msg))
        messages.warning(request, msg % (errors, total))
    else:
        msg = 'backends have' if successes > 1 else 'backend has'
        msg = _("%d {0} been successfully executed".format(msg))
        messages.success(request, msg % successes)
