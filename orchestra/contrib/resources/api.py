import json
from urllib.parse import parse_qs

from django.http import HttpResponse

from .helpers import get_history_data
from .models import ResourceData


def history_data(request):
    ids = map(int, parse_qs(request.META['QUERY_STRING'])['ids'][0].split(','))
    queryset = ResourceData.objects.filter(id__in=ids)
    history = get_history_data(queryset)
    response = json.dumps(history, indent=4)
    return HttpResponse(response, content_type="application/json")
