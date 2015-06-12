import textwrap

from django.contrib import messages
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra import settings as orchestra_settings
from orchestra.admin.utils import change_url


def get_backends_help_text(backends):
    help_texts = {}
    for backend in backends:
        help_text = backend.__doc__ or ''
        context = {
            'model': backend.model,
            'related_models': str(backend.related_models),
            'script_executable': backend.script_executable,
            'script_method': '.'.join((backend.script_method.__module__, backend.script_method.__name__)),
            'function_method': '.'.join((backend.function_method.__module__, backend.function_method.__name__)),
            'actions': str(backend.actions),
        }
        help_text += textwrap.dedent("""
            - Model: <tt>'%(model)s'</tt>
            - Related models: <tt>%(related_models)s</tt>
            - Script executable: <tt>%(script_executable)s</tt>
            - Script method: <tt>%(script_method)s</tt>
            - Function method: <tt>%(function_method)s</tt>
            - Actions: <tt>%(actions)s</tt>
            """
        ) % context
        help_text = help_text.lstrip().splitlines()
        help_settings = ['']
        if backend.doc_settings:
            module, names = backend.doc_settings
            for name in names:
                value = getattr(module, name)
                if isinstance(value, str):
                    help_settings.append("<tt>%s = '%s'</tt>" % (name, value))
                else:
                    help_settings.append("<tt>%s = %s</tt>" % (name, str(value)))
        help_text += help_settings
        help_texts[backend.get_name()] = '<br>'.join(help_text)
    return help_texts


def get_instance_url(operation):
    try:
        url = change_url(operation.instance)
    except NoReverseMatch:
        return _("Deleted {0}").format(operation.instance_repr or '-'.join(
            (escape(operation.content_type), escape(operation.object_id))))
    return orchestra_settings.ORCHESTRA_SITE_URL + url


def send_report(method, args, log):
    server = args[0]
    backend = method.__self__.__class__.__name__
    subject = '[Orchestra] %s execution %s on %s'  % (backend, log.state, server)
    separator = "\n%s\n\n" % ('~ '*40,)
    print(log.operations.all())
    operations = '\n'.join([' '.join((op.action, get_instance_url(op))) for op in log.operations.all()])
    message = separator.join([
        "[EXIT CODE] %s" % log.exit_code,
        "[STDERR]\n%s" % log.stderr,
        "[STDOUT]\n%s" % log.stdout,
        "[SCRIPT]\n%s" % log.script,
        "[TRACEBACK]\n%s" % log.traceback,
        "[OPERATIONS]\n%s" % operations,
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
        '<h4 style="color:#505050;">Operations</h4>'
            '<pre style="margin-left:20px;font-size:11px">%s</pre>' % escape(operations),
    ])
    mail_admins(subject, message, html_message=html_message)


def get_backend_url(ids):
    if len(ids) == 1:
        return reverse('admin:orchestration_backendlog_change', args=ids)
    elif len(ids) > 1:
        url = reverse('admin:orchestration_backendlog_changelist')
        return url + '?id__in=%s' % ','.join(map(str, ids))
    return ''


def message_user(request, logs):
    total, successes, async = 0, 0, 0
    ids = []
    async_ids = []
    for log in logs:
        total += 1
        if log.state != log.EXCEPTION:
            # EXCEPTION logs are not stored on the database
            ids.append(log.pk)
        if log.is_success:
            successes += 1
        elif not log.has_finished:
            async += 1
            async_ids.append(log.id)
    errors = total-successes-async
    url = get_backend_url(ids)
    async_url = get_backend_url(async_ids)
    async_msg = ''
    if async:
        async_msg = ungettext(
            _('<a href="{async_url}">{async} backend</a> is running on the background'),
            _('<a href="{async_url}">{async} backends</a> are running on the background'),
            async)
    if errors:
        msg = ungettext(
            _('<a href="{url}">{errors} out of {total} backend</a> has fail to execute'),
            _('<a href="{url}">{errors} out of {total} backends</a> have fail to execute'),
            errors)
        if async_msg:
            msg += ', ' + str(async_msg)
        msg = msg.format(errors=errors, async=async, async_url=async_url, total=total, url=url)
        messages.error(request, mark_safe(msg + '.'))
    elif successes:
        if async_msg:
            msg = ungettext(
                _('<a href="{url}">{successes} out of {total} backend</a> has been executed'),
                _('<a href="{url}">{successes} out of {total} backends</a> have been executed'),
                successes)
            msg += ', ' + str(async_msg)
        else:
            msg = ungettext(
                _('<a href="{url}">{total} backend</a> has been executed'),
                _('<a href="{url}">{total} backends</a> have been executed'),
                total)
        msg = msg.format(total=total, url=url, async_url=async_url, async=async, successes=successes)
        messages.success(request, mark_safe(msg + '.'))
    else:
        msg = async_msg.format(url=url, async_url=async_url, async=async)
        messages.success(request, mark_safe(msg + '.'))

