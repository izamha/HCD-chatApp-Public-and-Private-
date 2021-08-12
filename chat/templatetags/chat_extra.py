from django import template
from ..models import Message

register = template.Library()


@register.filter(name='format_date_chat')
def format_date_chat(value):
    instance_message = Message()
    return instance_message.format_date_chat(value)



