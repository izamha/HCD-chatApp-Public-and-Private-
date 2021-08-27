from rest_framework import serializers
from .models import (GroupChat,
                     GroupChatMessage,
                     Message, )
from users.models import CustomUser


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'password',)

    def create(self, validated_data):
        user = super(UserCreateSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('text', 'seen', 'thread', 'sender',)
