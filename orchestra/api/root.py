from rest_framework import views
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .. import settings
from ..core import services, accounts


class APIRoot(views.APIView):
    names = (
        'ORCHESTRA_SITE_NAME',
        'ORCHESTRA_SITE_VERBOSE_NAME'
    )
    
    def get(self, request, format=None):
        root_url = reverse('api-root', request=request, format=format)
        token_url = reverse('api-token-auth', request=request, format=format)
        links = [
            '<%s>; rel="%s"' % (root_url, 'api-root'),
            '<%s>; rel="%s"' % (token_url, 'api-get-auth-token'),
        ]
        body = {
            'accountancy': {},
            'services': {},
        }
        if not request.user.is_anonymous():
            list_name = '{basename}-list'
            detail_name = '{basename}-detail'
            for prefix, viewset, basename in self.router.registry:
                singleton_pk = getattr(viewset, 'singleton_pk', False)
                if singleton_pk:
                    url_name = detail_name.format(basename=basename)
                    kwargs = {
                        'pk': singleton_pk(viewset(), request)
                    }
                else:
                    url_name = list_name.format(basename=basename)
                    kwargs = {}
                url = reverse(url_name, request=request, format=format, kwargs=kwargs)
                links.append('<%s>; rel="%s"' % (url, url_name))
                model = viewset.queryset.model
                group = None
                if model in services:
                    group = 'services'
                    menu = services[model].menu
                if model in accounts:
                    group = 'accountancy'
                    menu = accounts[model].menu
                if group and menu:
                    body[group][basename] = {
                        'url': url,
                        'verbose_name': model._meta.verbose_name,
                        'verbose_name_plural': model._meta.verbose_name_plural,
                    }
        headers = {
            'Link': ', '.join(links)
        }
        body.update({
            name.lower(): getattr(settings, name, None)
                for name in self.names
        })
        return Response(body, headers=headers)
    
    def options(self, request):
        metadata = super(APIRoot, self).options(request)
        metadata.data['settings'] = {
            name.lower(): getattr(settings, name, None)
            for name in self.names
        }
        return metadata
