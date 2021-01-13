from orchestra.contrib.settings import Setting


VPS_TYPES = Setting('VPS_TYPES',
    (
        ('openvz', 'OpenVZ container'),
        ('lxc', 'LXC container')
    ),
    validators=[Setting.validate_choices]
)


VPS_DEFAULT_TYPE = Setting('VPS_DEFAULT_TYPE',
    'lxc',
    choices=VPS_TYPES
)


VPS_TEMPLATES = Setting('VPS_TEMPLATES',
    (
        ('debian7', 'Debian 7 - Wheezy'),
        ('placeholder', 'LXC placeholder')
    ),
    validators=[Setting.validate_choices]
)


VPS_DEFAULT_TEMPLATE = Setting('VPS_DEFAULT_TEMPLATE',
    'placeholder',
    choices=VPS_TEMPLATES
)


VPS_DEFAULT_VZSET_ARGS = Setting('VPS_DEFAULT_VZSET_ARGS',
    ('--onboot yes',),
)
