import textwrap

from django import forms


class OpenCustomFilteringOnSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        collapse = self.get_dynamic_collapse()
        attrs = kwargs.get('attrs', {})
        attrs.update({
            'onClick': collapse,
            'onChange': collapse,
        })
        attrs.update(kwargs.get('attrs', {}))
        kwargs['attrs'] = attrs
        super(OpenCustomFilteringOnSelect, self).__init__(*args, **kwargs)
    
    def get_dynamic_collapse(self):
        return textwrap.dedent("""\
            value = this.options[this.selectedIndex].value;
            fieldset = $(this).closest("fieldset");
            fieldset = $(".collapse");
            if ( value == 'CUSTOM' ) {
                if (fieldset.hasClass("collapsed")) {
                    fieldset.removeClass("collapsed").trigger("show.fieldset", [$(this).attr("id")]);
                }
            } else {
                if (! $(this).closest("fieldset").hasClass("collapsed")) {
                    fieldset.addClass("collapsed").trigger("hide.fieldset", [$(this).attr("id")]);
                }
            }
            """
        )
