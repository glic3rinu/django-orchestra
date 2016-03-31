from rest_framework import serializers

from .models import Ticket, Message, Queue


class QueueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Queue
        fields = ('url', 'id', 'name', 'default', 'notify')
        read_only_fields = ('name', 'default', 'notify')


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'author', 'author_name', 'content', 'created_at')
        read_only_fields = ('author', 'author_name', 'created_at')
    
    def get_identity(self, data):
        return data.get('id')
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super(MessageSerializer, self).create(validated_data)


class TicketSerializer(serializers.HyperlinkedModelSerializer):
    """ Validates if this zone generates a correct zone file """
    messages = MessageSerializer(required=False, many=True, read_only=True)
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = (
            'url', 'id', 'creator', 'creator_name', 'owner', 'queue', 'subject',
            'description', 'state', 'messages', 'is_read'
        )
        read_only_fields = ('creator', 'creator_name', 'owner')
    
    def get_is_read(self, obj):
        return obj.is_read_by(self.context['request'].user)
    
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super(TicketSerializer, self).create(validated_data)
