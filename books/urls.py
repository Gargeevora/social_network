from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list_view, name='list'),
    path('<int:pk>/', views.book_detail_view, name='detail'),
    path('sell/', views.sell_book_view, name='sell'),
    path('<int:pk>/request/', views.send_purchase_request_view, name='send_request'),
    path('requests/<int:request_id>/approve/', views.approve_request_view, name='approve_request'),
    path('requests/<int:request_id>/reject/', views.reject_request_view, name='reject_request'),
    path('my-books/', views.my_books_view, name='my_books'),
    path('<int:pk>/delete/', views.delete_book_view, name='delete'),
    path('<int:pk>/edit/', views.edit_book_view, name='edit'),
]