from django import forms
from .models import GroupChat


class GroupChatForm(forms.ModelForm):
    class Meta:
        model = GroupChat
        fields = ('room_name', 'users',)
