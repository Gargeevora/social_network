from django.contrib import admin
from .models import Event, RepresentativeRequest


class RepresentativeRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'requested_at']
    list_filter = ['status']
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        for rep_request in queryset:
            rep_request.status = 'approved'
            rep_request.save()
            rep_request.user.is_college_representative = True
            rep_request.user.save()
        self.message_user(request, 'Selected requests approved successfully.')
    approve_requests.short_description = 'Approve selected requests'


admin.site.register(Event)
admin.site.register(RepresentativeRequest, RepresentativeRequestAdmin)