from django.urls import path
from .views import index,delete_alert

urlpatterns = [
    path('', index, name='index'),
    path('delete/<int:alert_id>/',delete_alert, name='delete_alert'),
]