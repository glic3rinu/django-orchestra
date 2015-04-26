import re
import textwrap

from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from django.contrib.admin.templatetags.admin_static import static

# TODO rename readonlywidget
class SpanWidget(forms.Widget):
    """
    Renders a value wrapped in a <span> tag.
    Requires use of specific form support. (see ReadonlyForm or ReadonlyModelForm)
    """
    def __init__(self, *args, **kwargs):
        self.tag = kwargs.pop('tag', '<span>')
        super(SpanWidget, self).__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        original_value = self.original_value
        # Display icon
        if isinstance(original_value, bool):
            icon = static('admin/img/icon-%s.gif' % ('yes' if original_value else 'no',))
            return mark_safe('<img src="%s" alt="%s">' % (icon, str(original_value)))
        tag = self.tag[:-1]
        endtag = '/'.join((self.tag[0], self.tag[1:]))
        return mark_safe('%s%s >%s%s' % (tag, forms.util.flatatt(final_attrs), original_value, endtag))
    
    def value_from_datadict(self, data, files, name):
        return self.original_value
    
    def _has_changed(self, initial, data):
        return False


class ShowTextWidget(forms.Widget):
    def __init__(self, *args, **kwargs):
        for kwarg in ['tag', 'warning', 'hidden']:
            setattr(self, kwarg, kwargs.pop(kwarg, False))
        super(ShowTextWidget, self).__init__(*args, **kwargs)
    
    def render(self, name, value, attrs):
        value = force_text(value)
        if value is None:
            return ''
        if hasattr(self, 'initial'):
            value = self.initial
        if self.tag:
            endtag = '/'.join((self.tag[0], self.tag[1:]))
            final_value = ''.join((self.tag, value, endtag))
        else:
            final_value = '<br/>'.join(value.split('\n'))
        if self.warning:
            final_value = (
                '<ul class="messagelist"><li class="warning">%s</li></ul>'
                % final_value)
        if self.hidden:
            final_value = (
                '%s<input type="hidden" name="%s" value="%s"/>'
                % (final_value, name, value))
        return mark_safe(final_value)
    
    def _has_changed(self, initial, data):
        return False


class ReadOnlyWidget(forms.Widget):
    def __init__(self, *args):
        if len(args) == 1:
            args = (args[0], args[0])
        self.original_value = args[0]
        self.display_value = args[1]
        super(ReadOnlyWidget, self).__init__()
    
    def render(self, name, value, attrs=None):
        if self.display_value is not None:
            return mark_safe(self.display_value)
        return mark_safe(self.original_value)
    
    def value_from_datadict(self, data, files, name):
        return self.original_value


def paddingCheckboxSelectMultiple(padding):
    """ Ugly hack to render this widget nicely on Django admin """
    widget = forms.CheckboxSelectMultiple()
    old_render = widget.render
    def render(self, *args, **kwargs):
        value = old_render(self, *args, **kwargs)
        value = re.sub(r'^<ul id=([^>]+)>',
            r'<ul id=\1 style="padding-left:%ipx">' % padding, value, 1)
        return mark_safe(value)
    widget.render = render
    return widget


class DynamicHelpTextSelect(forms.Select):
    def __init__(self, target, help_text, *args, **kwargs):
        help_text = self.get_dynamic_help_text(target, help_text)
        attrs = kwargs.get('attrs', {})
        attrs.update({
            'onClick': help_text,
            'onChange': help_text,
        })
        attrs.update(kwargs.get('attrs', {}))
        kwargs['attrs'] = attrs
        super(DynamicHelpTextSelect, self).__init__(*args, **kwargs)
    
    def get_dynamic_help_text(self, target, help_text):
        return textwrap.dedent("""\
            siteoptions = {help_text};
            valueelement = $("#" + {target});
            help_text = siteoptions[this.options[this.selectedIndex].value] || ""
            valueelement.parent().find('p').remove();
            valueelement.parent().append("<p class='help'>" + help_text + "</p>");\
            """.format(target=target, help_text=str(help_text))
        )
