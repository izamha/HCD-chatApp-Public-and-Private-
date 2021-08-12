from tortoise import fields
from tortoise.models import Model


class ChatMessage(Model):
    """ Used to store chat history using the tortoise ORM which supports asyncio """
    id = fields.IntField(pk=True)
    room_id = fields.IntField(null=True)
    name = fields.CharField(max_length=250, null=True)
    message = fields.TextField()
    message_type = fields.CharField(max_length=50, null=True)
    image_caption = fields.CharField(max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True)

    class Meta:
        table = 'chat_chatmessage'

    def __str__(self):
        return f'Message: {self.id}'
