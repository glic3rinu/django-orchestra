def filter_actions(modeladmin, ticket, request):
    if not hasattr(modeladmin, 'change_view_actions_backup'):
        modeladmin.change_view_actions_backup = list(modeladmin.change_view_actions)
    actions = modeladmin.change_view_actions_backup
    if ticket.state == modeladmin.model.CLOSED:
        del_actions = actions
    else:
        from .actions import action_map
        del_actions = [action_map.get(ticket.state, None)]
        if ticket.owner == request.user:
            del_actions.append('take')
    exclude = lambda a: not (a == action or a.url_name == action)
    for action in del_actions:
        actions = filter(exclude, actions)
    return actions


def markdown_formated_changes(changes):
    markdown = ''
    for name, values in changes.items():
        context = (name.capitalize(), values[0], values[1])
        markdown += '* **%s** changed from _%s_ to _%s_\n' % context
    return markdown + '\n'


def get_ticket_changes(modeladmin, request, ticket):
    ModelForm = modeladmin.get_form(request, ticket)
    form = ModelForm(request.POST, request.FILES)
    changes = {}
    if form.is_valid():
        for attr in ['state', 'priority', 'owner', 'queue']:
            old_value = getattr(ticket, attr)
            new_value = form.cleaned_data[attr]
            if old_value != new_value:
                changes[attr] = (old_value, new_value)
    return changes
