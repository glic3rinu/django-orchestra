from django import forms
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.templatetags.static import static
from markdown import markdown

from orchestra.forms.widgets import SpanWidget

from .models import Queue, Ticket


class MarkDownWidget(forms.Textarea):
    """ MarkDown textarea widget with syntax preview """
    
    markdown_url = static('issues/markdown_syntax.html')
    markdown_help_text = (
        '<a href="%s" onclick=\'window.open("%s", "", "resizable=yes, '
        'location=no, width=300, height=640, menubar=no, status=no, scrollbars=yes"); '
        'return false;\'>markdown format</a>' % (markdown_url, markdown_url)
    )
    markdown_help_text = 'HTML not allowed, you can use %s' % markdown_help_text
    
    def render(self, name, value, attrs):
        widget_id = attrs['id'] if attrs and 'id' in attrs else 'id_%s' % name
        textarea = super(MarkDownWidget, self).render(name, value, attrs)
        preview = ('<a class="load-preview" href="#" data-field="{0}">preview</a>'\
                   '<div id="{0}-preview" class="content-preview"></div>'.format(widget_id))
        return mark_safe('<p class="help">%s<br/>%s<br/>%s</p>' % (
            self.markdown_help_text, textarea, preview))


class MessageInlineForm(forms.ModelForm):
    """  Add message form """
    created_on = forms.CharField(label="Created On", required=False)
    content = forms.CharField(widget=MarkDownWidget(), required=False)
    
    class Meta:
        fields = ('author', 'author_name', 'created_on', 'content')
    
    def __init__(self, *args, **kwargs):
        super(MessageInlineForm, self).__init__(*args, **kwargs)
        self.fields['created_on'].widget = SpanWidget(display='')
        
    def clean_content(self):
        """ clean HTML tags """
        return strip_tags(self.cleaned_data['content'])
    
    def save(self, *args, **kwargs):
        if self.instance.pk is None:
            self.instance.author = self.user
        return super(MessageInlineForm, self).save(*args, **kwargs)


class UsersIterator(forms.models.ModelChoiceIterator):
    """ Group ticket owner by superusers, ticket.group and regular users """
    def __init__(self, *args, **kwargs):
        self.ticket = kwargs.pop('ticket', False)
        super(forms.models.ModelChoiceIterator, self).__init__(*args, **kwargs)
    
    def __iter__(self):
        yield ('', '---------')
        users = get_user_model().objects.exclude(is_active=False).order_by('name')
        superusers = users.filter(is_superuser=True)
        if superusers:
            yield ('Operators', list(superusers.values_list('pk', 'name')))
            users = users.exclude(is_superuser=True)
        if users:
            yield ('Other', list(users.values_list('pk', 'name')))


class TicketForm(forms.ModelForm):
    display_description = forms.CharField(label=_("Description"), required=False)
    description = forms.CharField(widget=MarkDownWidget(attrs={'class':'vLargeTextField'}))
    
    class Meta:
        model = Ticket
        fields = (
            'creator', 'creator_name', 'owner', 'queue', 'subject', 'description',
            'priority', 'state', 'cc', 'display_description'
        )
    
    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        ticket = kwargs.get('instance', False)
        users = self.fields['owner'].queryset
        self.fields['owner'].queryset = users.filter(is_superuser=True)
        if not ticket:
            # Provide default ticket queue for new ticket
            try:
                self.initial['queue'] = Queue.objects.get(default=True).id
            except Queue.DoesNotExist:
                pass
        else:
            description = markdown(ticket.description)
            # some hacks for better line breaking
            description = description.replace('>\n', '#Ha9G9-?8')
            description = description.replace('\n', '<br>')
            description = description.replace('#Ha9G9-?8', '>\n')
            description = '<div style="padding-left: 95px;">%s</div>' % description
            widget = SpanWidget(display=description)
            self.fields['display_description'].widget = widget
    
    def clean_description(self):
        """  clean HTML tags """
        return strip_tags(self.cleaned_data['description'])


class ChangeReasonForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'cols': '100', 'rows': '10'}),
        required=False)
