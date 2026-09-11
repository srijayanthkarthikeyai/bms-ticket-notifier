from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import TicketAlertForm
from .models import TicketAlert
from .utils import normalize_bms_url

def index(request):
    if request.method == 'POST':
        form = TicketAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            
            # Auto-convert synopsis URL to /buytickets/ format
            alert.bms_url = normalize_bms_url(alert.bms_url)
            alert.save()
            messages.success(
                request, 
                f"Alert registered! Tracking URL: {alert.bms_url}"
            )
            return redirect('index')
    else:
        form = TicketAlertForm()
    alerts = TicketAlert.objects.order_by('-created_at')[:10]
    return render(request, 'tracker/index.html', {'form': form, 'alerts': alerts})

def delete_alert(request, alert_id):
    if request.method == 'POST':
        alert = get_object_or_404(TicketAlert, id=alert_id)
        alert.delete()
        messages.success(request, "Alert removed successfully.")
    return redirect('index')