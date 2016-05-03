import re
import textwrap

from django import forms
from django.utils.safestring import mark_safe

from django.contrib.admin.templatetags.admin_static import static


class SpanWidget(forms.Widget):
    """
    Renders a value wrapped in a <span> tag.
    Requires use of specific form support. (see ReadonlyForm or ReadonlyModelForm)
    """
    def __init__(self, *args, **kwargs):
        self.tag = kwargs.pop('tag', '<span>')
        self.original = kwargs.pop('original', '')
        self.display = kwargs.pop('display', None)
        super(SpanWidget, self).__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        original = self.original or value
        display = original if self.display is None else self.display
        # Display icon
        if isinstance(original, bool):
            icon = static('admin/img/icon-%s.svg' % ('yes' if original else 'no',))
            return mark_safe('<img src="%s" alt="%s">' % (icon, display))
        tag = self.tag[:-1]
        endtag = '/'.join((self.tag[0], self.tag[1:]))
        return mark_safe('%s%s >%s%s' % (tag, forms.utils.flatatt(final_attrs), display, endtag))
    
    def value_from_datadict(self, data, files, name):
        return self.original
    
    def _has_changed(self, initial, data):
        return False


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
