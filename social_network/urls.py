from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('terms/', views.terms_view, name='terms'),
    path('accounts/', include('accounts.urls')),
    path('books/', include('books.urls')),
    path('events/', include('events.urls')),
    path('posts/', include('posts.urls')),
    path('connections/', include('connections.urls')),
    path('notifications/', include('notifications.urls')),
    path('dashboard/', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)