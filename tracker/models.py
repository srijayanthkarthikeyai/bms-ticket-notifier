from django.db import models

# Create your models here.
from django.db import models

class TicketAlert(models.Model):
    user_email = models.EmailField()
    movie_name = models.CharField(max_length=255)
    bms_url = models.URLField(max_length=500, help_text="Direct BMS buy tickets link")
    theatre_filter = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Optional theatre filter (e.g. 'PVR', 'Srinivasa','Maruthi Theatre','Srinivasa Cine Complex','Geetha Annapurna Theatre','AVG Screens, 4K Dolby Atmos: Bhimavaram','Sri Padmalaya Cine Complex A/C 2K: Bhimavaram','Sri Vijayalakshmi Cine Complex: Bhimavaram')"
    )
    target_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="Target show date (e.g. 2026-09-12)"
    )
    is_active = models.BooleanField(default=True)
    alert_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.movie_name} -> {self.user_email}"
