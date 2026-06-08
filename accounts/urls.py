from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/', views.verify_email_notice_view, name='verify_email'),
    path('verify-email/<uidb64>/<token>/', views.verify_email_view, name='verify_email_confirm'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.user_profile_view, name='user_profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('report/', views.report_issue_view, name='report_issue'),
]