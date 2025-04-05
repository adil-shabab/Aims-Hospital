# core/templatetags/custom_filters.py

from django import template
from django.utils.timesince import timesince
from datetime import datetime
import re


register = template.Library()

@register.filter
def arrow_direction(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return 'down'  # default to 'down' if value is not an integer
    return 'up' if value >= 0 else 'down'




@register.filter(name='endswith')
def endswith(value, arg):
    """Checks if the value ends with the given argument"""
    return value.endswith(arg)


@register.filter
def divide(value, divisor):
    try:
        return float(value) / divisor
    except (ValueError, ZeroDivisionError):
        return value




@register.filter
def format_doctor_name(doctor_name):
    if doctor_name.startswith("Ms."):
        return doctor_name  # Remove "Ms. " from the name
    elif doctor_name == "mshsh":
        return doctor_name  # Return "mshsh" as is
    else:
        return f"Dr. {doctor_name}"  # Prepend "Dr." for other names



@register.filter
def time_since_string(date_string):
    """
    Parses a date string in the format 'dd-mm-yyyy' and returns a "time ago" format.
    """
    try:
        # Parse the string into a datetime object
        target_date = datetime.strptime(date_string, "%d-%m-%Y")
        # Calculate the "time since" difference
        return timesince(target_date)
    except ValueError:
        # Return the date string as-is if there's a parsing error
        return date_string











@register.filter
def youtube_video_id(url):
    """
    Extracts the YouTube video ID from a given URL.
    """
    youtube_regex = re.compile(
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&?/]+)'
    )
    match = youtube_regex.search(url)
    if match:
        return match.group(1)  # Return the video ID
    return None  # Return None if no match is found