from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home_view, name='home'),
    path('users/', views.users_view, name='users'),
    path('users/block/<int:user_id>/', views.block_user_view, name='block_user'),
    path('complaints/', views.complaints_view, name='complaints'),
    path('complaints/<int:complaint_id>/resolve/', views.resolve_complaint_view, name='resolve_complaint'),
    path('complaints/<int:complaint_id>/dismiss/', views.dismiss_complaint_view, name='dismiss_complaint'),
    path('representative-requests/', views.representative_requests_view, name='representative_requests'),
    path('representative-requests/<int:request_id>/approve/', views.approve_representative_view, name='approve_representative'),
    path('representative-requests/<int:request_id>/reject/', views.reject_representative_view, name='reject_representative'),
    path('audit-log/', views.audit_log_view, name='audit_log'),
    path('users/remove-representative/<int:user_id>/', views.remove_representative_view, name='remove_representative'),
    path('user-complaints/', views.user_complaints_view, name='user_complaints'),
    path('user-complaints/<int:complaint_id>/resolve/', views.resolve_user_complaint_view, name='resolve_user_complaint'),
    path('user-complaints/<int:complaint_id>/', views.user_complaint_detail_view, name='user_complaint_detail'),
    path('colleges/', views.colleges_view, name='colleges'),
    path('colleges/add/', views.add_college_view, name='add_college'),
    path('colleges/<int:college_id>/generate-invite/', views.generate_invite_view, name='generate_invite'),
    path('college-admin/', views.college_admin_home_view, name='college_admin_home'),
]