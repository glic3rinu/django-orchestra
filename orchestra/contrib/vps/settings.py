from orchestra.contrib.settings import Setting


VPS_TYPES = Setting('VPS_TYPES',
    (
        ('openvz', 'OpenVZ container'),
    ),
    validators=[Setting.validate_choices]
)


VPS_DEFAULT_TYPE = Setting('VPS_DEFAULT_TYPE',
    'openvz',
    choices=VPS_TYPES
)


VPS_TEMPLATES = Setting('VPS_TEMPLATES',
    (
        ('debian7', 'Debian 7 - Wheezy'),
    ),
    validators=[Setting.validate_choices]
)


VPS_DEFAULT_TEMPLATE = Setting('VPS_DEFAULT_TEMPLATE',
    'debian7',
    choices=VPS_TEMPLATES
)


VPS_DEFAULT_VZSET_ARGS = Setting('VPS_DEFAULT_VZSET_ARGS',
    ('--onboot yes',),
)
