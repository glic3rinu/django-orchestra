import django.dispatch


pre_action = django.dispatch.Signal(providing_args=['backend', 'instance', 'action'])

post_action = django.dispatch.Signal(providing_args=['backend', 'instance', 'action'])
