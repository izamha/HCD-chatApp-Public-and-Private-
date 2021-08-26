from django import forms
from .models import GroupChat
from users.models import CustomUser


class GroupChatForm(forms.ModelForm):
    class Meta:
        model = GroupChat
        fields = ('room_name', 'users',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GroupChatForm, self).__init__(*args, **kwargs)
        sample_choices = list(CustomUser.objects.all().exclude(name=self.request.user.name).values_list('id', 'name'))
        # set these choices on the 'users' field.
        self.fields['users'].choices = sample_choices

