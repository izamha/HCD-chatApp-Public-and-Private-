from django.contrib import admin
from django.core.cache import cache
from django.core.paginator import Paginator
from .models import Thread, Message, GroupChat, GroupChatMessage

admin.site.register(Thread)
admin.site.register(Message)


class GroupChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'group_name']
    search_fields = ['id', 'group_name']
    list_display_links = ['id']

    class Meta:
        model = GroupChat


admin.site.register(GroupChat, GroupChatAdmin)


# Resource: http://masnun.rocks/2017/03/20/django-admin-expensive-count-all-queries/
class CachingPaginator(Paginator):
    def _get_count(self):

        if not hasattr(self, "_count"):
            self._count = None

        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)

            except:
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


class GroupChatMessageAdmin(admin.ModelAdmin):
    list_filter = ['room_name', 'user', "created_at"]
    list_display = ['room_name', 'user', 'text', "created_at"]
    search_fields = ['room_name', 'user', 'text']
    # readonly_fields = ['id', 'user', 'created_at']

    show_full_result_count = False
    paginator = CachingPaginator

    class Meta:
        model = GroupChatMessage


admin.site.register(GroupChatMessage, GroupChatMessageAdmin)

# class ChatGroupAdmin(admin.ModelAdmin):
#     """ Enable Chart Group admin """
#     list_display = ('id', 'group_name', 'group_icon', 'created_at', 'date_modified')
#     list_filter = ('id', 'group_name', 'group_icon', 'created_at', 'date_modified')
#     list_display_links = ('group_name',)
