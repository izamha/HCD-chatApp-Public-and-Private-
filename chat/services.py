from tortoise import Tortoise, run_async
from django.conf import settings
from .tortoise_models import ChatMessage


async def chat_save_message(name, room_id, message):
    """ Store group chat message to sqlite3 """
    await Tortoise.init(db_url='sqlite://db.sqlite3', modules={'models': ['chat.models']})
    await Tortoise.generate_schemas()

    await ChatMessage.create(room_id=room_id, name=name, message=message)
    await Tortoise.close_connections()
