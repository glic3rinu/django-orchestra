from rest_framework import viewsets, mixins
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from orchestra.api import router, LogApiMixin

from .models import Ticket, Queue
from .serializers import TicketSerializer, QueueSerializer



class TicketViewSet(LogApiMixin, viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    
    @detail_route()
    def mark_as_read(self, request, pk=None):
        ticket = self.get_object()
        ticket.mark_as_read_by(request.user)
        return Response({'status': 'Ticket marked as read'})
    
    @detail_route()
    def mark_as_unread(self, request, pk=None):
        ticket = self.get_object()
        ticket.mark_as_unread_by(request.user)
        return Response({'status': 'Ticket marked as unread'})
    
    def get_queryset(self):
        qs = super(TicketViewSet, self).get_queryset()
        qs = qs.select_related('creator', 'queue')
        qs = qs.prefetch_related('messages__author')
        return qs.filter(creator=self.request.user)


class QueueViewSet(LogApiMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer


router.register(r'tickets', TicketViewSet)
router.register(r'ticket-queues', QueueViewSet)
