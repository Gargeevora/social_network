from django.contrib import admin
from .models import Complaint, AuditLog, UserComplaint

admin.site.register(Complaint)
admin.site.register(AuditLog)
admin.site.register(UserComplaint)