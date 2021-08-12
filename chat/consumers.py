import json

from asgiref.sync import sync_to_async
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from chat.services import chat_save_message

from users.models import CustomUser
from .models import Thread, Message, GroupChat, GroupChatMessage


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        me = self.scope['user']
        other_user_id = self.scope['url_route']['kwargs']['public_id']
        other_user = await sync_to_async(CustomUser.objects.get)(public_id=other_user_id)
        self.thread_obj = await sync_to_async(Thread.objects.get_or_create_personal_thread)(me, other_user)
        self.room_name = f'personal_thread_{self.thread_obj.id}'

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.send({
            'type': 'websocket.accept'
        })
        print(f'[{self.channel_name}] - You are connected.')
        print(f'[self.thread_obj]')

    async def websocket_receive(self, event):
        print(f'[{self.channel_name}] - Received Message - {event["text"]}')

        msg = json.dumps({
            'text': event.get('text'),
            'username': self.scope['user'].name,
            'created_at': '4555'
        })

        # Store the messages here
        # await self.save_message(event.get('text'))

        await self.channel_layer.group_send(
            self.room_name, {
                'type': 'websocket.message',
                'text': msg,
                'created_at': event.get('created_at')
            }
        )

    async def websocket_message(self, event):
        print(f'[{self.channel_name}] - Message Sent - {event["text"]}')
        await self.send({
            'type': 'websocket.send',
            'text': event.get('text'),
            'created_at': event.get('created_at')
        })

    async def websocket_disconnect(self, event):
        print(f'[{self.channel_name}] - Disconnected.')
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    @database_sync_to_async
    def save_message(self, text):
        Message.objects.create(thread=self.thread_obj, sender=self.scope['user'], text=text)


# Groups
class GroupChatConsumer(AsyncWebsocketConsumer):
    """ handshake websocket front end """

    room_name = None
    room_group_name = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = 'group_%s' % self.room_name
        self.real_room_name = await sync_to_async(GroupChat.objects.get)(pk=self.room_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        # Leave room group
        if self.room_group_name and self.channel_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = text_data
            message = text_data_json
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'username': self.scope['user'].name,
                    'message': message,
                }
            )
            await self.save_message(text=message)
        except json.decoder.JSONDecodeError as err:
            print(err)

    # Receive message from room group
    async def chat_message(self, event):
        """ exchange message here """
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'text': message,
            'username': username,
        }))

    @database_sync_to_async
    def save_message(self, text):
        GroupChatMessage.objects.create(user=self.scope['user'], room_name=self.real_room_name, text=text)
