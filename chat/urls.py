from django.urls import path

from chat import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ws/chat/<uuid:public_id>/', views.ChatListView.as_view(), name='room'),
    path('ws/chat/<int:group_id>/', views.room, name='public-chat'),
    path('ws/chat/create-group', views.GroupChatCreate.as_view(), name='public-chat-create'),
    path('search/', views.search, name='search'),

    # Trials
    # path('history/<str:room_id>', views.history, name='history'),
    path('unauthorized/', views.unauthorized, name='unauthorized'),
]
