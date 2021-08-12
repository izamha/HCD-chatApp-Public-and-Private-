from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import ListView, CreateView
from django.views.generic.edit import FormMixin

from .forms import GroupChatForm
from .models import Message, CustomUser, Thread, GroupChat, GroupChatMessage


@login_required
def home(request):
    instance = Message()
    last_message = instance.last_message(request.user)
    unseen_message = instance.count_unseen_messages(request.user)
    all_users = sorted(CustomUser.objects.all(), key=lambda inst: inst.date_joined)[::-1]
    groups_participated = GroupChat.objects.filter(users__in=[request.user.pk])
    print(groups_participated)
    context = {
        'title': 'Home',
        'last_message': last_message,
        'all_users': all_users,
        'groups_participated': groups_participated,
        'unseen_message': unseen_message,
    }
    return render(request, 'chat/home.html', context)


def get_members(group_id=None, group_obj=None, user=None):
    """ Get all participants that belong to a certain group """

    if group_id:
        chat_group = GroupChat.objects.get(id=id)
    else:
        chat_group = group_obj

    temp_members = []
    for member in chat_group.users.values_list('name', flat=True):
        if member != user:
            temp_members.append(member.title())
    temp_members.append('You')
    return ', '.join(temp_members)


@login_required
def room(request, group_id):
    all_groups = GroupChat.objects.all()
    for group in all_groups:
        if request.user in group.users.all():
            try:
                chat_group = GroupChat.objects.get(id=group_id)
                # TODO: Make sure a user is assigned to an existing group
                assigned_groups = list(chat_group.users.values_list('id', flat=True))
                groups_participated = GroupChat.objects.filter(users__in=[request.user.pk])
                group_messages = GroupChatMessage.objects.filter(room_name__in=[group_id])
                for g in groups_participated:
                    if request.user in g.users.all():
                        context = {
                            'chat_group': chat_group,
                            'members': get_members(group_obj=chat_group, user=request.user.username),
                            'all_group_members': GroupChat.objects.get(pk=group_id).users.all().count(),
                            'groups_participated': groups_participated,
                            'users': CustomUser.objects.all(),
                            'group_messages': group_messages
                        }
                        return render(request, 'chat/room_all.html', context)
                    else:
                        return render(request, 'chat/unauthorized.html')
            except:
                return render(request, 'chat/unauthorized.html')
        else:
            return HttpResponseRedirect(reverse("chat:unauthorized"))


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
        contacts = CustomUser.objects.all()
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
                }
                return context
            else:
                context = {
                    'me': self.request.user.name,
                    'messages': self.get_object().message_set.all(),
                    'users': CustomUser.objects.all(),
                    'thread': self.get_object(),
                    'other_user': self.other_user,
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
        context['form'] = GroupChatForm()
        return context
