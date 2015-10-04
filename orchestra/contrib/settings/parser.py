import ast
import copy
import json
import os
import re

from django.utils.translation import ugettext_lazy as _
from django.utils.functional import Promise

from orchestra.utils.paths import get_project_dir

from . import Setting


class Remove(object):
    """ used to signal a setting remove """
    pass


def get_settings_file():
    return os.path.join(get_project_dir(), 'settings.py')


def _find_updates(changes, settings_file):
    """ find all updates needed for applying changes on settings_file content """
    with open(settings_file, 'rb') as handler:
        p = ast.parse(handler.read())
    updates = []
    for elem in p.body:
        if updates and updates[-1][-1] is None:
            updates[-1][-1] = elem.lineno-1
        targets = getattr(elem, 'targets', None)
        if targets:
            var_name = targets[0].id
            if var_name in changes:
                updates.append([var_name, elem.lineno, None])
    return updates


class LazyUgettextRepr(object):
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return '_("%s")' % self.value
    
    def __len__(self):
        return len(repr(self.value))


class NotSupported(object):
    def __repr__(self):
        return 'Serialization not supported'
    
    def __len__(self):
        return 0


def get_eval_context():
    return {
        'NotSupported': NotSupported,
        '_': _,
    }


def serialize(obj, init=True):
    if isinstance(obj, NotSupported):
        return obj
    elif isinstance(obj, Promise):
        _obj = LazyUgettextRepr(obj)
    elif isinstance(obj, dict):
        _obj = {}
        for name, value in obj.items():
            name = serialize(name, init=False)
            value = serialize(value, init=False)
            if isinstance(name, NotSupported) or isinstance(value, NotSupported):
                return NotSupported()
            _obj[name] = value
    elif isinstance(obj, (tuple, list)):
        _obj = []
        for nested in obj:
            nested = serialize(nested, init=False)
            if isinstance(nested, NotSupported):
                return nested
            _obj.append(nested)
        _obj = type(obj)(_obj)
    elif isinstance(obj, (str, bool, int, float)):
        _obj = obj
    else:
        _obj = NotSupported()
    return repr(_obj) if init else _obj


def _format_setting(name, value):
    if isinstance(value, Remove):
        return ""
    try:
        value = json.dumps(value, indent=4)
    except TypeError:
        value = serialize(value)
    return "{name} = {value}".format(name=name, value=value)


def validate_changes(changes):
    for name, value in changes.items():
        if not isinstance(value, Remove):
            try:
                setting = Setting.settings[name]
            except KeyError:
                pass
            else:
                setting.validate_value(value)


def apply(changes, settings_file=get_settings_file()):
    """ returns settings_file content with applied changes """
    validate_changes(changes)
    updates = _find_updates(changes, settings_file)
    content = []
    _changes = copy.copy(changes)
    inside = False
    lineno = None
    if updates:
        name, lineno, end = updates.pop(0)
    # update existing variable declarations
    with open(settings_file, 'r') as handler:
        for num, line in enumerate(handler.readlines(), 1):
            line = line.rstrip()
            if num == lineno:
                value = _changes.pop(name)
                line = _format_setting(name, value)
                if line:
                    content.append(line)
                inside = True
                comments = []
                lastend = end
                try:
                    name, lineno, end = updates.pop(0)
                except IndexError:
                    if lastend is None:
                        break
            if not inside:
                content.append(line)
            else:
                # Discard lines since variable will be replaced
                # But save comments and blank lines
                if re.match(r'^\s*(#.*)*\s*$', line):
                    comments.append(line)
                else:
                    comments = []
                # End of variable declaration
                if num == lastend:
                    content.extend(comments)
                    inside = False
    
    # insert new variables at the end of file
    for name, value in _changes.items():
        content.append(_format_setting(name, value))
    return '\n'.join(content)


def save(changes, settings_file=get_settings_file(), backup=True):
    """ apply changes to project.settings file, saving a backup """
    new_settings = apply(changes, settings_file)
    tmp_settings_file = settings_file + '.tmp'
    with open(tmp_settings_file, 'w') as handle:
        handle.write(new_settings)
    if backup:
        os.rename(settings_file, settings_file + '.backup')
    os.rename(tmp_settings_file, settings_file)
