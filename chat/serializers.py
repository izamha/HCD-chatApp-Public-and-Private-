from rest_framework import serializers
from .models import (GroupChat,
                     GroupChatMessage,
                     Message,)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChat
        fields = '__all__'


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChat
        fields = ('room_name', 'users',)


class GroupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChat
        fields = ('room_name', 'users',)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
