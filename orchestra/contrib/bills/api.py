from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import detail_route

from orchestra.api import router, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin
from orchestra.utils.html import html_to_pdf

from .models import Bill
from .serializers import BillSerializer



class BillViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    
    @detail_route(methods=['get'])
    def document(self, request, pk):
        bill = self.get_object()
        content_type = request.META.get('HTTP_ACCEPT')
        if content_type == 'application/pdf':
            pdf = html_to_pdf(bill.html or bill.render())
            return HttpResponse(pdf, content_type='application/pdf')
        else:
            return HttpResponse(bill.html or bill.render())


router.register('bills', BillViewSet)
