from django.contrib import admin, messages
from django.shortcuts import render_to_response
from django.views import generic
from django.utils.translation import ngettext, ugettext_lazy as _

from orchestra.contrib.settings import Setting
from orchestra.utils import sys

from . import parser
from .forms import SettingFormSet


class SettingView(generic.edit.FormView):
    template_name = 'admin/settings/change_form.html'
    reload_template_name = 'admin/settings/reload.html'
    form_class = SettingFormSet
    success_url = '.'
    
    def get_context_data(self, **kwargs):
        context = super(SettingView, self).get_context_data(**kwargs)
        context.update({
            'title': _("Change settings"),
            'settings_file': parser.get_settings_file(),
        })
        return context
    
    def get_initial(self):
        initial_data = []
        prev_app = None
        account = 0
        for name, setting in Setting.settings.items():
            app = name.split('_')[0]
            initial = {
                'name': setting.name,
                'help_text': setting.help_text,
                'default': setting.default,
                'type': type(setting.default),
                'value': setting.value,
                'setting': setting,
                'app': app,
            }
            if app == 'ORCHESTRA':
                initial_data.insert(account, initial)
                account += 1
            else:
                initial_data.append(initial)
        return initial_data
    
    def form_valid(self, form):
        settings = Setting.settings
        changes = {}
        for data in form.cleaned_data:
            setting = settings[data['name']]
            if not isinstance(data['value'], parser.NotSupported) and setting.editable:
                if setting.value != data['value']:
                    # Ignore differences between lists and tuples
                    if (type(setting.value) != type(data['value']) and
                        isinstance(data['value'], list) and
                        tuple(data['value']) == setting.value):
                            continue
                    if setting.default == data['value']:
                        changes[setting.name] = parser.Remove()
                    else:
                        changes[setting.name] = data['value']
        if changes:
            # Display confirmation
            if not self.request.POST.get('confirmation'):
                settings_file = parser.get_settings_file()
                new_content = parser.apply(changes)
                cmd = "cat <<EOF | diff %s -\n%s\nEOF" % (settings_file, new_content)
                diff = sys.run(cmd, valid_codes=(1, 0)).stdout
                context = self.get_context_data(form=form)
                context['diff'] = diff
                if not diff:
                    messages.warning(self.request, _("Changes detected but no diff %s.") % changes)
                return self.render_to_response(context)
            n = len(changes)
            # Save changes
            parser.save(changes)
            sys.touch_wsgi()
            context = {
                'message': ngettext(
                    _("One change successfully applied, orchestra is being restarted."),
                    _("%s changes successfully applied, orchestra is being restarted.") % n,
                    n),
            }
            return render_to_response(self.reload_template_name, context)
        else:
            messages.success(self.request, _("No changes have been detected."))
        return super(SettingView, self).form_valid(form)


class SettingFileView(generic.TemplateView):
    template_name = 'admin/settings/view.html'
    
    def get_context_data(self, **kwargs):
        context = super(SettingFileView, self).get_context_data(**kwargs)
        settings_file = parser.get_settings_file()
        with open(settings_file, 'r') as handler:
            content = handler.read()
        context.update({
            'title': _("Settings file content"),
            'settings_file': settings_file,
            'content': content,
        })
        return context


admin.site.register_url(r'^settings/setting/view/$', SettingFileView.as_view(), 'settings_setting_view')
admin.site.register_url(r'^settings/setting/$', SettingView.as_view(), 'settings_setting_change')
