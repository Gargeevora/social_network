from django.contrib import admin
from .models import Book, PurchaseRequest


admin.site.register(Book)
admin.site.register(PurchaseRequest)