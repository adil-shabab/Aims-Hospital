# core/utils.py

from twilio.rest import Client
from django.conf import settings
import requests




def send_sms(phone_number, message):
    
    print("Sending Sms")


# def send_whatsapp(to_number, message):
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

#     try:
#         client.messages.create(
#             body=message,
#             from_='whatsapp:+14155238886',  # Your Twilio WhatsApp-enabled number
#             to=f'whatsapp:{to_number}'
#         )
#     except Exception as e:
#         # Handle the exception (log it, raise it, etc.)
#         print(f"Failed to send WhatsApp message: {e}")
#         return None





