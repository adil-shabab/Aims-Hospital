from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from .models import Appointment
from django.utils import timezone
from .utils import send_sms
import logging
from .models import *

logger = logging.getLogger(__name__)

def send_daily_doctor_appointments_sms():
    """
    Sends daily SMS to doctors with their appointments for the day.
    """
    # Get today's date
    print("Daily Doctor message Schedule")
    today = timezone.now().date()

    # Find all appointments for today
    appointments_today = Appointment.objects.filter(date=today)

    # Dictionary to group appointments by doctor
    doctor_appointments = {}

    # Group appointments by doctor
    for appointment in appointments_today:
        doctor = appointment.selected_doctor
        if doctor not in doctor_appointments:
            doctor_appointments[doctor] = []
        doctor_appointments[doctor].append(appointment)

    # Send SMS to each doctor
    for doctor, appointments in doctor_appointments.items():
        # Format the appointment details
        appointment_details = "\n".join([
            f"Patient: {appt.patient.name}, Time: {appt.schedule.start_time.strftime('%I:%M %p')}"
            for appt in appointments
        ])

        # Create the message for the doctor
        doctor_message = (
            f"Dear Dr. {doctor.name},\n\n"
            f"You have the following appointments today:\n"
            f"{appointment_details}\n\n"
            "Please make sure to attend on time."
        )

        # Format the doctor's phone number
        doctor_phone = format_phone_number(doctor.number)

        # Send the SMS to the doctor
        send_sms(doctor_phone, doctor_message)
        logger.info(f"Sending daily appointments SMS to Dr. {doctor.name} at {doctor.number}")


def format_phone_number(phone_number):
    """Ensure the phone number has the +91 prefix."""
    if not phone_number.startswith('+91'):
        return '+91' + phone_number
    return phone_number




def schedule_sms_one_hour_before(appointment):
    print("One Hour Before")
    scheduler = BackgroundScheduler()

    # Combine the date and time fields into a single datetime object
    appointment_time = datetime.combine(appointment.date, appointment.schedule.start_time)

    # Subtract 1 hour from the appointment time
    reminder_time = appointment_time - timedelta(hours=1, minutes=0)
    
    print("Reminder Time")

    logger.info(f"Scheduling SMS for one hour before: {reminder_time}")

    # Create a trigger for the scheduled job
    trigger = DateTrigger(run_date=reminder_time)

    # Schedule the job to send the SMS one hour before the appointment
    scheduler.add_job(
        send_sms_to_patient_one_hour_before,
        trigger=trigger,
        args=[appointment.id]
    )

    # Start the scheduler
    scheduler.start()

def send_sms_to_patient_one_hour_before(appointment_id):
    print("ONNNNNNe")


    def format_phone_number(phone_number):
        """Ensure the phone number has the +91 prefix."""
        if not phone_number.startswith('+91'):
            return '+91' + phone_number
        return phone_number

    appointment = Appointment.objects.get(id=appointment_id)
    message = (
        f"Dear {appointment.patient.name},\n\n"
        f"This is a reminder that your appointment with Dr. {appointment.selected_doctor.name} "
        f"is scheduled to start in one hour at {appointment.schedule.start_time.strftime('%I:%M %p')}."
    )


    formatted_user_number = format_phone_number(appointment.patient.phone_number)
    send_sms(formatted_user_number, message)

    logger.info(f"Sending one-hour-before SMS to {appointment.patient.phone_number}")


def schedule_sms_on_morning_of_appointment(appointment):
    print("Morning Message schedule") #here console iscoming after booking appointment
    scheduler = BackgroundScheduler()

    # Combine appointment.date with the specific time (11 AM)
    reminder_time_morning = datetime.combine(appointment.date, datetime.min.time()).replace(hour=10, minute=0, second=0)

    logger.info(f"Scheduling SMS for 11 AM on the day of the appointment: {reminder_time_morning}")

    # Create a trigger for the scheduled job
    trigger = DateTrigger(run_date=reminder_time_morning)

    # Schedule the job to send the SMS at 11 AM on the day of the appointment
    scheduler.add_job(
        send_sms_on_morning_of_appointment,
        trigger=trigger,
        args=[appointment.id]
    )

    # Start the scheduler
    scheduler.start()


def send_sms_on_morning_of_appointment(appointment_id):

    print("Morning") # this isnot coming in 12:28PM
    def format_phone_number(phone_number):
        """Ensure the phone number has the +91 prefix."""
        if not phone_number.startswith('+91'):
            return '+91' + phone_number
        return phone_number

    
    appointment = Appointment.objects.get(id=appointment_id)
    message = (
        f"Dear {appointment.patient.name},\n\n"
        f"This is a reminder that your appointment with Dr. {appointment.selected_doctor.name} "
        f"is scheduled today at {appointment.schedule.start_time.strftime('%I:%M %p')}."
    )



    formatted_user_number = format_phone_number(appointment.patient.phone_number)
    send_sms(formatted_user_number, message)

    logger.info(f"Sending morning-of-appointment SMS to {appointment.patient.phone_number}")





def schedule_sms_one_hour_before(appointment):
    print("One Hour Before")
    scheduler = BackgroundScheduler()
    

    # Combine the date and time fields into a single datetime object
    appointment_time = datetime.combine(appointment.date, appointment.schedule.start_time)

    # Subtract 1 hour from the appointment time
    reminder_time = appointment_time - timedelta(hours=1, minutes=0)
    
    print("Reminder Time")

    logger.info(f"Scheduling SMS for one hour before: {reminder_time}")

    # Create a trigger for the scheduled job
    trigger = DateTrigger(run_date=reminder_time)

    # Schedule the job to send the SMS one hour before the appointment
    scheduler.add_job(
        send_sms_to_patient_one_hour_before,
        trigger=trigger,
        args=[appointment.id]
    )

    # Start the scheduler
    scheduler.start()






logger = logging.getLogger(__name__)

def schedule_meeting(appointment):
    """
    Schedule the meeting creation 5 minutes before the scheduled appointment time.
    If the time difference is less than 5 minutes, generate the meeting link immediately.
    """
    scheduler = BackgroundScheduler()

    # Convert the appointment date from string to datetime.date object
    appointment_date = datetime.strptime(appointment.date, "%Y-%m-%d").date()
    appointment_time = datetime.combine(appointment_date, appointment.schedule.start_time)

    # Subtract 5 minutes to get reminder time
    reminder_time = appointment_time - timedelta(minutes=5)

    # Calculate the time difference between now and the reminder time
    time_diff = reminder_time - datetime.now()

    if time_diff.total_seconds() <= 0:
        # If less than or equal to 0, generate the link immediately
        logger.warning(f"Time difference is less than 5 minutes. Generating meeting link immediately for appointment {appointment.id}.")
        generate_meeting_link(appointment.id)
    else:
        # Log the scheduled job details
        logger.info(f"Scheduling SMS for 5 minutes before: {reminder_time}")

        # Create a trigger for the scheduled job
        trigger = DateTrigger(run_date=reminder_time)

        # Schedule the job to send the SMS or perform other actions 5 minutes before the appointment
        scheduler.add_job(
            generate_meeting_link,
            trigger=trigger,
            args=[appointment.id]
        )

        # Start the scheduler
        scheduler.start()

    logger.info(f"Job scheduled or executed for appointment: {appointment.id}")




import time
import jwt
import requests
from datetime import datetime
import time
import hmac
import hashlib
import base64
import requests
from django.conf import settings
import json




# Replace with your Zego credentials
APP_ID = '770866260'
SECRET = '098d0eb177ccee863a5a23bee2667aa8'
BASE_URL = 'https://api.zego.im/v1/meeting'


def generate_token():
    # Generate a token for authentication
    # This is a simple example; you should use a proper method to generate tokens
    now = int(time.time())
    token = f"{APP_ID}:{SECRET}:{now}"
    return token






def create_meeting(meeting_title, meeting_duration):
    token = generate_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token
    }

    # Meeting start time (current time)
    start_time = int(time.time())
    # Meeting end time (current time + duration in seconds)
    end_time = start_time + meeting_duration

    payload = {
        'title': meeting_title,
        'start_time': start_time,
        'end_time': end_time,
        'user_id': 'user123',  # Replace with actual user ID
        'user_name': 'User Name'  # Replace with actual user name
    }

    response = requests.post(BASE_URL + '/create', headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        meeting_info = response.json()
        print("Meeting created successfully!")
        print("Meeting ID:", meeting_info['meeting_id'])
        print("Join Link:", meeting_info['join_url'])
    else:
        print("Error creating meeting:", response.text)

def create_zego_meeting(appointment):
    """
    Create a video meeting using Zego API with dynamic duration.
    Args:
        appointment (object): The appointment object containing start_time and end_time
    Returns:
        str: The meeting URL or error message.
    """

    room_id = appointment.id
    user_id = appointment.patient.name
    create_meeting("Doctor", 60)


    # Assuming appointment.schedule.start_time and appointment.schedule.end_time are both datetime.time objects
    # start_time = appointment.schedule.start_time
    # end_time = appointment.schedule.end_time

    # # Combine the times with a date (arbitrary date, e.g., '2000-01-01') to make them datetime objects
    # start_datetime = datetime.combine(datetime.min, start_time)
    # end_datetime = datetime.combine(datetime.min, end_time)

    # # Calculate the difference in time
    # time_difference = end_datetime - start_datetime

    # # Convert the time difference to minutes
    # slot_duration_minutes = time_difference.total_seconds() / 60

    # endpoint = f"{ZEGO_BASE_URL}createMeeting"
    # headers = {
    #     "Authorization": f"Bearer {generate_zego_token()}",
    #     "Content-Type": "application/json",
    # }
    # data = {
    #     "topic": "Video Consultation",
    #     "start_time": int(time.time() + 300),  # 5 minutes before the actual start time
    #     "duration": slot_duration_minutes,  # Duration passed dynamically from the appointment slot
    #     "host_user_id": appointment.selected_doctor.id,  # Replace with the actual doctor ID
    # }

    # try:
    #     response = requests.post(endpoint, json=data, headers=headers)
    #     response.raise_for_status()  # Raise an error for HTTP codes >= 400
    #     meeting_data = response.json()
    #     return meeting_data.get("meeting_url")  # Return the meeting URL if present
    # except requests.RequestException as e:
    #     error_message = f"Error creating meeting: {e}"
    #     return error_message






def end_zego_meeting(meeting_id):
    """
    Ends a Zego meeting and stops anyone from joining.
    Args:
        meeting_id (str): The ID of the meeting to end.
    """
    endpoint = f"{ZEGO_BASE_URL}endMeeting"  # Adjust endpoint according to Zego documentation
    headers = {
        "Authorization": f"Bearer {generate_zego_token()}",
        "Content-Type": "application/json",
    }
    data = {
        "meeting_id": meeting_id,  # The meeting ID to end
    }

    try:
        response = requests.post(endpoint, json=data, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP codes >= 400
        print(f"Meeting {meeting_id} has been ended.")
    except requests.exceptions.RequestException as e:
        print(f"Error ending Zego meeting: {e}")



def generate_meeting_link(appointment_id):
    print("Working")
    appointment = Appointment.objects.get(id=appointment_id)
    meeting_url = create_zego_meeting(appointment)
    appointment.is_video_active = True
    appointment.video_link = meeting_url
    appointment.save()
    logger.info(f"Sending one-hour-before SMS to {appointment.patient.phone_number}")
