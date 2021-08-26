from django.urls import path

from chat import views
from users import views as users_views

urlpatterns = [
    path('', views.home, name='home'),
    path('ws/chat/<uuid:public_id>/', views.ChatListView.as_view(), name='room'),
    path('ws/chat/<int:group_id>/', views.room, name='public-chat'),
    path('ws/chat/create-group', views.GroupChatCreate.as_view(), name='public-chat-create'),
    path('ws/chat/add-user/<int:pk>/', views.GroupChatUpdate.as_view(), name='add-user'),
    path('search/', views.search, name='search'),

    # Trials
    # path('history/<str:room_id>', views.history, name='history'),
    path('unauthorized/', views.unauthorized, name='unauthorized'),

    # API
    path('api/groups/', views.GroupView.as_view(), name='groups'),
    path('api/messages/', views.MessageView.as_view(), name='messages'),
    path('api/create-group/', views.GroupCreateView.as_view(), name='create-group'),
    path('api/group/<int:pk>/', views.GroupDetail.as_view(), name='update-group'),
    path('api/message/<int:pk>', views.MessageDetail.as_view(), name='update-message'),
]
