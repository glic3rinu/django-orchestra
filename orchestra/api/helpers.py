from django.core.urlresolvers import NoReverseMatch
from rest_framework.reverse import reverse


def link_wrap(view, view_names):
    def wrapper(self, request, *args, **kwargs):
        """ wrapper function that inserts HTTP links on view """
        links = []
        for name in view_names:
            try:
                url = reverse(name, request=self.request)
            except NoReverseMatch:
                url = reverse(name, args, kwargs, request=request)
            links.append('<%s>; rel="%s"' % (url, name))
        response = view(self, request, *args, **kwargs)
        response['Link'] = ', '.join(links)
        return response
    for attr in dir(view):
        try:
            setattr(wrapper, attr, getattr(view, attr))
        except:
            pass
    return wrapper


def insert_links(viewset, base_name):
    collection_links = ['api-root', '%s-list' % base_name]
    object_links = ['api-root', '%s-list' % base_name, '%s-detail' % base_name]
    exception_links = ['api-root']
    list_links = ['api-root']
    retrieve_links = ['api-root', '%s-list' % base_name]
    # Determine any `@action` or `@link` decorated methods on the viewset
    for methodname in dir(viewset):
        method = getattr(viewset, methodname)
        view_name = '%s-%s' % (base_name, methodname.replace('_', '-'))
        if hasattr(method, 'collection_bind_to_methods'):
            list_links.append(view_name)
            retrieve_links.append(view_name)
            setattr(viewset, methodname, link_wrap(method, collection_links))
        elif hasattr(method, 'bind_to_methods'):
            retrieve_links.append(view_name)
            setattr(viewset, methodname, link_wrap(method, object_links))
    viewset.handle_exception = link_wrap(viewset.handle_exception, exception_links)
    viewset.list = link_wrap(viewset.list, list_links)
    viewset.retrieve = link_wrap(viewset.retrieve, retrieve_links)
