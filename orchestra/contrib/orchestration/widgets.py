import textwrap

from orchestra.forms.widgets import DynamicHelpTextSelect


class RouteBackendSelect(DynamicHelpTextSelect):
    """ Updates matches input field based on selected backend """
    def __init__(self, target, help_text, route_matches, *args, **kwargs):
        kwargs['attrs'] = {
            'onfocus': "this.oldvalue = this.value;",
        }
        self.route_matches = route_matches
        super(RouteBackendSelect, self).__init__(target, help_text, *args, **kwargs)
    
    def get_dynamic_help_text(self, target, help_text):
        help_text = super(RouteBackendSelect, self).get_dynamic_help_text(target, help_text)
        return help_text + textwrap.dedent("""\
            routematches = {route_matches};
            match = $("#id_match");
            if ( this.oldvalue == "" || match.value == routematches[this.oldvalue])
                match.value = routematches[this.options[this.selectedIndex].value];
            this.oldvalue = this.value;
            """.format(route_matches=self.route_matches)
        )
