# core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from .utils import send_sms
from datetime import timedelta
from .tasks import *

@receiver(post_save, sender=Appointment)
def send_payment_success_sms(sender, instance, created, **kwargs):
    pass
        
        
        
        
        

@receiver(post_save, sender=HealthCheckupBooking)
def send_payment_success_sms(sender, instance, created, **kwargs):
    pass







@receiver(post_save, sender=Appointment)
def create_meeting_link(sender, instance, created, **kwargs):
    pass