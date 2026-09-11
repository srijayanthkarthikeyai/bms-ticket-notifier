from django.contrib import admin
from .models import TicketAlert

@admin.register(TicketAlert)
class TicketAlertAdmin(admin.ModelAdmin):
    list_display = ('movie_name', 'user_email', 'is_active', 'alert_sent', 'created_at', 'last_checked_at')
    list_filter = ('is_active', 'alert_sent')
    search_fields = ('movie_name', 'user_email')