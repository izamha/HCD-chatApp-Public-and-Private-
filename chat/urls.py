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

    # API endpoints

    # Groups
    path('api/groups/', views.GroupView.as_view(), name='groups'),
    path('api/create-group/', views.GroupCreateView.as_view(), name='create-group'),
    path('api/group/<int:pk>/', views.GroupDetail.as_view(), name='update-group'),

    # User
    path('api/users/', views.AllUsers.as_view(), name='users'),
    path('api/user/<int:pk>/', views.UserDetail.as_view(), name='user'),
    path('api/create-user/', views.UserCreateView.as_view(), name='create-user'),
    path('api/user/<int:pk>', views.MessageDetail.as_view(), name='update-user'),

    # Message
    path('api/messages/', views.MessageView.as_view(), name='messages'),
    path('api/message/<int:pk>', views.MessageDetail.as_view(), name='update-message'),
    path('api/create-message/', views.MessageCreateView.as_view(), name='create-message'),
]
