import django.dispatch

zone_created = django.dispatch.Signal(providing_args=["instance"])
zone_updated = django.dispatch.Signal(providing_args=["instance"])
zone_deleted = django.dispatch.Signal(providing_args=["instance"])



@django.dispatch.receiver(zone_created, dispatch_uid="dns.zone_created")
def create_name(sender, **kwargs):
    instance = kwargs['instance']
    print 'zone created'


