from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list_view, name='list'),
    path('<int:pk>/', views.event_detail_view, name='detail'),
    path('announce/', views.announce_event_view, name='announce'),
    path('request-access/', views.request_representative_view, name='request_representative'),
    path('<int:pk>/interest/', views.toggle_interest_view, name='toggle_interest'),
    path('<int:pk>/edit/', views.edit_event_view, name='edit'),
]