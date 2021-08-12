import uuid

from django.db import models
from users.models import CustomUser
from .managers import ThreadManager
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group
from django.urls import reverse
from django.conf import settings


class TrackingModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Thread(models.Model):
    THREAD_TYPE = (
        ('personal', 'Personal'),
        ('group', 'Group')
    )

    name = models.CharField(max_length=50, null=True, blank=True)
    thread_type = models.CharField(max_length=15, choices=THREAD_TYPE, default='group')
    users = models.ManyToManyField(CustomUser)

    objects = ThreadManager()

    def __str__(self):
        if self.thread_type == 'personal' and self.users.count() == 2:
            return f'{self.users.first()} and {self.users.last()}'
        return f'{self.name}'


class Message(TrackingModel):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    text = models.TextField(blank=False, null=True)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Thread: {self.thread}'

    def count_unseen_messages(self, current_user):
        unseen_message = Message.objects.filter(thread__users__message=current_user.id, seen=False)
        return unseen_message.count()

    def last_message(self, current_user):
        unseen_message = Message.objects.filter(thread__users__message=current_user.id, seen=False)
        return unseen_message.last()

    # @property
    # def user_last_message(self):
    #     return user.message_set.order_by('-created_at')[:1]


# class Group(TrackingModel):
#     thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True)
#     group_name = models.CharField(max_length=255, verbose_name=_('Group Name'))
#     public_id = models.UUIDField(primary_key=False, default=uuid.uuid4, unique=True)
#     sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
#     text = models.TextField(blank=False, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f'Group {self.pk}: {self.group_name}'

# class ChatGroup(Group):
#     """Extend Group model to add extra info"""
#     group_name = models.CharField(blank=False, verbose_name=_('Group Name'), max_length=255)
#     group_icon = models.ImageField(blank=True, upload_to='group_icons', null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True)
#
#     def get_absolute_url(self):
#         return reverse('chat:room', args=[str(self.id)])

class GroupChat(models.Model):
    room_name = models.CharField(max_length=255, blank=False, null=True, verbose_name='Group Name')
    users = models.ManyToManyField(CustomUser, blank=True)
    group_icon = models.ImageField(default='default.png', upload_to='group_icons', blank=True)

    def __str__(self):
        return self.room_name

    def get_absolute_url(self):
        return reverse('public-chat', args=[str(self.id)])

    def connect_user(self, user):
        is_user_added = False
        if not user in self.users.all():
            self.users.add(user)
            self.save()
            is_user_added = True
        elif user in self.users.all():
            is_user_added = True
        return is_user_added

    def disconnect_user(self, user):
        is_user_removed = False
        if not user in self.users.all():
            self.users.remove(user)
            self.save()
            is_user_removed = True
        return is_user_removed

    @property
    def group_name(self):
        """ Returns the channels group name that sockets should subscribe to """
        return f'Group: {self.id}'


class GroupChatMessageManager(models.Manager):
    def by_group(self, group_name):
        qs = GroupChatMessage.objects.filter(group_name=group_name).order_by('-created_at')
        return qs


class GroupChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room_name = models.ForeignKey(GroupChat, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(unique=False, blank=False)

    objects = GroupChatMessageManager()

    def __str__(self):
        return f'Message({self.id}) in Group "{self.room_name.room_name}"'
