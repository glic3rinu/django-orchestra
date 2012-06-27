from django import forms
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class ShowText(forms.Widget):
    def render(self, name, value, attrs):
        if hasattr(self, 'initial'):
            value = self.initial
        if self.bold: 
            final_value = u'<b>%s</b>' % (value)
        else:
            final_value = value
        if self.warning:
            final_value = u'<ul class="messagelist"><li class="warning">%s</li></ul>' %(final_value)
        if self.hidden:
            final_value = u'%s<input type="hidden" name="%s" value="%s"/>' % (final_value, name, value)
        return mark_safe(final_value)
            
    def __init__(self, *args, **kwargs):
        if 'bold' in kwargs:
            self.bold = kwargs.pop('bold')
        else: self.bold = False
        if 'warning' in kwargs:
            self.warning = kwargs.pop('warning')
        else: self.warning = False            
        if 'hidden' in kwargs:
            self.hidden = kwargs.pop('hidden')
        else: self.hidden = True
        super(ShowText, self).__init__(*args, **kwargs)
        
    def _has_changed(self, initial, data):
        return False


class CheckboxSelectMultipleTable(forms.CheckboxSelectMultiple):
    def __init__(self, modeladmin, dep_structure=None, attrs=None, choices=()):
        self.dep_structure = dep_structure
        self.modeladmin = modeladmin
        super(CheckboxSelectMultipleTable, self).__init__(attrs, choices)
    
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        final_attrs = self.build_attrs(attrs, name=name)
        opts = self.modeladmin.model._meta
        output = [u"""<div class="module" id="changelist"> 
                        <div class="results"> 
                            <table id="result_list"> 
                                <thead> <tr> 
                                    <th scope="col" class="action-checkbox-column"> 
                                        <input type="checkbox" id="action-toggle" /> </th> 
                                    <th scope="col">%s</th> 
                                    <th scope="col">Depens on
                                    </th> 
                                </tr> </thead> 
                            <tbody>""" % opts.verbose_name ]
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        row = 1
        change_reverse_name = '%s:%s_%s_change' % (self.modeladmin.admin_site.name, opts.app_label, opts.module_name)
        for dep in self.dep_structure:
            keys_links = ''
            for key in self.dep_structure[dep]: 
                obj_url = reverse((change_reverse_name), None, args=(key.pk,))
                string = mark_safe(u'<a href="%s">%s</a>' % (obj_url, key))
                keys_links += string + ', '
            keys_links = keys_links[:-2]
            
            obj_url = reverse((change_reverse_name), None, args=(key.pk,))
            dep_link = mark_safe(u'<a href="%s">%s</a>' % (obj_url, dep))
            
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(dep.pk)
            rendered_cb = cb.render(name, option_value)
            output.append(u"""<tr class="row%s"> <td class="action-checkbox">%s</td> 
                                <td class="nowrap">%s</td>
                                <td class="nowrap">  %s</td> """ % (row%2, rendered_cb, dep_link, keys_links))
            row += 1
        output.append(u'</tbody> </table> </div></div>')
        if self.dep_structure:
            return mark_safe(u'\n'.join(output))   
        else: return 'None'   
