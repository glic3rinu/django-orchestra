from rest_framework import serializers

from .models import Ticket, Message, Queue


class QueueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Queue
        fields = ('url', 'name', 'default', 'notify')
        read_only_fields = ('name', 'default', 'notify')


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'author', 'author_name', 'content', 'created_on')
        read_only_fields = ('author', 'author_name', 'created_on')
    
    def get_identity(self, data):
        return data.get('id')
    
    def save_object(self, obj, **kwargs):
        obj.author = self.context['request'].user
        super(MessageSerializer, self).save_object(obj, **kwargs)


class TicketSerializer(serializers.HyperlinkedModelSerializer):
    """ Validates if this zone generates a correct zone file """
    messages = MessageSerializer(required=False, many=True)
    is_read = serializers.SerializerMethodField('get_is_read')
    
    class Meta:
        model = Ticket
        fields = (
            'url', 'id', 'creator', 'creator_name', 'owner', 'queue', 'subject',
            'description', 'state', 'messages', 'is_read'
        )
        read_only_fields = ('creator', 'creator_name', 'owner')
    
    def get_is_read(self, obj):
        return obj.is_read_by(self.context['request'].user)
    
    def save_object(self, obj, **kwargs):
        obj.creator = self.context['request'].user
        super(TicketSerializer, self).save_object(obj, **kwargs)
