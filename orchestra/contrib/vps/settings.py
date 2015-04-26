from orchestra.settings import Setting


VPS_TYPES = Setting('VPS_TYPES', (
    ('openvz', 'OpenVZ container'),
))


VPS_DEFAULT_TYPE = Setting('VPS_DEFAULT_TYPE', 'openvz', choices=VPS_TYPES)


VPS_TEMPLATES = Setting('VPS_TEMPLATES', (
    ('debian7', 'Debian 7 - Wheezy'),
))


VPS_DEFAULT_TEMPLATE = Setting('VPS_DEFAULT_TEMPLATE', 'debian7', choices=VPS_TEMPLATES)
