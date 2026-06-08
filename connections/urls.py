from django.urls import path
from . import views

app_name = 'connections'

urlpatterns = [
    path('send/<int:user_id>/', views.send_request_view, name='send_request'),
    path('accept/<int:request_id>/', views.accept_request_view, name='accept'),
    path('reject/<int:request_id>/', views.reject_request_view, name='reject'),
    path('requests/', views.friend_requests_view, name='requests'),
    path('friends/', views.friends_list_view, name='friends'),
    path('unfriend/<int:user_id>/', views.unfriend_view, name='unfriend'),
]