import django.dispatch


pre_action = django.dispatch.Signal(providing_args=['backend', 'instance', 'action'])

post_action = django.dispatch.Signal(providing_args=['backend', 'instance', 'action'])

pre_prepare = django.dispatch.Signal(providing_args=['backend'])

post_prepare = django.dispatch.Signal(providing_args=['backend'])

pre_commit = django.dispatch.Signal(providing_args=['backend'])

post_commit = django.dispatch.Signal(providing_args=['backend'])
