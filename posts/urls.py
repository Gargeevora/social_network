from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('create/', views.create_post_view, name='create'),
    path('<int:pk>/like/', views.like_post_view, name='like'),
    path('<int:pk>/comment/', views.add_comment_view, name='comment'),
    path('<int:pk>/delete/', views.delete_post_view, name='delete'),
]