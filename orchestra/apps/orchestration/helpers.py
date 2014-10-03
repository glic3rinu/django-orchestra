from django.contrib import messages
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _


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
    total, successes = 0, 0
    ids = []
    for log in logs:
        total += 1
        ids.append(log.pk)
        if log.state == log.SUCCESS:
            successes += 1
    errors = total-successes
    if total > 1:
        url = reverse('admin:orchestration_backendlog_changelist')
        url += '?id__in=%s' ','.join(map(str, ids))
    else:
        url = reverse('admin:orchestration_backendlog_change', args=ids)
    if errors:
        msg = ungettext(
            _('{errors} out of {total} <a href="{url}">banckends</a> has fail to execute.'),
            _('{errors} out of {total} <a href="{url}">banckends</a> have fail to execute.'),
            errors)
    else:
        msg = ungettext(
            _('{total} <a href="{url}">banckend</a> has been executed.'),
            _('{total} <a href="{url}">banckends</a> have been executed.'),
            total)
    messages.warning(request, mark_safe(msg.format(errors=errors, total=total, url=url)))
