from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from django.shortcuts import get_object_or_404
# API
from rest_framework import generics, views
from rest_framework.response import Response

from users.models import ActiveUser
from .forms import GroupChatForm
from .models import Message, CustomUser, Thread, GroupChat, GroupChatMessage
from .serializers import (GroupSerializer,
                          GroupCreateSerializer,
                          GroupDetailSerializer,
                          MessageSerializer, )
from rest_framework import status


@login_required
def home(request):
    instance = Message()
    last_message = instance.last_message(request.user)
    unseen_message = instance.count_unseen_messages(request.user)
    all_users = sorted(CustomUser.objects.all(), key=lambda inst: inst.date_joined)[::-1]
    groups_participated = GroupChat.objects.filter(users__in=[request.user.pk])
    active_users = ActiveUser.objects.all()
    context = {
        'title': 'Home',
        'last_message': last_message,
        'users': all_users,
        'groups_participated': groups_participated,
        'unseen_message': unseen_message,
        'active_users': active_users,
    }
    return render(request, 'chat/room_all.html', context)


def get_members(group_id=None, group_obj=None, user=None):
    """ Get all participants that belong to a certain group """

    if group_id:
        chat_group = GroupChat.objects.get(id=id)
    else:
        chat_group = group_obj

    temp_members = []
    for member in chat_group.users.values_list('name', flat=True):
        if member != user:
            temp_members.append(member)
        else:
            temp_members.append('You')
    return ', '.join(temp_members)


@login_required
def room(request, group_id):
    all_groups = GroupChat.objects.all()
    for group in all_groups:
        if request.user in group.users.all():
            chat_group = GroupChat.objects.get(id=group_id)
            groups = GroupChat.objects.filter(users__in=[request.user.pk])
            group_messages = GroupChatMessage.objects.filter(room_name__in=[group_id])
            active_users = ActiveUser().current_active_users2()
            context = {
                'chat_group': chat_group,
                'groups': groups,
                'group_messages': group_messages,
                'active_users': active_users,
                'users': CustomUser.objects.all(),
                'members': get_members(group_obj=chat_group, user=request.user.name),
            }
            return render(request, 'chat/room_all.html', context)
        # else:
        #     return HttpResponseRedirect(reverse("chat:unauthorized"))


def unauthorized(request):
    return render(request, 'chat/unauthorized.html')


def new_group(request):
    if request.method == 'POST':
        form = GroupChatForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'You have successfully created a group!')
            return redirect('public-chat')
    else:
        form = GroupChatForm()
    return render(request, 'chat/room_all.html', {'form': form})


def search(request):
    context = {}
    url_parameter = request.GET.get("q")
    if url_parameter:
        contacts = CustomUser.objects.filter(name__icontains=url_parameter)
        groups = GroupChat.objects.filter(users__in=[request.user.pk], room_name__icontains=url_parameter)
    else:
        contacts = CustomUser.objects.all().exclude(pk=request.user.pk)
        groups = GroupChat.objects.filter(users__in=[request.user.pk])
    context = {'contacts': contacts, 'groups': groups}
    if request.is_ajax():
        html = render_to_string(template_name='chat/search-results.html', context=context)
        data_dict = {'html_from_view': html}
        return JsonResponse(data=data_dict, safe=False)
    return render(request, "chat/room_all.html", context)


# async def history(request, room_id):
#     await Tortoise.init(**settings.TORTOISE_INIT)
#     chat_message = await ChatMessage.filter(room_id=room_id).order_by('created_at').values()
#     await Tortoise.close_connections()
#
#     return await sync_to_async(JsonResponse)(chat_message, safe=False)


class ChatListView(FormMixin, ListView):
    model = Thread
    template_name = 'chat/room_all.html'
    form_class = GroupChatForm

    def get_queryset(self):
        Thread.objects.by_user(self.request.user)

    def get_object(self):
        user_pub_id = self.kwargs.get('public_id')
        self.other_user = CustomUser.objects.get(public_id=user_pub_id)
        thread_obj = Thread.objects.get_or_create_personal_thread(self.request.user, self.other_user)
        if thread_obj is None:
            raise Http404
        return thread_obj

    def get_context_data(self, **kwargs):
        last_message = Message().last_message(self.request.user)
        """ Remember to set seen sms """
        user_pub_id = self.kwargs.get('public_id')
        current_user = CustomUser.objects.get(public_id=user_pub_id)
        groups_participated = GroupChat.objects.filter(users__in=[self.request.user.pk])
        users = CustomUser.objects.all()
        active_user = ActiveUser().current_active_users(user_pub_id)
        for g in groups_participated:
            if self.request.user in g.users.all():
                context = {
                    'me': self.request.user.name,
                    'messages': self.get_object().message_set.all(),
                    'users': users,
                    'thread': self.get_object(),
                    'other_user': self.other_user,
                    'groups_participated': groups_participated,
                    'current_user': current_user,
                    'active_user': active_user
                }
                return context
            else:
                context = {
                    'me': self.request.user.name,
                    'messages': self.get_object().message_set.all(),
                    'users': CustomUser.objects.all(),
                    'thread': self.get_object(),
                    'other_user': self.other_user,
                    'active_user': active_user
                }
                return context
        context = {
            'me': self.request.user.name,
            'messages': self.get_object().message_set.all(),
            'users': CustomUser.objects.all(),
            'thread': self.get_object(),
            'other_user': self.other_user,
            'current_user': current_user,
            'active_user': active_user
        }
        return context

    def post(self, request, **kwargs):
        self.object = self.get_object()
        thread = self.get_object()
        data = request.POST
        user = request.user
        text = data.get('message')
        Message.objects.create(sender=user, thread=thread, text=text)
        context = self.get_context_data(**kwargs)
        return context


class GroupChatCreate(CreateView):
    model = GroupChat
    template_name = 'chat/create_group.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(GroupChatCreate, self).get_context_data(**kwargs)
        context['form'] = GroupChatForm(request=self.request)
        return context

    def form_valid(self, form):
        user = CustomUser.objects.get(pk=self.request.user.id)
        group_name = form.cleaned_data.get('room_name')
        instance = GroupChat.objects.create(room_name=group_name)
        try:
            instance.users.add(user)
        except Exception as e:
            raise e
        return redirect("/")


class GroupChatUpdate(LoginRequiredMixin, UpdateView):
    model = GroupChat
    fields = ['room_name', 'users']

    def get_success_url(self):
        return reverse_lazy('public-chat', kwargs={'group_id': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Successfully updated the task.')
        return super().form_valid(form)


""" API Implementations """


class GroupView(generics.RetrieveAPIView):
    queryset = GroupChat.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)


class GroupCreateView(generics.CreateAPIView):
    serializer_class = GroupCreateSerializer


class GroupDetail(views.APIView):
    """ Retrieve, update or delete group object """

    def get_object(self, pk):
        try:
            return GroupChat.objects.get(pk=pk)
        except GroupChat.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        group = self.get_object(pk)
        serializer = GroupDetailSerializer(group, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        group = self.get_object(pk)
        serializer = GroupDetailSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        group = self.get_object(pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageView(generics.RetrieveAPIView):
    queryset = Message.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)


class MessageDetail(views.APIView):
    """ Gukurura, guhindura, no gukoresha messages in our API """

    def get_object(self, pk):
        try:
            return Message.objects.get(pk=pk)
        except Message.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        message = self.get_object(pk)
        serializer = MessageSerializer(message, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        message = self.get_object(pk)
        serializer = MessageSerializer(message, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        message = self.get_object(pk)
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
