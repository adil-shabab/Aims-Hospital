from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .forms import *
from .models import *
from django.contrib import messages as msg
from django.utils.text import slugify
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpResponseBadRequest
import datetime
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.conf import settings
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
import logging
from rest_framework import status
from rest_framework.views import APIView
import uuid
from .filters import RazorpayPaymentDetailsFilter
from django_filters.views import FilterView
from django.db.models import Sum
from datetime import timedelta  # Import timedelta
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.urls import reverse
from django.utils.dateformat import DateFormat
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import ExtractMonth

from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime


from django.http import Http404
import urllib.parse
from django.db.models import Case, When, Value, IntegerField
from django.utils.timezone import make_aware, get_current_timezone



# URLs to redirect to the homepage
redirect_urls = [
    '/visiting-instructions/',
    '/admission/',
    '/surgery/'
    '/dermatology-department/',
    '/nutrition-and-dietetics/',
    '/best-superspeciality-hospital/',
    '/bariatric-surgery/',
    '/plastic-surgery-department/',
    '/exploring-aesthetic-treatments-for-beauty-enhancements-and-skin-rejuvenation/',

]

def custom_404_view(request, exception):
    # Check if the requested path is in the redirect list
    if request.path in redirect_urls:
        return redirect('homepage')  # Redirect to the homepage

    return render(request, '404.html', status=404)

@login_required(login_url='login')
def cancel_appointment(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    
    
    try:
        appointment = Appointment.objects.get(id=pk)
        appointment.status = 'CANCELLED'
        appointment.save()
        msg.success(request, "Appointment Cancelled")
    except Appointment.DoesNotExist:
        msg.error(request, "Appointment does not exist.")

    # Redirect back to the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    




def check_new_appointments(request):
    # Fetch notifications that are unread and not yet alarmed
    unread_notifications = Notification.objects.filter(type='appointment', read_status=False, is_alarmed=False)
    
    # Count the number of such notifications
    count = unread_notifications.count()
    
    # Get the IDs of the notifications
    notification_ids = list(unread_notifications.values_list('id', flat=True))
    
    return JsonResponse({'new_appointments': count, 'notification_ids': notification_ids})


@csrf_exempt
@require_POST
def update_alarm_status(request):
    try:
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])
        
        # Update the is_alarmed field to True for the notifications
        Notification.objects.filter(id__in=notification_ids).update(is_alarmed=True)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required(login_url='login')
def dashboard(request):

    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')



    patients_by_department = Patient.objects.values('appointment__selected_doctor__department__title')\
        .annotate(count=Count('id'))\
        .order_by('appointment__selected_doctor__department__title')

    department_data = [
        {
            'department': item['appointment__selected_doctor__department__title'] if item['appointment__selected_doctor__department__title'] else 'Unknown Department',
            'count': item['count']
        } for item in patients_by_department if item['appointment__selected_doctor__department__title']
    ]
    
    patient_count = Patient.objects.all().count()
    doctor_count = Doctor.objects.filter(status = True).count()
    appointment_count = Appointment.objects.all().count()
    department_count = Department.objects.filter(status = True).count()
    blog_count = Blog.objects.filter(status = True).count()
    message_count = Message.objects.all().count()


    appointments = Appointment.objects.all().order_by('-created_at')[:10]



    context = {
        'patient_count': patient_count,
        'appointments' : appointments,
        'doctor_count' : doctor_count,
        'appointment_count' : appointment_count,
        'department_count' :  department_count,
        'blog_count' : blog_count,
        'message_count' : message_count,
        'department_data_json': json.dumps(department_data),
    }

    return render(request, 'backend/dashboard.html', context)
    



# message view 
@login_required(login_url='login')
def notifications(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    notifications = Notification.objects.all().order_by('-created_at')
    context = {'notifications': notifications,}
    return render(request, 'backend/notifications.html', context)





@login_required(login_url='login')
def gallery_list(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    gallery = Gallery.objects.all().order_by('-created_at')
    return render(request, 'backend/gallery.html', {'gallery': gallery})



# Create View for Gallery
@login_required(login_url='login')
def create_gallery(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            msg.success(request, "Gallery Image Uploaded")
            return redirect('gallery_list')  # Redirect to the gallery list page after creation
    else:
        form = GalleryForm()
    return render(request, 'backend/gallery-form.html', {'form': form})





# Create View for Gallery
@login_required(login_url='login')
def create_gallery_link(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            msg.success(request, "Gallery Uploaded")
            return redirect('gallery_list')  # Redirect to the gallery list page after creation
    else:
        form = GalleryForm()
    return render(request, 'backend/gallery-link.html', {'form': form})





# Delete View for Gallery
@login_required(login_url='login')
def delete_gallery(request, gallery_id):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    gallery = get_object_or_404(Gallery, id=gallery_id)
    gallery.delete()
    msg.success(request, "Gallery Image Deleted Successfully")
    return redirect('gallery_list')  # Redirect to the gallery list page after deletion






    


# department view 
@login_required(login_url='login')  
def ad_banners(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    ad_banners = AdBanner.objects.all()
    context ={ 'ad_banners': ad_banners }
    return render(request, 'backend/ad-banners.html', context)



@login_required(login_url='login')
def create_adbanner(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = AdBannerForm(request.POST, request.FILES)
        if form.is_valid():
            msg.success(request, "Ad Banner Created Successfully")
            adbanner = form.save()
            # After saving, you can redirect to the list of AdBanners or any other appropriate page
            return redirect('ad_banners')  # Replace with the correct URL name
    else:
        form = AdBannerForm()

    context = {
        'form': form,
    }
    return render(request, 'backend/create-ad-banner.html', context)




@login_required(login_url='login')
def update_adbanner(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    banner = get_object_or_404(AdBanner, slug=slug)
    if request.method == 'POST':
        form = AdBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            msg.success(request, "Ad Banner Updated Successfully")
            return redirect('ad_banners')  # Replace with the correct URL name for your list view
    else:
        form = AdBannerForm(instance=banner)

    context = {
        'form': form,
        'banner': banner,
    }
    return render(request, 'backend/update-ad-banner.html', context)



@login_required(login_url='login')
def delete_adbanner(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    adbanner = get_object_or_404(AdBanner, slug=slug)
    adbanner.delete()
    msg.success(request, "Ad Banner Deleted Successfully")
    return redirect('ad_banners')  # Replace with the correct URL name for your list view



# banner view 
@login_required(login_url='login')
def banners(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    banners = Banner.objects.all()
    context = {'banners': banners}
    return render(request, 'backend/banners.html',context)


@login_required(login_url='login')
def create_banner(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            msg.success(request, "Banner Created Successfully")
            return redirect('banners')  
        else:
           msg.error(request, 'Failed to Create banner. Please check the form for errors.')
            
    else:
        form = BannerForm()
    return render(request, 'backend/create-banner.html', {'form': form})
    

@login_required(login_url='login')
def update_banner(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    banner = get_object_or_404(Banner, id=pk)
    print(type(banner.status))
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            msg.success(request, 'Banner Updated Successfully')
            return redirect('banners')  
        else:
            msg.error(request, 'Failed to update banner. Please check the form for errors.')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'backend/update-banner.html', {'form': form, 'banner': banner})




@login_required(login_url='login')
def delete_banner(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    try:
        banner = Banner.objects.get(pk=pk)
        banner.delete()
        msg.success(request, 'Banner deleted successfully.')
        return redirect('banners')
    except Banner.DoesNotExist:
        msg.error(request, 'Banner not found.')
        return redirect('banners')















# doctors view 
@login_required(login_url='login')
def doctors(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')

    doctors = Doctor.objects.annotate(
        is_priority_null=Case(
            When(priority=None, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('is_priority_null', 'priority')
    context ={ 'doctors': doctors }
    return render(request, 'backend/doctors.html', context)


@login_required(login_url='login')
def create_doctor(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.save()
            msg.success(request, "Doctor Added Successfully")
            return redirect('doctors')  # Replace with your redirect URL
        
        else:
            error_messages = "Please correct the errors below:<br>"
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages += f"{field}: {error}<br>"
            msg.error(request, error_messages)
    form = DoctorForm()
    return render(request, 'backend/create-doctor.html', {'form': form})


@login_required(login_url='login')
def update_doctor(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    doctor = Doctor.objects.get(slug=slug)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.save()
            msg.success(request, "Doctor Updated Successfully")
            return redirect('doctors')  # Replace with your redirect URL
        else:
            error_messages = "Please correct the errors below:<br>"
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages += f"{field}: {error}<br>"
            msg.error(request, error_messages)
    else:
        form = DoctorForm(instance =doctor)
    return render(request, 'backend/update-doctor.html', {'form': form, 'doctor':doctor})


@login_required(login_url='login')
def delete_doctor(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    try:
        doctor = Doctor.objects.get(slug=slug)
        doctor.delete()
        msg.success(request, 'Doctor deleted successfully.')
        return redirect('doctors')
    except Doctor.DoesNotExist:
        msg.error(request, 'doctor not found.')
        return redirect('doctor')



@login_required(login_url='login')
def create_monthly_timing(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form2 = MonthlyTimeForm(request.POST)
        if form2.is_valid():
            timing = form2.save(commit=False)
            doctor = get_object_or_404(Doctor, id=pk)
            timing.doctor = doctor  # Assign the doctor to the timing instance
            timing.remaining_slots = timing.slot


            # Check if the start date is today or in the future
            if timing.date < timezone.now().date():
                msg.error(request, "The date must be today or in the future. Past dates are not allowed.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            # Check if the start time is less than end time
            if timing.start_time >= timing.end_time:
                msg.error(request, "Ending Time must be greater than Starting Time.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            # Check if the same doctor has any other timing in this time range
            overlapping_timings = MonthlyTiming.objects.filter(
                doctor=doctor,
                date=timing.date,
                start_time__lt=timing.end_time,
                end_time__gt=timing.start_time
            )

            if overlapping_timings.exists():
                msg.error(request, "The doctor already has another timing in this time range. Please choose a different time.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            # If all checks pass, save the timing
            timing.save()
            msg.success(request, "Timing Updated Successfully")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            # Gather all form errors
            error_messages = "Please correct the errors below:\n"
            for field, errors in form2.errors.items():
                for error in errors:
                    error_messages += f"{field}: {error}\n"
            msg.error(request, error_messages)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_timing_api(request, doctor_slug):
    doctor = get_object_or_404(Doctor, slug=doctor_slug)
    selected_slots = request.data.get('selected_slots', [])
    slot_count = request.data.get('slot', 1)

    if not selected_slots:
        return Response({"error": "No slots selected"}, status=status.HTTP_400_BAD_REQUEST)

    for slot in selected_slots:
        day, times = slot.split(' ', 1)
        start_time, end_time = times.split('-')

        # Convert strings to time objects
        start_time_obj = datetime.datetime.strptime(start_time.strip(), '%H:%M').time()
        end_time_obj = datetime.datetime.strptime(end_time.strip(), '%H:%M').time()

        # Check for overlapping times
        overlapping_timings = AvailableTime.objects.filter(
            doctor=doctor,
            day=day,
            status='active',
            start_time__lt=end_time_obj,
            end_time__gt=start_time_obj
        )

        if overlapping_timings.exists():
            return Response(
                {"error": f"The doctor already has another timing in this time range for {day}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the available time object
        AvailableTime.objects.create(
            doctor=doctor,
            day=day,
            start_time=start_time_obj,
            end_time=end_time_obj,
            slot=slot_count,
            status='active',
            remaining_slots=slot_count
        )

    return Response({"success": "Timings added successfully"}, status=status.HTTP_201_CREATED)



            
@login_required(login_url='login')
def create_timing(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    doctor = get_object_or_404(Doctor, slug=slug)
    timings = AvailableTime.objects.filter(doctor=doctor, status='active').order_by('day', 'start_time')
    monthly_timing = MonthlyTiming.objects.filter(doctor=doctor, status='active')

    if request.method == 'POST':
        form = AvailableTimeForm(request.POST)
        form2 = MonthlyTimeForm(request.POST)
        if form.is_valid():
            timing = form.save(commit=False)
            timing.doctor = doctor
            timing.remaining_slots = timing.slot

            # Check if the same doctor has any other timing in this time
            overlapping_timings = AvailableTime.objects.filter(
                doctor=doctor,
                day=timing.day,
                status='active',
                start_time__lt=timing.end_time,
                end_time__gt=timing.start_time
            )

            # Check if the start time is less than end time
            if timing.start_time >= timing.end_time:
                msg.error(request, "Ending Time must be greater than Starting Time.")
            elif overlapping_timings.exists():
                msg.error(request, "The doctor already has another timing in this time range. Please choose a different time.")
            else:
                timing.save()
                msg.success(request, "Timing Updated Successfully")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            error_messages = "Please correct the errors below:<br>"
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages += f"{field}: {error}<br>"
            msg.error(request, error_messages)
    else:
        form = AvailableTimeForm()
        form2 = MonthlyTimeForm()

    return render(request, 'backend/create-timing.html', {'doctor': doctor, 'form': form, 'timings': timings, 'form2': form2, 'monthly_timing': monthly_timing})





@login_required(login_url='login')
def leave_appointments(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request, 'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else:
        return redirect('homepage')

    # Retrieve the appointment IDs from the query string
    appointment_ids = request.GET.getlist('upcoming_appointment_ids')

    upcoming_appointments_list = []
    now = timezone.now()

    if appointment_ids:
        appointments = Appointment.objects.filter(id__in=appointment_ids, status="COMPLETED")

        # Process each appointment
        for appointment in appointments:
            payment_details = RazorpayPaymentDetails.objects.filter(status = 'COMPLETED',appointment=appointment).first()
            content_type = appointment.content_type
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)

            # Determine the appointment datetime based on the related object
            if isinstance(related_object, AvailableTime):
                appointment_datetime = timezone.datetime.combine(appointment.date, related_object.start_time)
            else:
                appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)

            appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

            # Only consider upcoming appointments
            if appointment_datetime >= now:
                detailed_appointment = {
                    'appointment': appointment,
                    'payment_details': payment_details,
                    'related_object': related_object
                }
                upcoming_appointments_list.append(detailed_appointment)

    # Render the response with the list of upcoming appointments
    return render(request, 'backend/leave-appointments.html', {
        'upcoming_appointments_list': upcoming_appointments_list,
    })



@login_required(login_url='login')
def delete_timing(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request, 'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else:
        return redirect('homepage')

    try:
        timing = AvailableTime.objects.get(id=pk)

        # Check if there are any appointments for this timing
        appointments = Appointment.objects.filter(
            content_type=ContentType.objects.get_for_model(AvailableTime),
            object_id=timing.id
        )

        # Separate past and upcoming appointments
        upcoming_appointments = appointments.filter(date__gte=timezone.now(), status='COMPLETED')
        past_appointments = appointments.filter(date__lt=timezone.now())

        if upcoming_appointments.exists():
        
            # Mark timing as inactive
            timing.status = 'inactive'
            timing.save()

            msg.warning(request, f'Timing has {upcoming_appointments.count()} upcoming appointment(s). The timing is now inactive, and new appointments cannot be created. Please attend to the already booked appointments.')

            # Collect upcoming appointment IDs to pass to the next view
            upcoming_appointment_ids = list(upcoming_appointments.values_list('id', flat=True))

            # Construct the query string
            query_string = urllib.parse.urlencode({'upcoming_appointment_ids': upcoming_appointment_ids}, doseq=True)
            url = f"{reverse('leave_appointments')}?{query_string}"

            # Redirect to leave_appointments URL with query parameters
            return redirect(url)

        else:
            # Delete timing if there are no upcoming appointments
            timing.status = 'inactive'
            timing.save()
            msg.success(request, 'Timing deleted successfully.')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except AvailableTime.DoesNotExist:
        msg.error(request, 'Timing not found.')
        return redirect('doctor')


@login_required(login_url='login')
def delete_timing_monthly(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    try:
        timing = MonthlyTiming.objects.get(id=pk)
        
        # Check if there are any appointments for this timing
        appointments = Appointment.objects.filter(content_type=ContentType.objects.get_for_model(MonthlyTiming), object_id=timing.id)
        
        # Separate past and upcoming appointments
        upcoming_appointments = appointments.filter(date__gte=timezone.now(), status='COMPLETED')
        past_appointments = appointments.filter(date__lt=timezone.now())

        if upcoming_appointments.exists():
            # Make status inactive for upcoming appointments and provide a message
            timing.status = 'inactive'
            timing.save()
            msg.warning(request, f'This iming has {upcoming_appointments.count()} upcoming appointment(s). The timing is now inactive, and new appointments cannot be created. Please attend to the already booked appointments.')

            # Collect upcoming appointment IDs to pass to the next view
            upcoming_appointment_ids = list(upcoming_appointments.values_list('id', flat=True))

            # Construct the query string
            query_string = urllib.parse.urlencode({'upcoming_appointment_ids': upcoming_appointment_ids}, doseq=True)
            url = f"{reverse('leave_appointments')}?{query_string}"

            # Redirect to leave_appointments URL with query parameters
            return redirect(url)
        else:
            # Delete timing if there are no upcoming appointments
            timing.status = 'inactive'
            timing.save()
            msg.success(request, 'Timing deleted successfully.')
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except MonthlyTiming.DoesNotExist:
        msg.error(request, 'Timing not found.')
        return redirect('doctor')







# blog View Section 
@login_required(login_url='login')
def blogs(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    blogs = Blog.objects.all()
    context = {'blogs': blogs}
    return render(request, 'backend/blogs.html', context)


@login_required(login_url='login')
def delete_blog(request,pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    blog = Blog.objects.get(id=pk)
    blog.delete()
    msg.success(request, "Blog Deleted Successfully")
    return redirect("blogs")




@login_required(login_url='login')
def create_blog(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            msg.success(request, "Blog created successfully")
            return redirect('blogs')
        else:
            msg.error(request, "There were errors in your form. Please correct them.")
            print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    msg.error(request, f"Error in {field}: {error}")
    else:
        form = BlogForm()
    return render(request, 'backend/create-blog.html', {'form': form})


@login_required(login_url='login')
def update_blog(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    blog = Blog.objects.get(slug=slug)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            msg.success(request,"Blog Updated Successfully")
            return redirect('blogs')  
        else:
            msg.error(request, "There were errors in your form. Please correct them.")
            print(form.errors)
    else:
        form = BlogForm(instance=blog)
    return render(request, 'backend/update-blog.html', {'form': form, 'blog': blog} )




@login_required(login_url='login')
def view_blog_comments(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    blog = Blog.objects.get(slug=slug)
    comments = BlogComment.objects.filter(blog=blog)
    comments_count = BlogComment.objects.filter(blog=blog).count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {'blog': blog, 'comments': comments, 'comments_count':comments_count,'now':now}
    return render(request, 'backend/blog-comments-view.html', context)



@login_required(login_url='login')
def view_blog_comment(request, blogSlug, commentSlug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    blog = get_object_or_404(Blog, slug=blogSlug)
    comment = get_object_or_404(BlogComment, slug=commentSlug)
    comments_count = BlogComment.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {
        'blog': blog,
        'comment': comment,
        'comments_count': comments_count,
        'now': now,
        'rating_range': range(1, 6)  # Pass a range of 1 to 5 for star ratings
    }
    return render(request, 'backend/blog-comments-view-inner.html', context)




@login_required(login_url='login')  
def health_checkup_plans(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    plans = HealthCheckupPlan.objects.all().order_by('priority')
    
    context = {
        'plans': plans
    }
    return render(request, 'backend/checkup-plans.html', context)


@login_required(login_url='login')  
def health_checkup_appointments(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    plan = HealthCheckupPlan.objects.get(slug=slug)
    appointments = HealthCheckupBooking.objects.filter(plan=plan,  status='COMPLETED')
    
    context = {
        'plan': plan,
        'appointments': appointments
    }
    return render(request, 'backend/checkup-appointments.html', context)


@login_required(login_url='login')  
def view_checkup_appointment(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    appointment = get_object_or_404(HealthCheckupBooking, id=pk)
    payment_details = RazorpayPaymentDetails.objects.filter(status = 'COMPLETED',booking=appointment).first()
    detailed_appointment = {
        'appointment': appointment,
        'payment_details': payment_details,
    }


    phone_number = appointment.patient.phone_number

    # Check if the phone number starts with "+91"
    if not phone_number.startswith("+91"):
        phone_number = "+91" + phone_number

    # Generate the WhatsApp link
    whatsapp_link = f"https://wa.me/{phone_number}"


    return render(request, 'backend/view-checkup-booking.html', {'whatsapp_link': whatsapp_link, 'detailed_appointment': detailed_appointment})





@login_required(login_url='login')
def create_health_checkup_plans(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = CheckupForm(request.POST, request.FILES)
        if form.is_valid():
            plan = form.save(commit=False)
            original_slug = slugify(plan.title)
            unique_slug = original_slug
            counter = 1
            while HealthCheckupPlan.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{original_slug}-{counter}'
                counter += 1
            plan.slug = unique_slug
            plan.save()
            msg.success(request, "Health Checkup Plan Created Successfully")
            return redirect('health_checkup_plans')  # Replace with your redirect URL

    else:
        form = CheckupForm()
    return render(request, 'backend/create-plan.html', {'form': form})





@login_required(login_url='login')
def update_health_checkup_plans(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    plan = get_object_or_404(HealthCheckupPlan, slug=slug)
    if request.method == 'POST':
        form = CheckupForm(request.POST, request.FILES, instance=plan)
        if form.is_valid():
            plan = form.save(commit=False)
            original_slug = slugify(plan.title)
            unique_slug = original_slug
            counter = 1
            while HealthCheckupPlan.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{original_slug}-{counter}'
                counter += 1
            plan.slug = unique_slug
            plan.save()
            
            msg.success(request, "Health Checkup plan Updated Successfully")
            return redirect('health_checkup_plans')  # Replace with your redirect URL
        else:
            msg.error(request, 'Failed to update Plan. Please check the form for errors.')
    else:
        form = CheckupForm(instance=plan)
    return render(request, 'backend/update-plan.html', {'form': form, 'plan': plan})



@login_required(login_url='login')
def delete_health_checkup_plan(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    try:
        plan = HealthCheckupPlan.objects.get(slug=slug)
        plan.delete()
        msg.success(request, 'Health checkup plan deleted successfully.')
        return redirect('health_checkup_plans')
    except HealthCheckupPlan.DoesNotExist:
        msg.error(request, 'Plan not found.')
        return redirect('health_checkup_plans')






# new one 


@login_required(login_url='login')  
def heart_day_health_checkup_plans(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    plans = HeartDayCheckup.objects.all().order_by('-created_at')
    
    context = {
        'plans': plans
    }
    return render(request, 'backend/heart-day-offers-plans.html', context)

@login_required(login_url='login')
def heart_day_create_health_checkup_plans(request):
    if request.method == 'POST':
        # Get the main checkup data from the form
        title = request.POST.get('title')
        price = request.POST.get('price')
        original_price = request.POST.get('original_price')

        if not title or not price or not original_price:
            msg.error(request, "All fields are required.")
            return redirect('heart_day_create_health_checkup_plans')

        # Create the HeartDayCheckup instance
        checkup = HeartDayCheckup.objects.create(
            title=title,
            price=price,
            original_price=original_price
        )

        # Iterate through the descriptions received from the POST request
        descriptions = request.POST.getlist('description')
        for desc in descriptions:
            if desc.strip():  # Check if the description is not empty
                CheckupDescription.objects.create(
                    heart_day_checkup=checkup,
                    description=desc
                )

        msg.success(request, "Heart Day Checkup Plan created successfully")
        return redirect('heart_day_health_checkup_plans')  # Redirect to the same page for now

    return render(request, 'backend/create-heart-day-checkup.html')

@login_required(login_url='login')
def heart_day_update_health_checkup_plans(request, pk):
    # Retrieve the existing HeartDayCheckup instance
    checkup = get_object_or_404(HeartDayCheckup, pk=pk)

    if request.method == 'POST':
        # Get the main checkup data from the form
        title = request.POST.get('title')
        price = request.POST.get('price')
        original_price = request.POST.get('original_price')

        # Update the checkup instance
        checkup.title = title
        checkup.price = price
        checkup.original_price = original_price
        checkup.save()

        # Clear existing descriptions before adding new ones
        CheckupDescription.objects.filter(heart_day_checkup=checkup).delete()

        # Iterate through the descriptions received from the POST request
        descriptions = request.POST.getlist('description')
        for desc in descriptions:
            if desc.strip():  # Check if the description is not empty
                CheckupDescription.objects.create(
                    heart_day_checkup=checkup,
                    description=desc
                )

        msg.success(request, "Heart Day Checkup Plan updated successfully")
        return redirect('heart_day_health_checkup_plans')
    
    return render(request, 'backend/update-heart-day-checkup.html', {
        'checkup': checkup,
        'descriptions': CheckupDescription.objects.filter(heart_day_checkup=checkup),
    })

@login_required(login_url='login')
def heart_day_delete_health_checkup_plan(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    try:
        plan = HeartDayCheckup.objects.get(id=pk)
        plan.delete()
        msg.success(request, 'Offer checkup plan deleted successfully.')
        return redirect('heart_day_health_checkup_plans')
    except HealthCheckupPlan.DoesNotExist:
        msg.error(request, 'Plan not found.')
        return redirect('health_checkup_plans')
class CreateHeartHealthCheckupBookingAPIView(APIView):

    def post(self, request, *args, **kwargs):
        print("Cooooooooooooooooooooooooooooooooooooming Here")
        plan_id = request.data.get('plan_id')
        name = request.data.get('name')
        email = request.data.get('email')
        number = request.data.get('number')
        message = request.data.get('message')
        payment_method = request.data.get('payment_method')

        print("all is set here")
        print("payment method",payment_method)
        print(plan_id)
        

        # Validate plan
        plan = get_object_or_404(HeartDayCheckup, id=plan_id)
        print("Plan",plan.title)

        # Create or get the patient
        patient, created = Patient.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone_number': number}
        )

        amount = int(plan.price * 100)  # Convert to paise


        print(payment_method)

        if payment_method == 'PAY_AT_HOSPITAL':
            print("Coming here")
            booking = HeartDayCheckupBooking.objects.create(
                plan=plan,
                patient=patient,
                message=message,
                status='COMPLETED',
                payment_method='PAY_AT_HOSPITAL'
            )

            if not request.user.is_superuser:
                Notification.objects.create(
                    message=f"{booking.patient.name} booked a health checkup {booking.plan.title} for ₹ {booking.plan.price} (World Heart Day Offer)",
                    read_status=False,
                    redirection_url=reverse('heart_day_view_checkup_appointment', args=[booking.id]),
                    object_id=booking.id,
                    type='checkup'
                )

            # Return the URL to the frontend to handle the redirection
            success_url = reverse('heart_health_checkup_payment_success', kwargs={'booking_id': booking.id})
            response_data = {'redirect_url': success_url}
            return JsonResponse(response_data)


        else:

            print("Coming here")

            try:
                # Create booking
                booking = HeartDayCheckupBooking.objects.create(
                    plan=plan,
                    patient=patient,
                    message=message,
                    payment_method="ONLINE_PAY_NOW"
                )

                # Your business logic
                response_data = {
                    'hdfc_payment_url': f'https://vshhospital.com/static/payments/initiatePaymentCheckupHeart.php?appointment_id={booking.id}&amount={amount}'
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': 'An error occurred: ' + str(e)}, status=500)


        
def update_heart_day_checkup_status(request):
    # Take parameters from request (GET or POST)
    appointment_id = request.GET.get('appointment_id') or request.POST.get('appointment_id')
    amount = request.GET.get('amount') or request.POST.get('amount')
    order_id = request.GET.get('order_id') or request.POST.get('order_id')


    hdfc_response = get_hdfc_order_status(order_id, str(appointment_id))
    if hdfc_response.get('status') == 'CHARGED':

        # Validate that we have all the necessary parameters
        if not appointment_id or not amount or not order_id:
            return JsonResponse({"error": "Missing required parameters."}, status=400)

        # Convert amount to integer
        try:
            amount = int(amount)
        except ValueError:
            return JsonResponse({"error": "Invalid amount format."}, status=400)

        # Fetch the appointment object
        booking = get_object_or_404(HeartDayCheckupBooking, id=appointment_id)

        # Update the appointment status to 'COMPLETED'
        booking.status = 'COMPLETED'
        booking.save()


        # Create a new RazorpayPaymentDetails record
        RazorpayPaymentDetails.objects.create(
            payment_id=str(uuid.uuid4()),  # Generate a custom UUID
            order_id=order_id,
            signature='',
            amount=amount*100,
            currency='INR',
            payment_method='online',
            status='COMPLETED',  # Mark as completed
            payment_for='OFFER',
            offer=booking,
        )



        # Create a notification for successful booking
        if not request.user.is_superuser:
            Notification.objects.create(
                message=f"{booking.patient.name} booked a health checkup {booking.plan.title} for ₹ {amount / 100} (Heart Day Offer)",
                read_status=False,
                redirection_url=reverse('heart_day_view_checkup_appointment', args=[booking.id]),
                object_id=booking.id,
                type='checkup'
            )

        # Redirect to the payment success page
        return redirect('heart_health_checkup_payment_success', booking_id=booking.id)

    elif hdfc_response.get('resp_category') == 'PAYMENT_FAILURE':
        booking = get_object_or_404(HeartDayCheckupBooking, id=appointment_id)
        # Create a new RazorpayPaymentDetails record
        RazorpayPaymentDetails.objects.create(
            payment_id=str(uuid.uuid4()),  # Generate a custom UUID
            order_id=order_id,
            signature='',
            amount=amount,
            currency='INR',
            payment_method='online',
            status='FAILED',  # Mark as completed
            payment_for='OFFER',
            offer=booking,
        )
    
        return redirect('heart_health_checkup_payment_failure')
    else :
        booking = get_object_or_404(HeartDayCheckupBooking, id=appointment_id)
        # Create a new RazorpayPaymentDetails record
        RazorpayPaymentDetails.objects.create(
            payment_id=str(uuid.uuid4()),  # Generate a custom UUID
            order_id=order_id,
            signature='',
            amount=amount*100,
            currency='INR',
            payment_method='online',
            status='FAILED',  # Mark as completed
            payment_for='OFFER',
            offer=booking,
        )
        
        return redirect('heart_health_checkup_payment_failure')
        

def heart_health_checkup_payment_success(request, booking_id):
    # Fetch the booking object or return 404 if not found
    booking = get_object_or_404(HeartDayCheckupBooking, id=booking_id)

    # Check if booking is completed
    if booking.status == 'COMPLETED':
        plan = booking.plan
        payment_details = None  # Default to None in case payment details are not applicable

        payment_details = None
        # Fetch payment details if payment was made online
        if booking.payment_method == 'ONLINE_PAY_NOW':
            try:
                payment_details = RazorpayPaymentDetails.objects.get(status='COMPLETED', offer=booking)
            except ObjectDoesNotExist:
                # Log this information if necessary or handle it gracefully
                payment_details = None  

        # Check if the user is a super admin
        if request.user.is_superuser:
            # Render the page for super admins
            return render(request, 'frontend/heart-day-healthcheckup-payment-success.html', {
                'booking': booking,
                'plan': plan,
                'payment_details': payment_details
            })
        else:
            # Render for non-super admin users
            return render(request, 'frontend/heart-day-healthcheckup-frontend-success.html', {
                'booking': booking,
                'plan': plan,
                # Include payment_details in case you need them on the frontend
                'payment_details': payment_details  
            })

    # Redirect to failure page if booking is not completed
    else:
        return redirect('heart_health_checkup_payment_failure')

        
def heart_health_checkup_payment_failure(request):
    if request.user.is_superuser:
        return render(request, 'frontend/heart-day-healthcheckup-payment-failure.html')
    else: 
        return render(request, 'frontend/heart-day-healthcheckup-frontend-failure.html')

@login_required(login_url='login')  
def heart_day_health_checkup_appointments(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    plan = HeartDayCheckup.objects.get(slug=slug)
    appointments = HeartDayCheckupBooking.objects.filter(plan=plan,  status='COMPLETED')
    upcoming_appointments = []


    for appointment in appointments:
        payment_details = RazorpayPaymentDetails.objects.filter(status = 'COMPLETED', offer=appointment).first()
        

        detailed_appointment = {
            'appointment': appointment,
            'payment_details': payment_details,
        }

        upcoming_appointments.append(detailed_appointment)

    
    context = {
        'plan': plan,
        'appointments': appointments,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'backend/heart-checkup-appointments.html', context)

@login_required(login_url='login')  
def heart_day_view_checkup_appointment(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    appointment = get_object_or_404(HeartDayCheckupBooking, id=pk)
    payment_details = None
    if appointment.payment_method == 'ONLINE_PAY_NOW':
        payment_details = RazorpayPaymentDetails.objects.filter(status = 'COMPLETED',offer=appointment).first()
    detailed_appointment = {
        'appointment': appointment,
        'payment_details': payment_details,
    }

    phone_number = appointment.patient.phone_number

    # Check if the phone number starts with "+91"
    if not phone_number.startswith("+91"):
        phone_number = "+91" + phone_number

    # Generate the WhatsApp link
    whatsapp_link = f"https://wa.me/{phone_number}"


    return render(request, 'backend/heart-view-checkup-booking.html', {'whatsapp_link': whatsapp_link, 'detailed_appointment': detailed_appointment})



@login_required(login_url='login')  
def change_payment_status(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    
    booking = get_object_or_404(HeartDayCheckupBooking, id=pk)

    RazorpayPaymentDetails.objects.create(
        payment_id=str(uuid.uuid4()),  # Generate a custom UUID
        order_id='',
        signature='',
        amount=booking.plan.price*100,
        currency='INR',
        payment_method='cash',
        status='COMPLETED',  # Directly mark as completed for cash payments
        payment_for='OFFER',
        offer=booking,
    )
    
    msg.success(request, "Payment Collected")
    return redirect(request.META.get('HTTP_REFERER', 'homepage'))






# department view 
@login_required(login_url='login')  
def departments(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    departments = Department.objects.all()
    context ={ 'departments': departments }
    return render(request, 'backend/departments.html', context)



@login_required(login_url='login')
def create_department(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            department = form.save(commit=False)
            department.save()
            msg.success(request, "Department Created Successfully")
            return redirect('departments')  # Replace with your redirect URL
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    msg.error(request, f"Error in {field}: {error}")
    else:
        form = DepartmentForm()
    return render(request, 'backend/create-department.html', {'form': form})



@login_required(login_url='login')
def update_department(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    department = get_object_or_404(Department, slug=slug)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES, instance=department)
        if form.is_valid():
            department = form.save(commit=False)
            department.save()
            
            msg.success(request, "Department Updated Successfully")
            return redirect('departments')  # Replace with your redirect URL
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    msg.error(request, f"Error in {field}: {error}")
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'backend/update-department.html', {'form': form, 'department': department})



@login_required(login_url='login')
def delete_department(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    try:
        department = Department.objects.get(slug=slug)
        department.delete()
        msg.success(request, 'Department deleted successfully.')
        return redirect('departments')
    except Department.DoesNotExist:
        msg.error(request, 'department not found.')
        return redirect('department')











# message view 
@login_required(login_url='login')
def messages(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    inbox = Message.objects.all().order_by('-created_at')
    inbox_count = Message.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {'inbox': inbox, 'now':now, 'inbox_count': inbox_count}
    return render(request, 'backend/messages.html', context)

@login_required(login_url='login')
def message(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    message = Message.objects.get(slug=slug)
    inbox_count = Message.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {'message':message,'now':now, 'inbox_count': inbox_count}
    return render(request, 'backend/message-view.html', context)







# message view 
@login_required(login_url='login')
def call_backs(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    call_back = CallBack.objects.all().order_by('-created_at')
    inbox_count = CallBack.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {'call_back': call_back, 'now':now, 'inbox_count': inbox_count}
    return render(request, 'backend/callbacks.html', context)

@login_required(login_url='login')
def call_back(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    message = CallBack.objects.get(id=pk)
    inbox_count = CallBack.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {'message':message,'now':now, 'inbox_count': inbox_count}
    return render(request, 'backend/callback_detail.html', context)





# career view 
@login_required(login_url='login')
def careers(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    careers = Career.objects.all()
    context ={'careers': careers}
    return render(request, 'backend/career.html', context)


@login_required(login_url='login')
def create_career(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = CareerForm(request.POST)
        if form.is_valid():
            form.save()
            msg.success(request, 'Career created successfully!')
            return redirect('careers')  # Redirect to a list of careers or any other appropriate view
    else:
        form = CareerForm()
    
    return render(request, 'backend/create-career.html', {'form': form})


@login_required(login_url='login')
def update_career(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    career = Career.objects.get(slug=slug)
    if request.method == 'POST':
        form = CareerForm(request.POST, instance=career)
        if form.is_valid():
            form.save()
            msg.success(request, 'Career Updated successfully!')
            return redirect('careers')  # Redirect to a list of careers or any other appropriate view
    else:
        form = CareerForm(instance=career)
    
    return render(request, 'backend/update-career.html', {'form': form})


@login_required(login_url='login')
def delete_career(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    try:
        career = Career.objects.get(id=pk)
        career.delete()
        msg.success(request, 'Career deleted successfully.')
        return redirect('careers')
    except Career.DoesNotExist:
        msg.error(request, 'Career not found.')
        return redirect('careers')
    
    

@login_required(login_url='login')
def view_career_applications(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    career = Career.objects.get(slug=slug)
    applications = CareerApplication.objects.filter(job=career).order_by('-created_at')
    application_count = CareerApplication.objects.filter(job=career).count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {'career': career, 'applications': applications, 'application_count':application_count,'now':now}
    return render(request, 'backend/career-application-view.html', context)


@login_required(login_url='login')
def view_career_application(request, careerslug, applicationslug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    career = get_object_or_404(Career, slug=careerslug)
    application = get_object_or_404(CareerApplication, slug=applicationslug)
    application_count = CareerApplication.objects.filter(job=career).count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    file_type = 'pdf' if application.cv and application.cv.name.endswith('.pdf') else 'image'

    context = {
        'career': career,
        'application': application,
        'application_count': application_count,
        'now': now,
        'file_type': file_type  # Add file type to the context

    }
    return render(request, 'backend/career-application-view-inner.html', context)





@login_required(login_url='login')
def view_international_applications(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    applications = InternationalMessage.objects.all()
    application_count = InternationalMessage.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {'applications': applications, 'application_count':application_count,'now':now}
    return render(request, 'backend/international-messages.html', context)


@login_required(login_url='login')
def view_international_application(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    application = get_object_or_404(InternationalMessage, id=pk)
    application_count = InternationalMessage.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    

    context = {
        'application': application,
        'application_count': application_count,
        'now': now,
    }
    return render(request, 'backend/international-application-view-inner.html', context)




@login_required(login_url='login')
def create_leave(request, slug):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    doctor = get_object_or_404(Doctor, slug=slug)
    leaves = Leave.objects.filter(doctor=doctor)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        # Convert the dates to actual date objects
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Ensure the start date is today or in the future
        if start_date < timezone.now().date():
            msg.error(request, "The leave start date must be today or in the future.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Ensure the end date is not before the start date
        if end_date < start_date:
            msg.error(request, "The end date cannot be before the start date.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Create leave entries for each day in the range
        current_date = start_date
        while current_date <= end_date:
            if Leave.objects.filter(doctor=doctor, date=current_date).exists():
                msg.error(request, f"The doctor already has a leave on {current_date}. Please choose a different date.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            Leave.objects.create(doctor=doctor, date=current_date, reason=reason)
            current_date += datetime.timedelta(days=1)

        msg.success(request, "Leave created successfully.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'backend/leave-request.html', {'doctor': doctor, 'leaves': leaves})

    

@login_required(login_url='login')
def delete_leave(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    leave = get_object_or_404(Leave, id=pk)
    
    # Check if the leave date is in the past
    if leave.date < timezone.now().date():
        msg.error(request, "You cannot delete this leave because this leave is already taken.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    leave.delete()
    msg.success(request, "Leave deleted successfully.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Create your views here.

def login(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            msg.success(request, "Logged In")


            try:
                profile = Summary.objects.get(user=user)
            except ObjectDoesNotExist:
                msg.error(request,'Profile does not exist. You cannot access here.')
                return redirect('homepage')

        
            if profile:
                if profile.role == 'hr':
                    return redirect('hr_dashboard')
                if profile.role == 'frontdesk':
                    return redirect('dashboard')
                    
                if profile.role == 'admin':
                    return redirect('dashboard')
                    
                if profile.role == 'media':
                    return redirect('media_dashboard') #media______
                else:
                    return redirect('homepage')
            return redirect('dashboard')
            
        else:
            print("Error")
            msg.error(request, 'Invalid Credential')
            return render(request, 'backend/login.html')
    return render(request, 'backend/login.html')


# logout 
@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')





@login_required(login_url='login')
def patients(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    # Filter patients based on the search query
    patients = Patient.objects.all().order_by('-created_at')
    if search_query:
        patients = patients.filter(
            Q(name__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(disease__icontains=search_query) |
            Q(gender__icontains=search_query)
        )

    # Pagination: Show 10 patients per page
    paginator = Paginator(patients, 20)
    paginated_patients = paginator.get_page(page_number)

    context = {
        'patients': paginated_patients,
        'search_query': search_query,
    }
    return render(request, 'backend/patients.html', context)




@login_required(login_url='login')
def appointments(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile.role == 'hr':
        return redirect('hr_dashboard')
    elif profile.role == 'media':
        return redirect('media_dashboard')
    elif profile.role not in ['frontdesk', 'admin']:
        return redirect('homepage')

    search_upcoming = request.GET.get('search_upcoming', '')

    # Get all appointments, optionally filtered by search query
    appointments = Appointment.objects.filter(
        Q(patient__name__icontains=search_upcoming) |
        Q(patient__email__icontains=search_upcoming) |
        Q(patient__phone_number__icontains=search_upcoming)
    ).order_by('-created_at')

    # Pagination for upcoming appointments (5 per page)
    paginator_appointments = Paginator(appointments, 20)  # Adjust 5 to any number you prefer
    page_number = request.GET.get('page')
    page_obj = paginator_appointments.get_page(page_number)

    context = {
        'appointments': page_obj,  # Pass the paginated appointments object to the template
        'search_upcoming': search_upcoming,
    }
    return render(request, 'backend/appointments.html', context)







@login_required(login_url='login')
def patient_appointments(request, patient_id):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')

    patient = get_object_or_404(Patient, id=patient_id)
    search_query = request.GET.get('search', '')
    active_tab = request.GET.get('tab', 'upcoming')  # Default to upcoming tab
    now = timezone.now()

    # Get all appointments for the patient
    completed_appointments = Appointment.objects.filter(patient=patient, status='COMPLETED').order_by('-date')
    cancelled_appointments = Appointment.objects.filter(patient=patient, status='CANCELLED').order_by('-date')

    # Apply search filter
    if search_query:
        completed_appointments = completed_appointments.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__email__icontains=search_query) |
            Q(patient__phone_number__icontains=search_query) |
            Q(selected_doctor__name__icontains=search_query)
        )
        cancelled_appointments = cancelled_appointments.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__email__icontains=search_query) |
            Q(patient__phone_number__icontains=search_query) |
            Q(selected_doctor__name__icontains=search_query)
        )

    past_appointments = []
    upcoming_appointments = []
    cancelled_appointments_list = []

    for appointment in completed_appointments:
        content_type = appointment.content_type
        related_object = content_type.get_object_for_this_type(id=appointment.object_id)

        if isinstance(related_object, AvailableTime):
            appointment_datetime = timezone.datetime.combine(appointment.date, related_object.start_time)
        else:
            appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)

        appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

        payment_details = RazorpayPaymentDetails.objects.filter(status = 'COMPLETED',appointment=appointment).first()
        
        detailed_appointment = {
            'appointment': appointment,
            'related_object': related_object,
            'payment_details': payment_details
        }

        if appointment_datetime < now:
            past_appointments.append(detailed_appointment)
        else:
            upcoming_appointments.append(detailed_appointment)

    # Process cancelled appointments
    for appointment in cancelled_appointments:
        content_type = appointment.content_type
        related_object = content_type.get_object_for_this_type(id=appointment.object_id)

        payment_details = RazorpayPaymentDetails.objects.filter(status = 'COMPLETED',appointment=appointment).first()

        detailed_appointment = {
            'appointment': appointment,
            'related_object': related_object,
            'payment_details': payment_details
        }

        cancelled_appointments_list.append(detailed_appointment)

    # Paginate results
    paginator_past = Paginator(past_appointments, 20)
    paginator_upcoming = Paginator(upcoming_appointments, 20)
    paginator_cancelled = Paginator(cancelled_appointments_list, 20)

    page_number_past = request.GET.get('page_past')
    page_number_upcoming = request.GET.get('page_upcoming')
    page_number_cancelled = request.GET.get('page_cancelled')

    past_appointments_paginated = paginator_past.get_page(page_number_past)
    upcoming_appointments_paginated = paginator_upcoming.get_page(page_number_upcoming)
    cancelled_appointments_paginated = paginator_cancelled.get_page(page_number_cancelled)

    context = {
        'patient': patient,
        'past_appointments': past_appointments_paginated,
        'upcoming_appointments': upcoming_appointments_paginated,
        'cancelled_appointments': cancelled_appointments_paginated,
        'search_query': search_query,
        'active_tab': active_tab,  # Pass the active tab to the template
    }
    return render(request, 'backend/patient-appointments.html', context)



@login_required(login_url='login')
def doctor_appointments(request, doctor_id):
    # Check if the user has a profile
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request, 'Profile does not exist. You cannot access here.')
        return redirect('login')

    # Check user role and redirect accordingly
    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else:
        return redirect('homepage')

    # Fetch the doctor
    doctor = get_object_or_404(Doctor, id=doctor_id)
    search_query = request.GET.get('search', '')
    active_tab = request.GET.get('tab', 'upcoming')  # Default to upcoming tab
    now = timezone.now()

    # Filter appointments for the doctor based on status
    completed_appointments = Appointment.objects.filter(selected_doctor=doctor, status='COMPLETED').order_by('-date')
    cancelled_appointments = Appointment.objects.filter(selected_doctor=doctor, status='CANCELLED').order_by('-date')

    # Apply search query if provided
    if search_query:
        completed_appointments = completed_appointments.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__email__icontains=search_query) |
            Q(patient__phone_number__icontains=search_query) |
            Q(selected_doctor__name__icontains=search_query)
        )
        cancelled_appointments = cancelled_appointments.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__email__icontains=search_query) |
            Q(patient__phone_number__icontains=search_query) |
            Q(selected_doctor__name__icontains=search_query)
        )

    past_appointments = []
    upcoming_appointments = []
    cancelled_appointments_list = []

    # Process completed appointments
    for appointment in completed_appointments:
        content_type = appointment.content_type

        try:
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)
        except ObjectDoesNotExist:
            related_object = 'Timing deleted'  # Handle missing object case

        # Determine the appointment datetime and timing details
        if isinstance(related_object, AvailableTime):
            appointment_datetime = timezone.datetime.combine(appointment.date, related_object.start_time)
            timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"
        elif isinstance(related_object, str) and related_object == 'Timing deleted':
            appointment_datetime = timezone.datetime.combine(appointment.date, timezone.datetime.min.time())
            timing_details = "Timing deleted"
        else:
            appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)
            timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"

        # Make appointment_datetime timezone-aware
        appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

        payment_details = RazorpayPaymentDetails.objects.filter(status='COMPLETED', appointment=appointment).first()

        detailed_appointment = {
            'appointment': appointment,
            'related_object': related_object,
            'payment_details': payment_details,
            'timing_details': timing_details
        }

        if appointment_datetime < now:
            past_appointments.append(detailed_appointment)
        else:
            upcoming_appointments.append(detailed_appointment)

    # Process cancelled appointments
    for appointment in cancelled_appointments:
        content_type = appointment.content_type
        
        try:
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)
        except ObjectDoesNotExist:
            related_object = 'Timing deleted'  # Handle missing object case

        # Determine timing details
        if isinstance(related_object, AvailableTime):
            timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"
        elif isinstance(related_object, str) and related_object == 'Timing deleted':
            timing_details = "Timing deleted"
        else:
            timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"

        payment_details = RazorpayPaymentDetails.objects.filter(status='COMPLETED', appointment=appointment).first()

        detailed_appointment = {
            'appointment': appointment,
            'related_object': related_object,
            'payment_details': payment_details,
            'timing_details': timing_details
        }

        cancelled_appointments_list.append(detailed_appointment)

    # Pagination setup
    paginator_past = Paginator(past_appointments, 20)  # Show 10 past appointments per page
    paginator_upcoming = Paginator(upcoming_appointments, 20)  # Show 10 upcoming appointments per page
    paginator_cancelled = Paginator(cancelled_appointments_list, 20)  # Show 10 cancelled appointments per page

    page_number_past = request.GET.get('page_past')
    page_number_upcoming = request.GET.get('page_upcoming')
    page_number_cancelled = request.GET.get('page_cancelled')

    past_appointments_paginated = paginator_past.get_page(page_number_past)
    upcoming_appointments_paginated = paginator_upcoming.get_page(page_number_upcoming)
    cancelled_appointments_paginated = paginator_cancelled.get_page(page_number_cancelled)

    context = {
        'doctor': doctor,
        'past_appointments': past_appointments_paginated,
        'upcoming_appointments': upcoming_appointments_paginated,
        'cancelled_appointments': cancelled_appointments_paginated,
        'search_query': search_query,
        'active_tab': active_tab,
    }
    return render(request, 'backend/doctor-appointment.html', context)
@login_required(login_url='login')
def create_patient(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            msg.success(request, 'Patient created successfully.')
            return redirect('patients')  # Redirect to the patient list view or any other view
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            msg.error(request, ' '.join(error_messages))
    else:
        form = PatientForm()
    
    return render(request, 'backend/create-patient.html', {'form': form})



@login_required(login_url='login')
def update_patient(request, pk):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    patient = Patient.objects.get(id=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            msg.success(request, 'Patient upated successfully.')
            return redirect('patients')  # Redirect to the patient list view or any other view
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            msg.error(request, ' '.join(error_messages))
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'backend/update-patient.html', {'form': form})











logger = logging.getLogger(__name__)

@api_view(['GET'])
def check_available_timings(request, doctor_id, date):
    logger.info(f"Checking available timings for doctor {doctor_id} on date {date}")
    
    try:
        # Parse the date
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid date format: {date}")
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        # Get the doctor
        doctor = get_object_or_404(Doctor, id=doctor_id)
        logger.info(f"Doctor found: {doctor}")

        # Check if the doctor is on leave on the specified date
        if Leave.objects.filter(doctor=doctor, date=date_obj).exists():
            logger.info(f"Doctor {doctor} is on leave on {date_obj}")
            return Response({'error': 'Doctor is on leave on this day.'}, status=400)

        # Check for monthly timings with remaining slots
        monthly_timings = MonthlyTiming.objects.filter(
            doctor=doctor, 
            status='active', 
            date=date_obj, 
            remaining_slots__gte=1
        ).order_by('start_time')
        monthly_serializer = MonthlyTimingSerializer(monthly_timings, many=True)

        # Check for available times based on the day of the week
        day_of_week = date_obj.strftime('%A').lower()
        available_times = AvailableTime.objects.filter(
            doctor=doctor, 
            status='active', 
            day=day_of_week
        )

        # Filter available times based on remaining slots
        valid_available_times = []
        for available_time in available_times:
            appointments_on_same_day = Appointment.objects.filter(
                date=date_obj,
                selected_doctor=doctor,
                status='COMPLETED',
                content_type=ContentType.objects.get_for_model(AvailableTime),
                object_id=available_time.id
            ).count()
            remaining_slots = available_time.slot - appointments_on_same_day
            if remaining_slots >= 1:
                valid_available_times.append(available_time)
        
        # Sort the valid available times by start time before serialization
        valid_available_times.sort(key=lambda x: x.start_time)
        available_times_serializer = AvailableTimeSerializer(valid_available_times, many=True)

        # Combine both sets of timings
        combined_timings = {
            'monthly_timings': monthly_serializer.data,
            'weekly_timings': available_times_serializer.data
        }

        logger.info(f"Timings found: {combined_timings}")
        return Response({'timings': combined_timings}, status=200)

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return Response({'error': 'An internal server error occurred.'}, status=500)





@login_required(login_url='login')
def create_appointment_backend(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    doctors = Doctor.objects.all()
    departments = Department.objects.all()
    available_times = AvailableTime.objects.all()
    monthly_timings = MonthlyTiming.objects.all()
    return render(request, 'backend/create-appointment.html', {
        'doctors': doctors,
        'departments': departments,
        'available_times': available_times,
        'monthly_timings': monthly_timings
    })


@login_required(login_url='login')
def patient_appointments_create(request, patient_id):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    departments = Department.objects.all()
    patient = Patient.objects.get(id=patient_id)
    return render(request, 'backend/create-appointment-patient.html', {
        'patient': patient,
        'departments': departments
    })


@login_required(login_url='login')
def create_appointement_page(request):
    try:
        profile = Summary.objects.get(user=request.user)
    except ObjectDoesNotExist:
        msg.error(request,'Profile does not exist. You cannot access here.')
        return redirect('login')

    if profile:
        if profile.role == 'hr':
            return redirect('hr_dashboard')
        elif profile.role == 'media':
            return redirect('media_dashboard')  # Correctly redirect to media dashboard
        elif profile.role not in ['frontdesk', 'admin']:
            return redirect('homepage')
    else: 
        return redirect('homepage')
    doctors = Doctor.objects.all()
    departments = Department.objects.all()
    available_times = AvailableTime.objects.all()
    monthly_timings = MonthlyTiming.objects.all()
    return render(request, 'frontend/create-appointement.html', {
        'doctors': doctors,
        'departments': departments,
        'available_times': available_times,
        'monthly_timings': monthly_timings
    })




class DoctorsByDepartmentAPIView(APIView):
    def get(self, request, *args, **kwargs):
        department_id = request.query_params.get('department_id')
        print("Coming Here")
        print(department_id)
        
        if not department_id:
            return Response({"error": "department_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        department = get_object_or_404(Department, id=department_id)
        doctors = Doctor.objects.filter(department=department, status=True)
        print(doctors)
        
        serializer = DoctorSerializer(doctors, many=True)
        print(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_200_OK)






class PaymentListView(FilterView):
    model = RazorpayPaymentDetails
    template_name = 'backend/payments.html'
    context_object_name = 'payments'
    filterset_class = RazorpayPaymentDetailsFilter

    # Override the get_queryset method to apply ordering and filter by status 'COMPLETED'
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='COMPLETED').order_by('-created_at')  # Filter by 'COMPLETED' and order by created_at descending

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payments = context['payments']

        formatted_payments = []
        total_amount = 0

        # Utility function to format time
        def format_time(time):
            if time:
                formatted_time = time.strftime('%I:%M %p')
                return formatted_time.lstrip("0")  # Remove leading zero
            return None

        # Process each payment
        for payment in payments:
            total_amount += payment.amount / 100  # Convert paise to rupees

            # Handle appointments
            if payment.appointment:
                appointment = payment.appointment
                content_type = appointment.content_type
                related_object = None

                # Safely retrieve the related object
                try:
                    model_class = content_type.model_class()
                    related_object = model_class.objects.get(id=appointment.object_id)
                    appointment.schedule = related_object
                except ObjectDoesNotExist:
                    related_object = 'Timing deleted'

                # Handle both cases with valid or missing related object
                formatted_payment = {
                    'patient_name': appointment.patient.name,
                    'order_id': payment.order_id,
                    'disease': appointment.patient.disease,
                    'appointment_date': appointment.date,
                    'appointment_start_time': format_time(appointment.schedule.start_time) if related_object != 'Timing deleted' and hasattr(appointment.schedule, 'start_time') else None,
                    'appointment_end_time': format_time(appointment.schedule.end_time) if related_object != 'Timing deleted' and hasattr(appointment.schedule, 'end_time') else None,
                    'doctor_name': appointment.selected_doctor.name,
                    'doctor_photo_url': appointment.selected_doctor.photo.url if appointment.selected_doctor.photo else None,
                    'paid_date': payment.created_at.strftime('%B %d %Y'),
                    'paid_amount': payment.amount / 100,
                    'payment_method': payment.payment_method,
                    'type': 'Appointment'
                }
                formatted_payments.append(formatted_payment)

            # Handle health checkup bookings
            elif payment.booking:
                booking = payment.booking
                plan = booking.plan

                formatted_payment = {
                    'patient_name': booking.patient.name,
                    'order_id': payment.order_id,
                    'disease': 'Health Checkup',
                    'appointment_date': booking.created_at.strftime('%B %d %Y'),
                    'appointment_start_time': None,
                    'appointment_end_time': None,
                    'doctor_name': plan.title,
                    'plan_title': plan.title,
                    'doctor_photo_url': None,
                    'paid_date': payment.created_at.strftime('%B %d %Y'),
                    'paid_amount': payment.amount / 100,
                    'payment_method': payment.payment_method,
                    'type': 'Health Checkup'
                }
                formatted_payments.append(formatted_payment)

            # Handle special offers
            elif payment.offer:
                booking = payment.offer
                plan = booking.plan

                formatted_payment = {
                    'patient_name': booking.patient.name,
                    'order_id': payment.order_id,
                    'disease': 'Health Checkup (World Heart Day)',
                    'appointment_date': booking.created_at.strftime('%B %d %Y'),
                    'appointment_start_time': None,
                    'appointment_end_time': None,
                    'doctor_name': booking.plan.title,
                    'plan_title': booking.plan.title,
                    'doctor_photo_url': None,
                    'paid_date': payment.created_at.strftime('%B %d %Y'),
                    'paid_amount': payment.amount / 100,
                    'payment_method': booking.payment_method,
                    'type': 'Health Checkup (World Heart Day)'
                }
                formatted_payments.append(formatted_payment)

        # Apply pagination
        paginator = Paginator(formatted_payments, 20)  # Show 10 payments per page
        page_number = self.request.GET.get('page')
        paginated_payments = paginator.get_page(page_number)

        # Pass data to context
        context['formatted_payments'] = paginated_payments
        context['total_amount'] = total_amount
        return context

class CreateAppointmentPatientAPIView(APIView):
    def post(self, request, *args, **kwargs):
        patient_id = request.data.get('patient_id')
        date = request.data.get('date')
        message = request.data.get('message')
        department_id = request.data.get('department')
        doctor_id = request.data.get('selected_doctor')
        payment_method = request.data.get('payment_method', 'online')  # Default to 'online' if not provided
        schedule_id = request.data.get('schedule_id')
        registration_fee_include = request.data.get('registration_fee')
        discount_percentage = float(request.data.get('discount', 0))

        registration_fee = 'paid'
        if registration_fee_include == 'on':
            registration_fee = 'unpaid'

        # Debug statements
        print(f"Patient ID: {patient_id}, Date: {date}, Message: {message}, Department: {department_id}")
        print(f"Doctor: {doctor_id}, Payment Method: {payment_method}, Schedule ID: {schedule_id}")

        # Check if all required fields are present
        if not all([patient_id, date, message, department_id, doctor_id, schedule_id]):
            return Response({"error": "Missing one or more required fields."}, status=status.HTTP_400_BAD_REQUEST)

        doctor = get_object_or_404(Doctor, id=doctor_id)
        leave_exists = Leave.objects.filter(doctor=doctor, date=date).exists()
        if leave_exists:
            return Response({"error": "The selected doctor is on leave on the specified date."}, status=status.HTTP_400_BAD_REQUEST)

        # Get patient
        patient = get_object_or_404(Patient, id=patient_id)

        # Get department and doctor
        department = get_object_or_404(Department, id=department_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Determine if the schedule is monthly or weekly
        try:
            monthly_timing = MonthlyTiming.objects.get(uuid=schedule_id)
            content_type = ContentType.objects.get_for_model(MonthlyTiming)
            object_id = monthly_timing.id
            start_time = monthly_timing.start_time
        except MonthlyTiming.DoesNotExist:
            available_time = get_object_or_404(AvailableTime, uuid=schedule_id)
            content_type = ContentType.objects.get_for_model(AvailableTime)
            object_id = available_time.id
            start_time = available_time.start_time

        # Combine date and start_time to form a datetime
        appointment_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        appointment_datetime = timezone.datetime.combine(appointment_date, start_time)
        appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

        if appointment_datetime <= timezone.now():
            return Response({"error": "The appointment datetime must be in the future."}, status=status.HTTP_400_BAD_REQUEST)

        # Create appointment
        appointment = Appointment.objects.create(
            date=date,
            message=message,
            payment_id='',  # This will be filled after Razorpay payment if online
            payment_method=payment_method,
            patient=patient,
            department=department,
            selected_doctor=doctor,
            content_type=content_type,
            object_id=object_id,
            status='PENDING' if payment_method == 'online' else 'COMPLETED',
            discount=discount_percentage  # Store the discount percentage in the appointment
        )

        amount = int(doctor.fee) * 100  # amount in paise
        if registration_fee != 'paid':
            amount += 27000  # add registration fee in paise

        discount_amount = (amount * discount_percentage) / 100
        amount -= int(discount_amount)

        if payment_method == 'cash':

            msg.success(request, "Appointment booked successfully!")

            
            # Get the related object (AvailableTime or MonthlyTiming)
            content_type = appointment.content_type
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)

            # Determine the timing
            if isinstance(related_object, AvailableTime):
                start_time = related_object.start_time
                end_time = related_object.end_time
            else:
                start_time = related_object.start_time
                end_time = related_object.end_time

            



            
            if not request.user.is_superuser:
                Notification.objects.create(
                    message=f"{appointment.patient.name} booked an appointment with {appointment.selected_doctor.name} for ₹ {amount / 100}",
                    read_status=False,
                    redirection_url=reverse('view_appointment', args=[appointment.id]),
                    object_id=appointment.id,
                    type='appointment'
                )

        

        if payment_method == 'online':

            print("Sdfjlkasjdflkdsajlkfjdslkfjdsfjlkdsajflkdsjflkdsjflkdsjlkdsajlkdsajflkdsajlkdsfjlkdsjlkdsafjlkdfjldsafjlsdajflkdsajflksdfjldfsjlkdfsjsldfjdfslk")



            try:
                # Your business logic
                response_data = {
                    'hdfc_payment_url': f'https://vshhospital.com/static/payments/initiatePayment.php?appointment_id={appointment.id}&amount={amount}'
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': 'An error occurred: ' + str(e)}, status=500)

                
           
            # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # razorpay_order = client.order.create({
            #     'amount': amount,
            #     'currency': 'INR',
            #     'payment_capture': '1'
            # })

            # appointment.payment_id = razorpay_order['id']
            # appointment.save()

            # RazorpayPaymentDetails.objects.create(
            #     payment_id=razorpay_order['id'],
            #     order_id=razorpay_order['id'],
            #     signature='',  # This will be filled after payment verification
            #     amount=amount,
            #     currency='INR',
            #     payment_method=payment_method,
            #     status='PENDING',  # Initial status
            #     appointment=appointment
            # )

            # return Response({
            #     'razorpay_order_id': razorpay_order['id'],
            #     'appointment_id': appointment.id,
            #     'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            #     'amount': amount,
            #     'currency': 'INR',
            #     'name': patient.name,
            #     'callback_url': "http://" + "127.0.0.1:8000" + "/handle-payment/",
            #     'email': patient.email,
            #     'phone_number': patient.phone_number,
            #     'description': 'Appointment Booking'
            # }, status=status.HTTP_201_CREATED)
        else:
            # Create RazorpayPaymentDetails with custom ID for cash payments
            RazorpayPaymentDetails.objects.create(
                payment_id=str(uuid.uuid4()),  # Generate a custom UUID
                order_id='',
                signature='',
                amount=amount,
                currency='INR',
                payment_method='cash',
                status='COMPLETED',  # Directly mark as completed for cash payments
                appointment=appointment
            )


        # Return response for non-online payment method
        return Response({
            'appointment_id': appointment.id,
            'name': patient.name,
            'email': patient.email,
            'phone_number': patient.phone_number,
            'description': 'Appointment Booking'
        }, status=status.HTTP_201_CREATED)


        

    def get(self, request, *args, **kwargs):
        doctors = Doctor.objects.all()
        departments = Department.objects.all()
        available_times = AvailableTime.objects.all()
        monthly_timings = MonthlyTiming.objects.all()

        data = {
            'doctors': [{'id': doctor.id, 'name': doctor.name, 'fee': doctor.fee} for doctor in doctors],
            'departments': [{'id': department.id, 'title': department.title} for department in departments],
            'available_times': [{'uuid': time.uuid, 'start_time': time.start_time, 'end_time': time.end_time} for time in available_times],
            'monthly_timings': [{'uuid': timing.uuid, 'start_time': timing.start_time, 'end_time': timing.end_time} for timing in monthly_timings],
        }
        return Response(data, status=status.HTTP_200_OK)






def get_hdfc_order_status(order_id, customer_id):
        
    # Replace these with actual merchant ID, customer ID, and API key
    merchant_id = "36912"
    api_key = "F74FC346C764DEE94CC2E86B208D30"

    # Base64 encode with the API key as the username and an empty string as the password
    credentials = f'{api_key}:'.encode('ascii')
    base64_credentials = base64.b64encode(credentials).decode('ascii')

    # URL for the HDFC API
    url = f'https://smartgateway.hdfcbank.com/orders/{order_id}'

    # Headers
    headers = {
        'Authorization': f'Basic {base64_credentials}',
        'version': '2023-06-30',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-merchantid': merchant_id,
        'x-customerid': customer_id,
    }

    # Make the GET request to HDFC API
    try:
        response = requests.get(url, headers=headers)
        logger.info(f"HDFC API Response Status: {response.status_code}, Body: {response.text}")
        return response.json()  # return the full response object
    except requests.exceptions.RequestException as e:
        logger.error(f"HDFC API request failed: {str(e)}")
        return Response({"error": f"HDFC API request failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def update_appointment_status(request):
    
    # Take parameters from request (GET or POST)
    appointment_id = request.GET.get('appointment_id') or request.POST.get('appointment_id')
    amount = request.GET.get('amount') or request.POST.get('amount')
    order_id = request.GET.get('order_id') or request.POST.get('order_id')


    # Now, retrieve the HDFC order status
    hdfc_response = get_hdfc_order_status(order_id, str(appointment_id))
    

    if hdfc_response.get('status') == 'CHARGED':
        

        # Validate that we have all the necessary parameters
        if not appointment_id or not amount or not order_id:
            return JsonResponse({"error": "Missing required parameters."}, status=400)

        # Convert amount to integer
        try:
            amount = int(amount)
        except ValueError:
            return JsonResponse({"error": "Invalid amount format."}, status=400)

        # Fetch the appointment object
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Update the appointment status to 'COMPLETED'
        appointment.status = 'COMPLETED'
        appointment.save()

        # Create a new RazorpayPaymentDetails record
        RazorpayPaymentDetails.objects.create(
            payment_id=str(uuid.uuid4()),  # Generate a custom UUID
            order_id=order_id,
            signature='',
            amount=amount,
            currency='INR',
            payment_method='online',
            status='COMPLETED',  # Mark as completed
            appointment=appointment
        )

        # Create notifications only if the user is not a superuser
        if not request.user.is_superuser:
            Notification.objects.create(
                message=f"{appointment.patient.name} booked an appointment with {appointment.selected_doctor.name} for ₹ {amount / 100}",  # Divide by 100 to get amount in INR
                read_status=False,
                redirection_url=reverse('view_appointment', args=[appointment.id]),
                object_id=appointment.id,
                type='appointment'
            )


        # Redirect to the payment success page
        return redirect('payment_success_account', appointment_id=appointment.id)



    elif hdfc_response.get('resp_category') == 'PAYMENT_FAILURE':

        appointment = get_object_or_404(Appointment, id=appointment_id)
        # Create a new RazorpayPaymentDetails record
        RazorpayPaymentDetails.objects.create(
            payment_id=str(uuid.uuid4()),  # Generate a custom UUID
            order_id=order_id,
            signature='',
            amount=amount,
            currency='INR',
            payment_method='online',
            status='FAILED',  # Mark as completed
            appointment=appointment
        )
        return redirect('payment_failure_account')
    
    else :

        # Create a new RazorpayPaymentDetails record
        appointment = get_object_or_404(Appointment, id=appointment_id)
        RazorpayPaymentDetails.objects.create(
            payment_id=str(uuid.uuid4()),  # Generate a custom UUID
            order_id=order_id,
            signature='',
            amount=amount,
            currency='INR',
            payment_method='online',
            status='FAILED',  # Mark as completed
            appointment=appointment
        )

        return redirect('payment_failure_account')
        



def collect_cash_appointment(request, pk):
    # Fetch the appointment by its primary key
    appointment = get_object_or_404(Appointment, id=pk)

    # Check if the appointment is already marked as COMPLETED
    if appointment.status == 'COMPLETED':
        try:
            order_id = f"ORDER-{uuid.uuid4().hex[:8].upper()}"
            # Fetch the associated payment details
            payment = RazorpayPaymentDetails.objects.get(appointment=appointment)
            payment.status = 'COMPLETED'
            payment.order_id = order_id
            payment.save()
            
            # Add a success message
            msg.success(request, "Payment marked as COMPLETED successfully.")
        except RazorpayPaymentDetails.DoesNotExist:
            # Handle case if payment details are missing
            msg.error(request, "Payment details not found for this appointment.")
    else:
        # Handle case where appointment is not completed
        msg.error(request, "Appointment status is not COMPLETED, so payment cannot be collected.")

    # Redirect to the same page (or wherever `request.META['HTTP_REFERER']` points to)
    return redirect(request.META.get('HTTP_REFERER', '/'))


class CreateAppointmentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        disease = request.data.get('disease') or ''
        message = request.data.get('message') or ''

        department_id = request.data.get('department')
        doctor_id = request.data.get('selected_doctor')
        gender = request.data.get('gender')


        # Check if all required fields are present
        if not all([name, email, phone_number, department_id, doctor_id, gender]):
            return Response({"error": "Missing one or more required fields."}, status=status.HTTP_400_BAD_REQUEST)

        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Create or get patient
        patient, created = Patient.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone_number': phone_number, 'disease': disease, 'gender': gender}
        )

        # Get department and doctor
        department = get_object_or_404(Department, id=department_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)

        appointment = Appointment.objects.create(
            message=message,
            patient=patient,
            department=department,
            selected_doctor=doctor,
        )

        msg.success(request, "Appointment Booked Successfully")

        if not request.user.is_superuser:
            Notification.objects.create(
                message=f"{appointment.patient.name} booked an appointment with {appointment.selected_doctor.name}",
                read_status=False,
                redirection_url=reverse('view_appointment', args=[appointment.id]),
                object_id=appointment.id,
                type='appointment'
            )

            

        # Return response for non-online payment method
        return Response({
            'appointment_id': appointment.id,
            'name': name,
            'email': email,
            'phone_number': phone_number,
            'description': 'Appointment Booking'
        }, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        doctors = Doctor.objects.all()
        departments = Department.objects.all()
        available_times = AvailableTime.objects.all()
        monthly_timings = MonthlyTiming.objects.all()

        data = {
            'doctors': [{'id': doctor.id, 'name': doctor.name} for doctor in doctors],
            'departments': [{'id': department.id, 'title': department.title} for department in departments],
        }
        return Response(data, status=status.HTTP_200_OK)







logger = logging.getLogger(__name__)

@csrf_exempt
def handle_payment(request):
    if request.method == 'POST':
        try:
            # Log the raw request body to see what is being received
            raw_body = request.body.decode('utf-8')
            logger.info("Raw request body: %s", raw_body)

            # Parse URL-encoded form data
            payment_data = request.POST
            logger.info("Parsed form data: %s", payment_data)
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        payment_id = payment_data.get('razorpay_payment_id')
        appointment_id = payment_data.get('razorpay_order_id')
        razorpay_signature = payment_data.get('razorpay_signature')

        if not payment_id or not appointment_id or not razorpay_signature:
            return redirect('payment_failure_account')
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': appointment_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            appointment = get_object_or_404(Appointment, payment_id=appointment_id)
            appointment.status = 'COMPLETED'
            appointment.save()


            # Update RazorpayPaymentDetails with the payment status and signature
            payment_details = get_object_or_404(RazorpayPaymentDetails, appointment=appointment)
            payment_details.status = 'COMPLETED'
            payment_details.signature = razorpay_signature
            payment_details.payment_id = payment_id
            payment_details.order_id = appointment_id
            payment_details.save()


            # Inside the successful payment verification block
            if not request.user.is_superuser:
                Notification.objects.create(
                    message=f"{appointment.patient.name} booked an appointment with {appointment.selected_doctor.name} for ₹ {payment_details.amount / 100}",
                    read_status=False,
                    redirection_url=reverse('view_appointment', args=[appointment.id]),
                    object_id=appointment.id,
                    type = 'appointment'
                )
                

                        


            # Decrement the remaining slots
            content_type = appointment.content_type
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)

            if isinstance(related_object, MonthlyTiming):
                related_object.remaining_slots -= 1
                related_object.save()
            elif isinstance(related_object, AvailableTime):
                appointments_on_same_day = Appointment.objects.filter(
                    date=appointment.date,
                    content_type=content_type,
                    object_id=appointment.object_id
                ).count()
                if appointments_on_same_day <= related_object.slot:
                    related_object.save()

            return redirect('payment_success_account', appointment_id=appointment.id)
        except razorpay.errors.SignatureVerificationError:
            logger.error("Payment verification failed for appointment_id=%s", appointment_id)
            appointment = get_object_or_404(Appointment, payment_id=appointment_id)
            appointment.status = 'FAILED'
            appointment.save()
            return redirect('payment_failure_account')
    else:
        logger.error("Invalid HTTP method: %s", request.method)
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




class HandlePaymentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        appointment_id = request.data.get('appointment_id')
        razorpay_signature = request.data.get('razorpay_signature')

        # Verify the payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': appointment_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            appointment = get_object_or_404(Appointment, id=appointment_id)
            appointment.status = 'COMPLETED'
            appointment.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError:
            return redirect('payment_failure_account')


@method_decorator(login_required, name='dispatch')
class UnreadNotificationsView(APIView):
    def get(self, request):
        notifications = Notification.objects.filter(read_status=False).order_by('-created_at')
        notifications_data = [
            {
                'id': notification.id,
                'message': notification.message,
                'created_at': naturaltime(notification.created_at),
                'redirection_url': notification.redirection_url
            }
            for notification in notifications
        ]
        return Response(notifications_data, status=status.HTTP_200_OK)



@method_decorator(login_required, name='dispatch')
class MarkNotificationAsReadView(APIView):
    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id)
        notification.read_status = True
        notification.first_read_by = request.user
        notification.save()
        return Response({'message': 'Notification marked as read.'}, status=status.HTTP_200_OK)


@method_decorator(login_required, name='dispatch')
class MarkAllNotificationsAsReadView(APIView):
    def post(self, request):
        Notification.objects.filter(read_status=False).update(read_status=True)
        return Response({'message': 'All notifications marked as read.'}, status=status.HTTP_200_OK)





def view_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    detailed_appointment = {
        'appointment': appointment,
    }
    phone_number = appointment.patient.phone_number

    # Check if the phone number starts with "+91"
    if not phone_number.startswith("+91"):
        phone_number = "+91" + phone_number

    # Generate the WhatsApp link
    whatsapp_link = f"https://wa.me/{phone_number}"

    return render(request, 'backend/appointment-view.html', {'detailed_appointment': detailed_appointment, 'whatsapp_link': whatsapp_link})




def payment_success_account(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Get the related object (AvailableTime or MonthlyTiming)
    
    if(appointment.status == 'COMPLETED'):
        content_type = appointment.content_type
        related_object = content_type.get_object_for_this_type(id=appointment.object_id)

        payment_details = RazorpayPaymentDetails.objects.get(status = 'COMPLETED', appointment = appointment)

        # Determine the timing
        if isinstance(related_object, AvailableTime):
            start_time = related_object.start_time
            end_time = related_object.end_time
        else:
            start_time = related_object.start_time
            end_time = related_object.end_time


        # Check if the user is a super admin
        if request.user.is_superuser:
            # Render the page for super admins
            return render(request, 'backend/payment-success.html', {
                'appointment': appointment,
                'start_time': start_time,
                'end_time': end_time,
                'payment_details': payment_details,
            })
        else:
            # Redirect non-super admin users to another page
            return render(request, 'frontend/payment-success.html', {
                'appointment': appointment,
                'start_time': start_time,
                'end_time': end_time,
                'payment_details': payment_details,
            })

    else: 
        return redirect('payment_failure_account')

def payment_failure_account(request):
    if request.user.is_superuser:
        return render(request, 'backend/payment-failure.html')
    else: 
        return render(request, 'frontend/payment-failure.html')
        






def payment_success_pay_at_hospital(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Get the related object (AvailableTime or MonthlyTiming)
    
    if(appointment.status == 'COMPLETED'):
        content_type = appointment.content_type
        related_object = content_type.get_object_for_this_type(id=appointment.object_id)


        # Determine the timing
        if isinstance(related_object, AvailableTime):
            start_time = related_object.start_time
            end_time = related_object.end_time
        else:
            start_time = related_object.start_time
            end_time = related_object.end_time


        # Check if the user is a super admin
        if request.user.is_superuser:
            # Render the page for super admins
            return render(request, 'frontend/payment-success-pay-at-hospital.html', {
                'appointment': appointment,
                'start_time': start_time,
                'end_time': end_time,
            })
        else:
            # Redirect non-super admin users to another page
            return render(request, 'frontend/payment-success-pay-at-hospital.html', {
                'appointment': appointment,
                'start_time': start_time,
                'end_time': end_time,
            })

    else: 
        return redirect('payment_failure_account')





class CreateHealthCheckupBookingAPIView(APIView):
    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')
        name = request.data.get('name')
        email = request.data.get('email')
        number = request.data.get('number')
        message = request.data.get('message')

        # Validate plan
        plan = get_object_or_404(HealthCheckupPlan, id=plan_id)

        # Create or get the patient
        patient, created = Patient.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone_number': number}
        )

        # Create booking
        booking = HealthCheckupBooking.objects.create(
            plan=plan,
            patient=patient,
            message=message
        )

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay order
        amount = int(plan.price * 100)  # Convert to paise
        

        try:
            # Your business logic
            response_data = {
                'hdfc_payment_url': f'https://vshhospital.com/static/payments/initiatePaymentCheckup.php?appointment_id={booking.id}&amount={amount}'
            }
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred: ' + str(e)}, status=500)






def update_checkup_status(request):
    # Take parameters from request (GET or POST)
    appointment_id = request.GET.get('appointment_id') or request.POST.get('appointment_id')
    amount = request.GET.get('amount') or request.POST.get('amount')
    order_id = request.GET.get('order_id') or request.POST.get('order_id')


    hdfc_response = get_hdfc_order_status(order_id, str(appointment_id))
    if hdfc_response.get('status') == 'CHARGED':

        # Validate that we have all the necessary parameters
        if not appointment_id or not amount or not order_id:
            return JsonResponse({"error": "Missing required parameters."}, status=400)

        # Convert amount to integer
        try:
            amount = int(amount)
        except ValueError:
            return JsonResponse({"error": "Invalid amount format."}, status=400)

        # Fetch the appointment object
        booking = get_object_or_404(HealthCheckupBooking, id=appointment_id)

        # Update the appointment status to 'COMPLETED'
        booking.status = 'COMPLETED'
        booking.save()


        # Create a new RazorpayPaymentDetails record
        RazorpayPaymentDetails.objects.create(
            payment_id=str(uuid.uuid4()),  # Generate a custom UUID
            order_id=order_id,
            signature='',
            amount=amount,
            currency='INR',
            payment_method='online',
            status='COMPLETED',  # Mark as completed
            payment_for='CHECKUP',
            booking=booking,
        )



        # Create a notification for successful booking
        if not request.user.is_superuser:
            Notification.objects.create(
                message=f"{booking.patient.name} booked a health checkup {booking.plan.title} for ₹ {amount / 100}",
                read_status=False,
                redirection_url=reverse('view_checkup_appointment', args=[booking.id]),
                object_id=booking.id,
                type='checkup'
            )

        # Redirect to the payment success page
        return redirect('health_checkup_payment_success', booking_id=booking.id)

    elif hdfc_response.get('resp_category') == 'PAYMENT_FAILURE':
        booking = get_object_or_404(HealthCheckupBooking, id=appointment_id)
        # Create a new RazorpayPaymentDetails record
        RazorpayPaymentDetails.objects.create(
            payment_id=str(uuid.uuid4()),  # Generate a custom UUID
            order_id=order_id,
            signature='',
            amount=amount,
            currency='INR',
            payment_method='online',
            status='FAILED',  # Mark as completed
            payment_for='CHECKUP',
            booking=booking,
        )
    
        return redirect('health_checkup_payment_failure')
    else :
        booking = get_object_or_404(HealthCheckupBooking, id=appointment_id)
        # Create a new RazorpayPaymentDetails record
        RazorpayPaymentDetails.objects.create(
            payment_id=str(uuid.uuid4()),  # Generate a custom UUID
            order_id=order_id,
            signature='',
            amount=amount,
            currency='INR',
            payment_method='online',
            status='FAILED',  # Mark as completed
            payment_for='CHECKUP',
            booking=booking,
        )
        
        return redirect('health_checkup_payment_failure')
        


class HandleHealthCheckupPaymentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        booking_id = request.data.get('booking_id')
        razorpay_signature = request.data.get('razorpay_signature')

        # Retrieve booking and payment details
        booking = get_object_or_404(HealthCheckupBooking, id=booking_id)
        payment_details = get_object_or_404(RazorpayPaymentDetails, booking=booking, order_id=request.data.get('razorpay_order_id'))

        # Verify payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': payment_details.order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            payment_details.payment_id = payment_id
            payment_details.signature = razorpay_signature
            payment_details.status = 'COMPLETED'
            payment_details.save()

            booking.status = 'COMPLETED'
            booking.save()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError:
            return Response({'status': 'error', 'message': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)






logger = logging.getLogger(__name__)

@csrf_exempt
def handle_health_checkup_payment(request):
    if request.method == 'POST':
        try:
            # Log the raw request body to see what is being received
            raw_body = request.body.decode('utf-8')
            logger.info("Raw request body: %s", raw_body)

            # Parse URL-encoded form data
            payment_data = request.POST
            logger.info("Parsed form data: %s", payment_data)
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=400)

        payment_id = payment_data.get('razorpay_payment_id')
        order_id = payment_data.get('razorpay_order_id')
        razorpay_signature = payment_data.get('razorpay_signature')

        if not payment_id or not order_id or not razorpay_signature:
            return redirect('health_checkup_payment_failure')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)

            # Retrieve the booking using the Razorpay order ID
            booking = get_object_or_404(HealthCheckupBooking, payment_id=order_id)
            booking.status = 'COMPLETED'
            booking.save()

            # Update RazorpayPaymentDetails with the payment status and signature
            payment_details = get_object_or_404(RazorpayPaymentDetails, booking=booking)
            payment_details.status = 'COMPLETED'
            payment_details.signature = razorpay_signature
            payment_details.payment_id = payment_id
            payment_details.order_id = order_id
            payment_details.save()

            # Create a notification for successful booking
            if not request.user.is_superuser:
                Notification.objects.create(
                    message=f"{booking.patient.name} booked a health checkup {booking.plan.title} for ₹ {payment_details.amount / 100}",
                    read_status=False,
                    redirection_url=reverse('view_checkup_appointment', args=[booking.id]),
                    object_id=booking.id,
                    type='checkup'
                )

            return redirect('health_checkup_payment_success', booking_id=booking.id)
        except razorpay.errors.SignatureVerificationError:
            logger.error("Payment verification failed for order_id=%s", order_id)
            booking = get_object_or_404(HealthCheckupBooking, payment_id=order_id)
            booking.status = 'FAILED'
            booking.save()
            return redirect('health_checkup_payment_failure')
    else:
        logger.error("Invalid HTTP method: %s", request.method)
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method.'}, status=405)




def health_checkup_payment_success(request, booking_id):
    booking = get_object_or_404(HealthCheckupBooking, id=booking_id)
    

    if booking.status == 'COMPLETED':
        # Since health checkup bookings do not have time slots, we will just confirm the plan details.
        plan = booking.plan
        
        payment_details = RazorpayPaymentDetails.objects.get(status = 'COMPLETED',booking = booking)

        # Check if the user is a super admin
        if request.user.is_superuser:
            # Render the page for super admins
            return render(request, 'frontend/healthcheckup-payment-success.html', {
                'booking': booking,
                'plan': plan,
                'payment_details' : payment_details
            })
        else:
            # Render for non-super admin users
            return render(request, 'frontend/healthcheckup-frontend-success.html', {
                'booking': booking,
                'plan': plan,
                'payment_details' : payment_details
                
            })

    else:
        return redirect('health_checkup_payment_failure')


# views.py

def health_checkup_payment_failure(request):
    if request.user.is_superuser:
        return render(request, 'frontend/healthcheckup-payment-failure.html')
    else: 
        return render(request, 'frontend/healthcheckup-frontend-failure.html')




def campaign_appointments(request):
    appointments = DepartmentAppointment.objects.all()
    context = {
        'appointments' : appointments
    }
    return render(request, 'backend/departmentappointment.html', context)


def campaign_appointments_view(request, pk):
    appointment = DepartmentAppointment.objects.get(id=pk)

    phone_number = appointment.number

    # Check if the phone number starts with "+91"
    if not phone_number.startswith("+91"):
        phone_number = "+91" + phone_number

    # Generate the WhatsApp link
    whatsapp_link = f"https://wa.me/{phone_number}"


    context = {
        'appointment' : appointment,
        'whatsapp_link': whatsapp_link
    }
    return render(request, 'backend/departmentappointment-view.html', context)











def healthy_2025(request):
    return render(request, 'frontend/healthy-2025.html')


# Create your views here.
def homepage(request):
    departments = Department.objects.filter(status=True, show_on_homepage = True)[:8]
    nav_deps = Department.objects.filter(status=True)
    cookies_accepted = request.COOKIES.get('cookiesAccepted')

    
    doctors = Doctor.objects.filter(show_on_homepage = True, status=True).annotate(
    is_priority_null=Case(
            When(priority=None, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('is_priority_null', 'priority')


    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    banners = Banner.objects.filter(status=True)
    ad_banners = AdBanner.objects.filter(status=True)

    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')
    context = {
        'departments': departments,
        'doctors': doctors,
        'blogs': blogs,
        'cookies_accepted': cookies_accepted,
        'ad_banners': ad_banners,
        'banners': banners,
        'nav_deps': nav_deps,
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/index.html', context)






# Create your views here.
def heart_day(request):
    nav_deps = Department.objects.filter(status=True)
    blogs = Blog.objects.filter(status=True, show_on_homepage=True)[:3]
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    health_checkup_plans = HeartDayCheckup.objects.all().order_by('-updated_at')

    health_checkup_plans_array = []

    # Populate health_checkup_plans_array with plans and their descriptions
    for x in health_checkup_plans:
        description = CheckupDescription.objects.filter(heart_day_checkup=x)
        
        # Adding the checkup plan and its descriptions to the array
        health_checkup_plans_array.append({
            'plan': x,
            'descriptions': description
        })

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
        'health_checkup_plans': health_checkup_plans_array,  # Update the context to include health_checkup_plans_array
    }

    return render(request, 'frontend/heart-day.html', context)




def heart_day_seo(request):
   
    health_checkup_plans = HeartDayCheckup.objects.all().order_by('-updated_at')

    health_checkup_plans_array = []

    # Populate health_checkup_plans_array with plans and their descriptions
    for x in health_checkup_plans:
        description = CheckupDescription.objects.filter(heart_day_checkup=x)
        
        # Adding the checkup plan and its descriptions to the array
        health_checkup_plans_array.append({
            'plan': x,
            'descriptions': description
        })

    context = {
        'health_checkup_plans': health_checkup_plans_array,  # Update the context to include health_checkup_plans_array
    }

    return render(request, 'frontend/heart-day-seo.html', context)






def view_user_appointment(request):
    appointments = []
    nav_deps = Department.objects.filter(status=True)
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    email = request.GET.get('email')


    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')
    
    if email:
        # Fetch the current date and time
        current_time = timezone.now()

        # Fetch the appointments associated with the provided email
        # and filter to include only future appointments
        all_appointments = Appointment.objects.filter(
            patient__email=email,
            status = 'COMPLETED',
            date__gte=current_time
        ).order_by('date')

        # Process each appointment to include timing information
        for appointment in all_appointments:
            content_type = appointment.content_type
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)
            
            payment = RazorpayPaymentDetails.objects.get(status = 'COMPLETED',appointment = appointment)


            if isinstance(related_object, AvailableTime):
                start_time = related_object.start_time.strftime('%I:%M %p')
                end_time = related_object.end_time.strftime('%I:%M %p')
            else:
                start_time = related_object.start_time.strftime('%I:%M %p')
                end_time = related_object.end_time.strftime('%I:%M %p')

            appointments.append({
                'appointment': appointment,
                'start_time': start_time,
                'end_time': end_time,
                'related_object': related_object,
                'order_id' : payment.order_id
            })
    
    return render(request, 'frontend/view-appointment.html', {
        'appointments': appointments,
        'email': email,
        'nav_deps': nav_deps,
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
        'blogs': blogs
    })
    
    
    
def gallery_frontend(request):

    # Fetch galleries separately for each folder
    gallery = Gallery.objects.all()

    # Fetch blogs and departments for the sidebar or additional content
    blogs = Blog.objects.filter(status=True, show_on_homepage=True)[:3]
    nav_deps = Department.objects.filter(status=True)

    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'gallery' : gallery,
        'blogs': blogs,
        'nav_deps': nav_deps,
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    
    return render(request, 'frontend/galleries.html', context)


def insurance(request):
    blogs = Blog.objects.filter(status=True, show_on_homepage=True)[:3]
    context = {
        'blogs': blogs,
    }
    
    return render(request, 'frontend/insurance.html', context)


def patient(request):
    blogs = Blog.objects.filter(status=True, show_on_homepage=True)[:3]
    context = {
        'blogs': blogs,
    }
    
    return render(request, 'frontend/patient.html', context)


def patient_feedback(request):
    blogs = Blog.objects.filter(status=True, show_on_homepage=True)[:3]
    context = {
        'blogs': blogs,
    }
    
    return render(request, 'frontend/feedback.html', context)


# Create your views here.
def about(request):
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/about.html', context)



def services(request):
    # Fetch published blogs (limit to 3) and active departments
    blogs = Blog.objects.filter(status=True, show_on_homepage=True)[:3]  # Keep select_related here
    departments = Department.objects.filter(status=True)  # Remove select_related('speciality_type')

    # Group departments by speciality type
    speciality_dict = {}
    for dept in departments:
        speciality_dict.setdefault(dept.speciality_type, []).append(dept)

    # Prepare context for the template
    context = {
        'blogs': blogs,
        'speciality_dict': speciality_dict,  # Grouped departments
        'speciality_choices': Department.SPECIALITY_CHOICES,  # For tab headers
    }
    return render(request, 'frontend/services.html', context)
    

# Create your views here.
def frontend_blogs(request):
    blogs = Blog.objects.filter(status=True)
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/blogs.html', context)



def frontend_doctors(request):
    search_query = request.GET.get('search', '')
    department_query = request.GET.get('department', '')
    sort_by = request.GET.get('sort_by', '')  # Sorting parameter

    # Fetch the latest blogs and all departments
    blogs = Blog.objects.filter(status=True, show_on_homepage=True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    departments = Department.objects.filter(status=True)

    # Get top 4 departments based on your criteria (e.g., alphabetical order or any custom logic)
    top_departments = Department.objects.filter(status=True, show_on_homepage=True).order_by('title')[:4]

    # Filter doctors based on search and department
    doctors = Doctor.objects.filter(status=True).annotate(
        is_priority_null=Case(
            When(priority=None, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('is_priority_null', 'priority')
    
    # Apply search query
    if search_query:
        doctors = doctors.filter(name__icontains=search_query)

    # Apply department filter with exact match
    if department_query:
        doctors = doctors.filter(department__title__iexact=department_query)  # Use iexact for case-insensitive exact match

    # Apply sorting by department
    if sort_by:
        doctors = doctors.filter(department__title__iexact=sort_by)

    context = {
        'blogs': blogs,
        'doctors': doctors,
        'departments': departments,
        'top_departments': top_departments,
        'active_sort': sort_by,
        'nav_deps': nav_deps,
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/doctors.html', context)


def autism(request):
    blogs = Blog.objects.filter(status=True, show_on_homepage=True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/autism.html', context)


def facilities(request): 
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')
    
    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/facilities.html', context)


def contact(request):
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    if request.method == 'POST':
        data = json.loads(request.body)
        form = MessageForm(data)
        if form.is_valid():
            message = form.save(commit=False)
            message.slug = slugify(message.name)

            # Ensure unique slug
            original_slug = message.slug
            counter = 1
            while Message.objects.filter(slug=message.slug).exists():
                message.slug = f'{original_slug}-{counter}'
                counter += 1

            message.save()

            # Create a notification
            Notification.objects.create(
                message=f'New message from {message.name}',
                redirection_url=reverse('message', args=[message.slug]),
                type='message',
                object_id=message.id
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return render(request, 'frontend/contact.html', {'form': MessageForm(), 'blogs': blogs,'nav_deps': nav_deps, 'super_specialities': super_specialities, 'other_specialities': other_specialities,})

# Create your views here.
def icu(request):
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/icu.html', context)


def single_service(request, slug):
    department = Department.objects.get(slug=slug)
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    doctors = Doctor.objects.filter(status=True, department=department)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    print(doctors.count())

    context = {
        'department': department,
        'blogs': blogs,
        'nav_deps': nav_deps,
        'doctors': doctors,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    
    return render(request, 'frontend/service.html', context)
    
def single_blog(request, slug):
    # Fetch the blog using slug and handle non-existing blog cases
    blog = get_object_or_404(Blog, slug=slug)
    tags_list = blog.tags.split(',')  # Convert comma-separated string to a list
    comments = BlogComment.objects.filter(blog=blog).order_by('-created_at')
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')


    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            message = data.get('comment')
            rating = data.get('rating')

            # Validate form data
            if not (name and email and message and rating):
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    raise ValueError("Rating must be between 1 and 5.")
            except ValueError as e:
                return JsonResponse({'error': str(e)}, status=400)

            # Create and save the comment
            comment = BlogComment(
                name=name,
                email=email,
                message=message,
                rating=rating,
                blog=blog
            )
            comment.save()
            # Create a notification
            NotificationMedia.objects.create(
                message=f'{comment.name} Commented on {blog.heading} Blog',
                redirection_url=reverse('media_view_blog_comment', args=[blog.slug, comment.slug]),
                type='comment',
                object_id=comment.id
            )

            return JsonResponse({'success': 'Your comment has been posted successfully!'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    context = {
        'blog': blog,
        'tags_list': tags_list,
        'comments': comments,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    
    return render(request, 'frontend/blog.html', context)
    
def single_doctor(request, slug):
    doctor = Doctor.objects.get(slug=slug)
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'doctor': doctor,
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    
    return render(request, 'frontend/doctor.html', context)






def single_doctor_backup(request, slug):
    doctor = Doctor.objects.get(slug=slug)
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'doctor': doctor,
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    
    return render(request, 'frontend/backup-doctor.html', context)
    
def privacy(request):
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/privacy-policy.html', context)

def terms(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/terms.html', context)

def international(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/international-patient.html', context)

def best_in_class(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/best-in-class.html', context)

def international_visa(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/international-visa.html', context)

def assistance(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/assistance.html', context)

def documentation_fly(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/documentation-fly.html', context)

def dedicated_patient(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/dedicated-assistance.html', context)

def assistance_treatment_plan(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/treatment-plan.html', context)

def airport(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')

    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,

    }
    return render(request, 'frontend/airport.html', context)

def legal(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')
    context = {
        'blogs': blogs,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/legal.html', context)

def frontend_careers(request):    
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    careers = Career.objects.filter(status=True)
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')
    context = {
        'blogs': blogs,
        'careers': careers,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/careers.html', context)

@csrf_exempt
def single_career(request, slug):
    career = get_object_or_404(Career, slug=slug)
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')
    
    if request.method == 'POST':
        # Extract data from request
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        cover_letter = request.POST.get('cover-letter')
        cv = request.FILES.get('resume')

        # Create new career application
        application = CareerApplication(
            name=name,
            email=email,
            number=number,
            cover_letter=cover_letter,
            cv=cv,
            job=career
        )
        application.save()
        


        return JsonResponse({'success': True, 'message': 'Application submitted successfully'})

    context = {
        'blogs': blogs,
        'career': career,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/career.html', context)

def health_checkups(request):
    blogs = Blog.objects.filter(status=True, show_on_homepage = True)[:3]
    health_checkup_plans = HealthCheckupPlan.objects.filter(status=True).order_by('priority')
    nav_deps = Department.objects.filter(status=True)
    
    # Filter departments based on speciality type
    super_specialities = nav_deps.filter(speciality_type='super_speciality')[:12]
    other_specialities = nav_deps.filter(speciality_type='other_speciality')
    context = {
        'blogs': blogs,
        'health_checkup_plans': health_checkup_plans,
        'nav_deps': nav_deps,
        
        'super_specialities': super_specialities,
        'other_specialities': other_specialities,
    }
    return render(request, 'frontend/health-checkups.html', context)


@csrf_exempt  # Disable CSRF for simplicity, but it's better to include proper CSRF token handling
def acl(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            phone_number = data.get('phone_number')
            message = data.get('message')
            department = data.get('department')

            # Validate the phone number length
            if not phone_number.isdigit() or len(phone_number) != 10:
                return JsonResponse({'success': False, 'message': 'Invalid phone number'}, status=400)

            # Process the form data, e.g., save to the database or send an email
            # For demonstration, let's just return a success message

            booking = DepartmentAppointment.objects.create(name=name, department=department, message=message, number=phone_number)

            Notification.objects.create(
                message=f"{name} booked an Appointment for ACL (Orthopedic)",
                read_status=False,
                redirection_url=reverse('campaign_appointments_view', args=[booking.id]),
                object_id=booking.id,
                type='appointment'
            )
            return JsonResponse({'success': True, 'message': 'Appointment booked successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An error occurred'}, status=500)

    return render(request, 'frontend/acl.html')

@csrf_exempt  # Disable CSRF for simplicity, but it's better to include proper CSRF token handling
def urology(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            phone_number = data.get('phone_number')
            message = data.get('message')
            department = data.get('department')

            # Validate the phone number length
            if not phone_number.isdigit() or len(phone_number) != 10:
                return JsonResponse({'success': False, 'message': 'Invalid phone number'}, status=400)

            # Process the form data, e.g., save to the database or send an email
            # For demonstration, let's just return a success message

            booking = DepartmentAppointment.objects.create(name=name, department=department, message=message, number=phone_number)

            Notification.objects.create(
                message=f"{name} booked an Appointment for (Urology Camp)",
                read_status=False,
                redirection_url=reverse('campaign_appointments_view', args=[booking.id]),
                object_id=booking.id,
                type='appointment'
            )
            return JsonResponse({'success': True, 'message': 'Appointment booked successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An error occurred'}, status=500)

    return render(request, 'frontend/urology.html')



import requests
import base64


class GetPaymentDetailsByOrderId(APIView):

    def get(self, request, order_id):
        try:
            # Get payment details from local DB
            payment_details = RazorpayPaymentDetails.objects.get(status = 'COMPLETED', order_id=order_id)

            payment_data = {
                'amount': payment_details.amount / 100,
                'order_id': payment_details.order_id,
                'payment_id': payment_details.payment_id,
            }

            # Check if it's for an appointment or health checkup
            if payment_details.payment_for == 'APPOINTMENT':
                appointment = get_object_or_404(Appointment, id=payment_details.appointment_id)
                appointment_data = {
                    'appointment_id': appointment.id,
                    'patient_name': appointment.patient.name,  # Example field
                    'doctor_name': appointment.selected_doctor.name,  # Example field
                    'appointment_date': appointment.date,  # Example field
                }
                payment_data['appointment_details'] = appointment_data

            else:
                booking = get_object_or_404(HealthCheckupBooking, id=payment_details.booking_id)
                booking_data = {
                    'health_checkup_plan': booking.plan.title,
                    'booking_id': booking.id,
                    'patient_name': booking.patient.name,  # Example field
                }
                payment_data['health_checkup_details'] = booking_data

            # Now, retrieve the HDFC order status
            hdfc_response = self.get_hdfc_order_status(order_id, str(appointment.id))

            if hdfc_response.status_code == 200:
                hdfc_data = hdfc_response.json()
                payment_data['hdfc_order_status'] = hdfc_data
            else:
                logger.error(f"Failed to retrieve HDFC order status. Status Code: {hdfc_response.status_code}, Response: {hdfc_response.text}")
                return Response({"error": f"Failed to retrieve HDFC order status. Status Code: {hdfc_response.status_code}, Response: {hdfc_response.text}"}, status=hdfc_response.status_code)

            return Response(payment_data, status=status.HTTP_200_OK)

        except RazorpayPaymentDetails.DoesNotExist:
            return Response({"error": "Payment details not found."}, status=status.HTTP_404_NOT_FOUND)

    def get_hdfc_order_status(self, order_id, customer_id):
        # Replace these with actual merchant ID, customer ID, and API key
        merchant_id = "36912"
        api_key = "F74FC346C764DEE94CC2E86B208D30"

        # Base64 encode with the API key as the username and an empty string as the password
        credentials = f'{api_key}:'.encode('ascii')
        base64_credentials = base64.b64encode(credentials).decode('ascii')

        # URL for the HDFC API
        url = f'https://smartgateway.hdfcbank.com/orders/{order_id}'

        # Headers
        headers = {
            'Authorization': f'Basic {base64_credentials}',
            'version': '2023-06-30',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-merchantid': merchant_id,
            'x-customerid': customer_id,
        }

        # Make the GET request to HDFC API
        try:
            response = requests.get(url, headers=headers)
            logger.info(f"HDFC API Response Status: {response.status_code}, Body: {response.text}")
            return response  # return the full response object
        except requests.exceptions.RequestException as e:
            logger.error(f"HDFC API request failed: {str(e)}")
            return Response({"error": f"HDFC API request failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        


class InternationalMessageCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = InternationalMessageSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()  # Save the valid data to create an instance
            Notification.objects.create(
                message=f"{instance.name} applied in internation application",
                read_status=False,
                redirection_url=reverse('view_international_application', args=[instance.id]),
                object_id=instance.id,
                type='message'
            )
            return Response({"message": "Message created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




















from rest_framework.permissions import BasePermission
class CustomAPIKeyPermission(BasePermission):
    """
    Allows access only to requests with a valid API key in the headers.
    """

    def has_permission(self, request, view):
        # Retrieve the API key from headers
        api_key = request.headers.get('X-API-KEY')

        # Validate it against the custom API key in settings
        return api_key == getattr(settings, 'API_KEY_THINKB', None)




# API VIEW
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView


# get all active doctors 
class DoctorListView(ListAPIView):
    queryset = Doctor.objects.select_related('department').filter(status = True) # Optimized query
    serializer_class = DoctorApiSerializer
    permission_classes = [CustomAPIKeyPermission]  # Apply custom permission




# Doctor by id 
class DoctorDetailView(RetrieveAPIView):
    queryset = Doctor.objects.select_related('department').all()  # Eager load department for optimization
    serializer_class = DoctorApiSerializer
    permission_classes = [CustomAPIKeyPermission]  # Apply custom permission





# API View to get all departments
class DepartmentListView(ListAPIView):
    queryset = Department.objects.all()  # Fetch all departments
    serializer_class = DepartmentApiSerializer  # Use the DepartmentApiSerializer for serialization
    permission_classes = [CustomAPIKeyPermission]  # Optionally apply the custom permission



# to get department details using id 
class DepartmentDetailView(RetrieveAPIView):
    queryset = Department.objects.all()  # Eager load department for optimization
    serializer_class = DepartmentApiSerializer
    permission_classes = [CustomAPIKeyPermission]  # Apply custom permission




# API View to get all doctors in a specific department
class DoctorByDepartmentListView(ListAPIView):
    serializer_class = DoctorApiSerializer
    permission_classes = [CustomAPIKeyPermission]  # Apply custom permission

    def get_queryset(self):
        """
        Filter doctors by department ID passed in the URL.
        """
        department_id = self.kwargs['department_id']
        return Doctor.objects.filter(department_id=department_id, status=True).select_related('department')





@api_view(['GET'])
def check_available_timings_api(request, doctor_id, date):
    logger.info(f"Checking available timings for doctor {doctor_id} on date {date}")

    # Check if API Key is provided in the request headers
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        logger.error("API Key is missing in the request headers.")
        return Response({'error': 'API Key is missing.'}, status=400)
    
    # Validate the API key (example API key validation)
    if api_key != settings.API_KEY_THINKB:  # Replace with the correct key or check against a database
        logger.error(f"Invalid API Key: {api_key}")
        return Response({'error': 'Invalid API Key.'}, status=403)

    try:
        # Parse the date
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid date format: {date}")
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        # Get the doctor
        doctor = get_object_or_404(Doctor, id=doctor_id)
        logger.info(f"Doctor found: {doctor}")

        # Check if the doctor is on leave on the specified date
        if Leave.objects.filter(doctor=doctor, date=date_obj).exists():
            logger.info(f"Doctor {doctor} is on leave on {date_obj}")
            return Response({'error': 'Doctor is on leave on this day.'}, status=400)

        # Check for monthly timings with remaining slots
        monthly_timings = MonthlyTiming.objects.filter(
            doctor=doctor, 
            status='active', 
            date=date_obj, 
            remaining_slots__gte=1
        ).order_by('start_time')
        monthly_serializer = MonthlyTimingSerializer(monthly_timings, many=True)

        # Check for available times based on the day of the week
        day_of_week = date_obj.strftime('%A').lower()
        available_times = AvailableTime.objects.filter(
            doctor=doctor, 
            status='active', 
            day=day_of_week
        )

        # Filter available times based on remaining slots
        valid_available_times = []
        for available_time in available_times:
            appointments_on_same_day = Appointment.objects.filter(
                date=date_obj,
                selected_doctor=doctor,
                status='COMPLETED',
                content_type=ContentType.objects.get_for_model(AvailableTime),
                object_id=available_time.id
            ).count()
            remaining_slots = available_time.slot - appointments_on_same_day
            if remaining_slots >= 1:
                valid_available_times.append(available_time)

        # Sort the valid available times by start time before serialization
        valid_available_times.sort(key=lambda x: x.start_time)
        available_times_serializer = AvailableTimeSerializer(valid_available_times, many=True)

        # Combine both sets of timings
        combined_timings = {
            'monthly_timings': monthly_serializer.data,
            'weekly_timings': available_times_serializer.data
        }

        # Return the combined timings response
        return Response(combined_timings, status=200)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return Response({'error': 'An error occurred while checking available timings.'}, status=500)







@api_view(['GET'])
def get_appointments(request):
    from django.utils.timezone import now

    # Check if API Key is provided in the request headers
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        logger.error("API Key is missing in the request headers.")
        return Response({'error': 'API Key is missing.'}, status=400)
    
    # Validate the API key (example API key validation)
    if api_key != settings.API_KEY_THINKB:  # Replace with the correct key or check against a database
        logger.error(f"Invalid API Key: {api_key}")
        return Response({'error': 'Invalid API Key.'}, status=403)

    try:
            
        completed_appointments = Appointment.objects.filter(status="COMPLETED").order_by('-date')
        cancelled_appointments = Appointment.objects.filter(status="CANCELLED").order_by('-date')

        past_appointments = []
        upcoming_appointments_list = []
        cancelled_appointments_list = []



        # Process completed appointments
        for appointment in completed_appointments:
            payment_details = RazorpayPaymentDetails.objects.filter(status='COMPLETED', appointment=appointment).first()
            content_type = appointment.content_type
            
            try:
                related_object = content_type.get_object_for_this_type(id=appointment.object_id)
            except ObjectDoesNotExist:
                related_object = 'Timing deleted'  # Set to 'Timing deleted' if object doesn't exist
            
            # Determine the appointment_datetime
            if isinstance(related_object, AvailableTime):
                appointment_datetime = timezone.datetime.combine(appointment.date, related_object.start_time)
            elif isinstance(related_object, str) and related_object == 'Timing deleted':
                # Handle the 'Timing deleted' case by assigning a default datetime for comparison
                appointment_datetime = timezone.datetime.combine(appointment.date, timezone.datetime.min.time())
            else:
                appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)

            appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

            # Build a detailed appointment dictionary
            detailed_appointment = {
                'id': appointment.id,
                'date': appointment.date,
                'status': appointment.status,
                'doctor' : appointment.selected_doctor.name,
                'department': appointment.selected_doctor.department.title,
                'patient_name' : appointment.patient.name,
                'patient_email' : appointment.patient.email,
                'patient_number' : appointment.patient.phone_number,
                'is_pay_at_hospital' : appointment.is_pay_at_hospital,
                'related_object': {
                    'uuid': related_object.uuid if related_object else None,
                    'start_time': related_object.start_time if hasattr(related_object, 'start_time') else None,
                    'end_time': related_object.end_time if hasattr(related_object, 'end_time') else None,
                } if related_object else None,
                'payment_details': {
                    'id': payment_details.id if payment_details else 'pay_at_hospital',
                    'order_id': payment_details.order_id if payment_details else 'pay_at_hospital',
                    'amount': payment_details.amount/100 if payment_details else str(appointment.selected_doctor.fee),
                    'status': payment_details.status if payment_details else 'pay_at_hospital',
                },
            }


            print(appointment_datetime)

            if appointment_datetime < now():
                past_appointments.append(detailed_appointment)
            else:
                upcoming_appointments_list.append(detailed_appointment)


        # Process cancelled appointments
        for appointment in cancelled_appointments:
            payment_details = RazorpayPaymentDetails.objects.filter(status = 'COMPLETED',appointment=appointment).first()
            content_type = appointment.content_type
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)


            # Build a detailed appointment dictionary
            detailed_appointment = {
                'id': appointment.id,
                'date': appointment.date,
                'status': appointment.status,
                'doctor' : appointment.selected_doctor.name,
                'department': appointment.selected_doctor.department.title,
                'patient_name' : appointment.patient.name,
                'patient_email' : appointment.patient.email,
                'patient_number' : appointment.patient.phone_number,
                'is_pay_at_hospital' : appointment.is_pay_at_hospital,
                'related_object': {
                    'uuid': related_object.uuid if related_object else None,
                    'start_time': related_object.start_time if hasattr(related_object, 'start_time') else None,
                    'end_time': related_object.end_time if hasattr(related_object, 'end_time') else None,
                } if related_object else None,
                'payment_details': {
                    'id': payment_details.id if payment_details else 'pay_at_hospital',
                    'order_id': payment_details.order_id if payment_details else 'pay_at_hospital',
                    'amount': payment_details.amount/100 if payment_details else str(appointment.selected_doctor.fee),
                    'status': payment_details.status if payment_details else 'pay_at_hospital',
                },
            }
            cancelled_appointments_list.append(detailed_appointment)









        # Combine both sets of timings
        appointments_data = {
            'upcoming_appointments_list': upcoming_appointments_list,
            'cancelled_appointments_list': cancelled_appointments_list,
            'past_appointments': past_appointments,
        }

        # Return the combined timings response
        return Response(appointments_data, status=200)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return Response({'error': 'An error occurred while checking appointments.'}, status=500)




@api_view(['GET'])
def filter_appointments(request):
    from django.utils.timezone import now

    # Check if API Key is provided in the request headers
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        logger.error("API Key is missing in the request headers.")
        return Response({'error': 'API Key is missing.'}, status=400)
    
    # Validate the API key (example API key validation)
    if api_key != settings.API_KEY_THINKB:  # Replace with the correct key or check against a database
        logger.error(f"Invalid API Key: {api_key}")
        return Response({'error': 'Invalid API Key.'}, status=403)

    try:
        # Get query parameters for filtering
        patient_name = request.query_params.get('patient_name', None)
        patient_email = request.query_params.get('patient_email', None)
        department = request.query_params.get('department', None)
        doctor_name = request.query_params.get('doctor_name', None)

        # Start with all appointments
        queryset = Appointment.objects.filter(status='COMPLETED').order_by('-date')

        # Apply filters based on query parameters
        if patient_name:
            queryset = queryset.filter(patient__name__icontains=patient_name)
        if patient_email:
            queryset = queryset.filter(patient__email__icontains=patient_email)
        if department:
            queryset = queryset.filter(department__title__icontains=department)
        if doctor_name:
            queryset = queryset.filter(selected_doctor__name__icontains=doctor_name)

        # Separate appointments into past, upcoming, and cancelled
        past_appointments = []
        upcoming_appointments = []
        cancelled_appointments = []

        for appointment in queryset:
            payment_details = RazorpayPaymentDetails.objects.filter(status='COMPLETED', appointment=appointment).first()
            content_type = appointment.content_type
            
            try:
                related_object = content_type.get_object_for_this_type(id=appointment.object_id)
            except ObjectDoesNotExist:
                related_object = 'Timing deleted'  # Set to 'Timing deleted' if object doesn't exist
            
            # Determine the appointment_datetime
            if isinstance(related_object, AvailableTime):
                appointment_datetime = timezone.datetime.combine(appointment.date, related_object.start_time)
            elif isinstance(related_object, str) and related_object == 'Timing deleted':
                # Handle the 'Timing deleted' case by assigning a default datetime for comparison
                appointment_datetime = timezone.datetime.combine(appointment.date, timezone.datetime.min.time())
            else:
                appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)

            appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

            # Build a detailed appointment dictionary
            detailed_appointment = {
                'id': appointment.id,
                'date': appointment.date,
                'status': appointment.status,
                'doctor': appointment.selected_doctor.name,
                'department': appointment.selected_doctor.department.title,
                'patient_name': appointment.patient.name,
                'patient_email': appointment.patient.email,
                'patient_number': appointment.patient.phone_number,
                'is_pay_at_hospital': appointment.is_pay_at_hospital,
                'related_object': {
                    'uuid': related_object.uuid if related_object else None,
                    'start_time': related_object.start_time if hasattr(related_object, 'start_time') else None,
                    'end_time': related_object.end_time if hasattr(related_object, 'end_time') else None,
                } if related_object else None,
                'payment_details': {
                    'id': payment_details.id if payment_details else 'pay_at_hospital',
                    'order_id': payment_details.order_id if payment_details else 'pay_at_hospital',
                    'amount': payment_details.amount / 100 if payment_details else str(appointment.selected_doctor.fee),
                    'status': payment_details.status if payment_details else 'pay_at_hospital',
                },
            }

            # Categorize appointments
            if appointment.status == 'CANCELLED':
                cancelled_appointments.append(detailed_appointment)
            elif appointment_datetime < now():
                past_appointments.append(detailed_appointment)
            else:
                upcoming_appointments.append(detailed_appointment)

        # Return the categorized appointments
        appointments_data = {
            'past_appointments': past_appointments,
            'upcoming_appointments': upcoming_appointments,
            'cancelled_appointments': cancelled_appointments,
        }

        return Response(appointments_data, status=200)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return Response({'error': 'An error occurred while filtering appointments.'}, status=500)

@api_view(['GET'])
def get_appointment_details(request, pk):
    """
    Fetch details of a specific appointment by its ID.
    """
    # Check if API Key is provided in the request headers
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        logger.error("API Key is missing in the request headers.")
        return Response({'error': 'API Key is missing.'}, status=400)
    
    # Validate the API key (example API key validation)
    if api_key != settings.API_KEY_THINKB:  # Replace with the correct key or check against a database
        logger.error(f"Invalid API Key: {api_key}")
        return Response({'error': 'Invalid API Key.'}, status=403)


    try:
        # Fetch the appointment
        appointment = get_object_or_404(Appointment, id=pk)

        if appointment.status == "PENDING":
            return Response({'error': 'Appointment is not booked.'}, status=400)

        payment_details = RazorpayPaymentDetails.objects.filter(status = 'COMPLETED',appointment=appointment).first()
        content_type = appointment.content_type
        related_object = content_type.get_object_for_this_type(id=appointment.object_id)


        # Build a detailed appointment dictionary
        detailed_appointment = {
            'id': appointment.id,
            'date': appointment.date,
            'status': appointment.status,
            'doctor' : appointment.selected_doctor.name,
            'department': appointment.selected_doctor.department.title,
            'patient_name' : appointment.patient.name,
            'patient_email' : appointment.patient.email,
            'patient_number' : appointment.patient.phone_number,
            'is_pay_at_hospital' : appointment.is_pay_at_hospital,
            'related_object': {
                'uuid': related_object.uuid if related_object else None,
                'start_time': related_object.start_time if hasattr(related_object, 'start_time') else None,
                'end_time': related_object.end_time if hasattr(related_object, 'end_time') else None,
            } if related_object else None,
            'payment_details': {
                'id': payment_details.id if payment_details else 'pay_at_hospital',
                'order_id': payment_details.order_id if payment_details else 'pay_at_hospital',
                'amount': payment_details.amount/100 if payment_details else str(appointment.selected_doctor.fee),
                'status': payment_details.status if payment_details else 'pay_at_hospital',
            },
        }
            
        return Response({'appointment_details': detailed_appointment}, status=200)
        


    except Exception as e:
        logger.error(f"Error fetching appointment details: {e}")
        return Response({'error': 'An error occurred while fetching appointment details.'}, status=500)





# get timing and doctors by department wise
@api_view(['GET'])
def get_doctors_by_department_and_date(request, department_id, date):
    logger.info(f"Fetching doctors in department {department_id} available on date {date}")
    
    # Check if API Key is provided in the request headers
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        logger.error("API Key is missing in the request headers.")
        return Response({'error': 'API Key is missing.'}, status=400)
    
    # Validate the API key (example API key validation)
    if api_key != settings.API_KEY_THINKB:  # Replace with the correct key or check against a database
        logger.error(f"Invalid API Key: {api_key}")
        return Response({'error': 'Invalid API Key.'}, status=403)

    try:
        # Parse the date
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid date format: {date}")
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        # Get all doctors in the given department
        doctors_in_department = Doctor.objects.filter(department_id=department_id)
        if not doctors_in_department:
            return Response({'error': 'No doctors found in this department.'}, status=404)
        
        available_doctors = []

        # Check each doctor for available timings and if they're on leave
        for doctor in doctors_in_department:
            logger.info(f"Checking availability for doctor {doctor.name}")

            # Check if the doctor is on leave on the specified date
            if Leave.objects.filter(doctor=doctor, date=date_obj).exists():
                logger.info(f"Doctor {doctor.name} is on leave on {date_obj}")
                continue  # Skip this doctor

            # Check for monthly timings with remaining slots
            monthly_timings = MonthlyTiming.objects.filter(
                doctor=doctor, 
                status='active', 
                date=date_obj, 
                remaining_slots__gte=1
            ).order_by('start_time')
            monthly_serializer = MonthlyTimingSerializer(monthly_timings, many=True)

            # Check for weekly available times (based on day of week)
            day_of_week = date_obj.strftime('%A').lower()  # Get the day of the week (e.g., 'monday')
            available_times = AvailableTime.objects.filter(
                doctor=doctor, 
                status='active', 
                day=day_of_week
            )

            # Filter available times based on remaining slots
            valid_available_times = []
            for available_time in available_times:
                # Count appointments on the same day and calculate remaining slots
                appointments_on_same_day = Appointment.objects.filter(
                    date=date_obj,
                    selected_doctor=doctor,
                    status='COMPLETED',
                    content_type=ContentType.objects.get_for_model(AvailableTime),
                    object_id=available_time.id
                ).count()
                remaining_slots = available_time.slot - appointments_on_same_day
                if remaining_slots >= 1:
                    valid_available_times.append(available_time)

            # If either monthly timings or weekly available times exist, include the doctor
            if monthly_timings.exists() or valid_available_times:
                doctor_data = DoctorApiSerializer(doctor).data
                doctor_data['monthly_timings'] = MonthlyTimingSerializer(monthly_timings, many=True).data
                doctor_data['weekly_timings'] = AvailableTimeSerializer(valid_available_times, many=True).data
                available_doctors.append(doctor_data)

        # If no doctors are available, return an appropriate response
        if not available_doctors:
            return Response({'error': 'No doctors available on this date.'}, status=404)

        # Return the list of available doctors with their timings
        return Response({'available_doctors': available_doctors}, status=200)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return Response({'error': 'An error occurred while fetching doctor availability.'}, status=500)






# book appointment api 

@method_decorator(csrf_exempt, name='dispatch')
class CreateAppointmentAppAPIView(APIView):
    def post(self, request, *args, **kwargs):


        # Check if API Key is provided in the request headers
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            logger.error("API Key is missing in the request headers.")
            return Response({'error': 'API Key is missing.'}, status=400)
        
        # Validate the API key (example API key validation)
        if api_key != settings.API_KEY_THINKB:  # Replace with the correct key or check against a database
            logger.error(f"Invalid API Key: {api_key}")
            return Response({'error': 'Invalid API Key.'}, status=403)



        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        disease = request.data.get('disease') or ''
        date = request.data.get('date')
        message = request.data.get('message') or ''

        date = request.data.get('date')
        message = request.data.get('message')
        department_id = request.data.get('department')
        doctor_id = request.data.get('selected_doctor')
        payment_method = request.data.get('payment_method', 'online')  # Default to 'online' if not provided
        schedule_id = request.data.get('schedule_id')
        gender = request.data.get('gender')
        registration_fee_include = request.data.get('registration_fee')
        discount_percentage = float(request.data.get('discount', 0))  # Get discount percentage

        registration_fee = 'paid'

        if registration_fee_include == 'on':
            registration_fee = 'unpaid'

        # Debug statements
        print(f"Name: {name}, Email: {email}, Phone: {phone_number}, Disease: {disease}, Gender: {gender}")
        print(f"Date: {date}, Message: {message}, Department: {department_id}")
        print(f"Doctor: {doctor_id}, Payment Method: {payment_method}, Schedule ID: {schedule_id}")
        print(f"Discount: {discount_percentage}%")


        if not name:
            return Response({"error": "Name is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not phone_number:
            return Response({"error": "Phone Number is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not gender:
            return Response({"error": "Gender is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not doctor_id:
            return Response({"error": "Doctor is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not schedule_id:
            return Response({"error": "Timing is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not department_id:
            return Response({"error": "Department is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not date:
            return Response({"error": "Appointment Date is required."}, status=status.HTTP_400_BAD_REQUEST)

        doctor = get_object_or_404(Doctor, id=doctor_id)
        leave_exists = Leave.objects.filter(doctor=doctor, date=date).exists()
        if leave_exists:
            return Response({"error": "The selected doctor is on leave on the specified date."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or get patient
        patient, created = Patient.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone_number': phone_number, 'disease': disease, 'gender': gender}
        )

        # Get department and doctor
        department = get_object_or_404(Department, id=department_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)


        if doctor.department != department:
            return Response(
                {"error": "The selected doctor does not belong to the selected department."}, 
                status=400
            )


        # Determine if the schedule is monthly or weekly
        try:
            monthly_timing = MonthlyTiming.objects.get(uuid=schedule_id)
            if monthly_timing.doctor != doctor :
                return Response({"error": "This timing is not to this doctor"}, status=status.HTTP_400_BAD_REQUEST)
            content_type = ContentType.objects.get_for_model(MonthlyTiming)
            object_id = monthly_timing.id
            start_time = monthly_timing.start_time
        except MonthlyTiming.DoesNotExist:
            available_time = get_object_or_404(AvailableTime, uuid=schedule_id)
            if available_time.doctor != doctor :
                return Response({"error": "This timing is not to this doctor"}, status=status.HTTP_400_BAD_REQUEST)


            appointments_on_same_day = Appointment.objects.filter(
                date=date,
                selected_doctor=doctor,
                status='COMPLETED',
                content_type=ContentType.objects.get_for_model(AvailableTime),
                object_id=available_time.id
            ).count()
            remaining_slots = available_time.slot - appointments_on_same_day
            if remaining_slots <= 0:
                print("SADFSDFAsd")
                return Response({"error": "This slot is filled"}, status=status.HTTP_400_BAD_REQUEST)

                
            content_type = ContentType.objects.get_for_model(AvailableTime)
            object_id = available_time.id
            start_time = available_time.start_time

        # Combine date and start_time to form a datetime
        appointment_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        appointment_datetime = timezone.datetime.combine(appointment_date, start_time)
        appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

        if appointment_datetime <= timezone.now():
            return Response({"error": "The appointment datetime must be in the future."}, status=status.HTTP_400_BAD_REQUEST)

        
        if payment_method == 'online':
            
            # Create appointment
            appointment = Appointment.objects.create(
                date=date,
                message=message,
                payment_id='',  # This will be filled after Razorpay payment if online
                payment_method=payment_method,
                patient=patient,
                department=department,
                selected_doctor=doctor,
                content_type=content_type,
                object_id=object_id,
                is_app = True,
                status='PENDING' if payment_method == 'online' else 'COMPLETED',
                discount=discount_percentage  # Save discount percentage
            )

            amount = int(doctor.fee) * 100  # amount in paise
            if registration_fee != 'paid':
                amount += 27000  # add registration fee in paise

            # Apply discount
            if discount_percentage > 0:
                discount_amount = (amount * discount_percentage) / 100
                amount -= int(discount_amount)

            # Initialize Razorpay client
            try:
                payment__id = str(uuid.uuid4())
                # Create a new RazorpayPaymentDetails record
                RazorpayPaymentDetails.objects.create(
                    payment_id= payment__id,  # Generate a custom UUID
                    order_id='order_id',
                    signature='',
                    amount=amount,
                    currency='INR',
                    payment_method='online',
                    status='PENDING',  # Mark as completed
                    appointment=appointment
                )
                # Your business logic
                response_data = {
                    'payment_id' : payment__id,
                    'hdfc_payment_url': f'https://vshhospital.com/static/payments/initiatePaymentApi.php?appointment_id={appointment.id}&amount={amount}'
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': 'An error occurred: ' + str(e)}, status=500)

        
        elif payment_method == 'pay_at_hospital':        

        
            # Create appointment
            appointment = Appointment.objects.create(
                date=date,
                message=message,
                payment_id='',  # This will be filled after Razorpay payment if online
                payment_method=payment_method,
                patient=patient,
                department=department,
                selected_doctor=doctor,
                content_type=content_type,
                object_id=object_id,
                is_pay_at_hospital = True,
                is_app = True,
                status='PENDING' if payment_method == 'online' else 'COMPLETED',
                discount=discount_percentage  # Save discount percentage
            )

            amount = int(doctor.fee) * 100  # amount in paise
            if registration_fee != 'paid':
                amount += 27000  # add registration fee in paise

            # Apply discount
            if discount_percentage > 0:
                discount_amount = (amount * discount_percentage) / 100
                amount -= int(discount_amount)



            Notification.objects.create(
                message=f"{appointment.patient.name} booked an appointment with {appointment.selected_doctor.name} for Pay at Hospital",
                read_status=False,
                redirection_url=reverse('view_appointment', args=[appointment.id]),
                object_id=appointment.id,
                type='appointment'
            )



            RazorpayPaymentDetails.objects.create(
                payment_id=str(uuid.uuid4()),  # Generate a custom UUID
                order_id='',
                signature='',
                amount=amount,
                currency='INR',
                payment_method='cash',
                status='PENDING',  # Directly mark as completed for cash payments
                appointment=appointment
            )
            
            detailed_appointment = {
                'id': appointment.id,
                'date': appointment.date,
                'status': appointment.status,
                'doctor' : appointment.selected_doctor.name,
                'department': appointment.selected_doctor.department.title,
                'patient_name' : appointment.patient.name,
                'patient_email' : appointment.patient.email,
                'patient_number' : appointment.patient.phone_number,
            }


            return Response(detailed_appointment, status=200)
        
        else:
            
            return Response({"error": "Payment Method is not allowed"}, status=status.HTTP_400_BAD_REQUEST)



    def get(self, request, *args, **kwargs):
        return Response({"error": "Only Post Method Allowed"}, status=status.HTTP_400_BAD_REQUEST)




def acl_payment_success(request):
    return render(request, 'frontend/acl-payment-success.html')







def update_appointment_status_api(request):
    # Take parameters from request (GET or POST)
    appointment_id = request.GET.get('appointment_id') or request.POST.get('appointment_id')
    amount = request.GET.get('amount') or request.POST.get('amount')
    order_id = request.GET.get('order_id') or request.POST.get('order_id')

    # Validate that we have all the necessary parameters
    if not appointment_id or not amount or not order_id:
        return JsonResponse({"error": "Missing required parameters."}, status=400)

    # Convert amount to integer
    try:
        amount = int(amount)
    except ValueError:
        return JsonResponse({"error": "Invalid amount format."}, status=400)

    # Retrieve the HDFC order status
    hdfc_response = get_hdfc_order_status(order_id, str(appointment_id))
    if hdfc_response.get('status') == 'CHARGED':
        # Fetch the appointment object
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Update the appointment status to 'COMPLETED'
        appointment.status = 'COMPLETED'
        appointment.save()

        # Check if a RazorpayPaymentDetails record already exists
        if not RazorpayPaymentDetails.objects.filter(appointment=appointment).exists():
            # Create a new RazorpayPaymentDetails record
            RazorpayPaymentDetails.objects.create(
                payment_id=str(uuid.uuid4()),  # Generate a custom UUID
                order_id=order_id,
                signature='',
                amount=amount,
                currency='INR',
                payment_method='online',
                status='COMPLETED',  # Mark as completed
                appointment=appointment
            )

            # Create notifications for the patient and doctor
            Notification.objects.create(
                message=f"{appointment.patient.name} booked an appointment with {appointment.selected_doctor.name} for ₹ {amount / 100}",  # Amount in INR
                read_status=False,
                redirection_url=reverse('view_appointment', args=[appointment.id]),
                object_id=appointment.id,
                type='appointment'
            )


        else:

            razorpay_details = RazorpayPaymentDetails.objects.filter(appointment=appointment).first()
            razorpay_details.status='COMPLETED'
            razorpay_details.order_id=order_id
            razorpay_details.amount=amount
            razorpay_details.payment_method='online'
            razorpay_details.save()

            
            # Create notifications for the patient and doctor
            Notification.objects.create(
                message=f"{appointment.patient.name} booked an appointment with {appointment.selected_doctor.name} for ₹ {amount / 100}",  # Amount in INR
                read_status=False,
                redirection_url=reverse('view_appointment', args=[appointment.id]),
                object_id=appointment.id,
                type='appointment'
            )


        # Additional actions if appointment status is completed
        if appointment.status == 'COMPLETED':
            content_type = appointment.content_type
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)

            # Determine the timing
            if isinstance(related_object, AvailableTime):
                start_time = related_object.start_time
                end_time = related_object.end_time
            else:
                start_time = related_object.start_time
                end_time = related_object.end_time


            return JsonResponse(
                {
                    "success": "Appointment status updated and notifications sent.",
                    "appointment": {
                        "id": appointment.id,
                        "patient_name": appointment.patient.name,
                        "doctor_name": appointment.selected_doctor.name,
                        "scheduled_date": appointment.date,
                        "start_time" : start_time,
                        "end_time" : end_time,
                    },
                    "payment_details": {
                        "order_id": order_id,
                        "amount": amount/100,
                        "currency": "INR",
                        "payment_method": "online",
                    },
                },
                status=200,
            )
    # Handle failed or uncharged payment
    return JsonResponse({"error": "Payment verification failed or not charged."}, status=400)

        






class GetPaymentDetailsByOrderIdForApp(APIView):

    def get(self, request, order_id):
        try:
            # Get payment details from local DB
            payment_details = RazorpayPaymentDetails.objects.get(status = 'COMPLETED', order_id=order_id)

            payment_data = {
                'amount': payment_details.amount / 100,
                'order_id': payment_details.order_id,
                'payment_id': payment_details.payment_id,
            }

            # Check if it's for an appointment or health checkup
            if payment_details.payment_for == 'APPOINTMENT':
                appointment = get_object_or_404(Appointment, id=payment_details.appointment_id)
                appointment_data = {
                    'appointment_id': appointment.id,
                    'patient_name': appointment.patient.name,  # Example field
                    'doctor_name': appointment.selected_doctor.name,  # Example field
                    'appointment_date': appointment.date,  # Example field
                }
                payment_data['appointment_details'] = appointment_data

            else:
                booking = get_object_or_404(HealthCheckupBooking, id=payment_details.booking_id)
                booking_data = {
                    'health_checkup_plan': booking.plan.title,
                    'booking_id': booking.id,
                    'patient_name': booking.patient.name,  # Example field
                }
                payment_data['health_checkup_details'] = booking_data

            # Now, retrieve the HDFC order status
            hdfc_response = self.get_hdfc_order_status(order_id, str(appointment.id))

            if hdfc_response.status_code == 200:
                hdfc_data = hdfc_response.json()
                payment_data['hdfc_order_status'] = hdfc_data
            else:
                logger.error(f"Failed to retrieve HDFC order status. Status Code: {hdfc_response.status_code}, Response: {hdfc_response.text}")
                return Response({"error": f"Failed to retrieve HDFC order status. Status Code: {hdfc_response.status_code}, Response: {hdfc_response.text}"}, status=hdfc_response.status_code)

            return Response(payment_data, status=status.HTTP_200_OK)

        except RazorpayPaymentDetails.DoesNotExist:
            return Response({"error": "Payment details not found."}, status=status.HTTP_404_NOT_FOUND)

    def get_hdfc_order_status(self, order_id, customer_id):
        # Replace these with actual merchant ID, customer ID, and API key
        merchant_id = "36912"
        api_key = "F74FC346C764DEE94CC2E86B208D30"

        # Base64 encode with the API key as the username and an empty string as the password
        credentials = f'{api_key}:'.encode('ascii')
        base64_credentials = base64.b64encode(credentials).decode('ascii')

        # URL for the HDFC API
        url = f'https://smartgateway.hdfcbank.com/orders/{order_id}'

        # Headers
        headers = {
            'Authorization': f'Basic {base64_credentials}',
            'version': '2023-06-30',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-merchantid': merchant_id,
            'x-customerid': customer_id,
        }

        # Make the GET request to HDFC API
        try:
            response = requests.get(url, headers=headers)
            logger.info(f"HDFC API Response Status: {response.status_code}, Body: {response.text}")
            return response  # return the full response object
        except requests.exceptions.RequestException as e:
            logger.error(f"HDFC API request failed: {str(e)}")
            return Response({"error": f"HDFC API request failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class GetPaymentDetailsByPaymentIdForApp(APIView):

    def get(self, request, payment_id):
        try:
            # Get payment details from local DB
            payment_details = RazorpayPaymentDetails.objects.get(status = 'COMPLETED', payment_id=payment_id)
            order_id = payment_details.order_id

            payment_data = {
                'amount': payment_details.amount / 100,
                'order_id': payment_details.order_id,
                'payment_id': payment_details.payment_id,
            }

            # Check if it's for an appointment or health checkup
            if payment_details.payment_for == 'APPOINTMENT':
                appointment = get_object_or_404(Appointment, id=payment_details.appointment_id)
                appointment_data = {
                    'appointment_id': appointment.id,
                    'patient_name': appointment.patient.name,  # Example field
                    'doctor_name': appointment.selected_doctor.name,  # Example field
                    'appointment_date': appointment.date,  # Example field
                }
                payment_data['appointment_details'] = appointment_data

            else:
                booking = get_object_or_404(HealthCheckupBooking, id=payment_details.booking_id)
                booking_data = {
                    'health_checkup_plan': booking.plan.title,
                    'booking_id': booking.id,
                    'patient_name': booking.patient.name,  # Example field
                }
                payment_data['health_checkup_details'] = booking_data

            # Now, retrieve the HDFC order status
            hdfc_response = self.get_hdfc_order_status(order_id, str(appointment.id))

            if hdfc_response.status_code == 200:
                hdfc_data = hdfc_response.json()
                payment_data['hdfc_order_status'] = hdfc_data
            else:
                logger.error(f"Failed to retrieve HDFC order status. Status Code: {hdfc_response.status_code}, Response: {hdfc_response.text}")
                return Response({"error": f"Failed to retrieve HDFC order status. Status Code: {hdfc_response.status_code}, Response: {hdfc_response.text}"}, status=hdfc_response.status_code)

            return Response(payment_data, status=status.HTTP_200_OK)

        except RazorpayPaymentDetails.DoesNotExist:
            return Response({"error": "Payment details not found."}, status=status.HTTP_404_NOT_FOUND)

    def get_hdfc_order_status(self, order_id, customer_id):
        # Replace these with actual merchant ID, customer ID, and API key
        merchant_id = "36912"
        api_key = "F74FC346C764DEE94CC2E86B208D30"

        # Base64 encode with the API key as the username and an empty string as the password
        credentials = f'{api_key}:'.encode('ascii')
        base64_credentials = base64.b64encode(credentials).decode('ascii')

        # URL for the HDFC API
        url = f'https://smartgateway.hdfcbank.com/orders/{order_id}'

        # Headers
        headers = {
            'Authorization': f'Basic {base64_credentials}',
            'version': '2023-06-30',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-merchantid': merchant_id,
            'x-customerid': customer_id,
        }

        # Make the GET request to HDFC API
        try:
            response = requests.get(url, headers=headers)
            logger.info(f"HDFC API Response Status: {response.status_code}, Body: {response.text}")
            return response  # return the full response object
        except requests.exceptions.RequestException as e:
            logger.error(f"HDFC API request failed: {str(e)}")
            return Response({"error": f"HDFC API request failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
import json
import random
import time




def send_otp(phone_number, otp):
    """
    Sends OTP using the 2Factor API.
    """
    url = f"https://2factor.in/API/V1/{settings.TWO_FACTOR_API_KEY}/SMS/{phone_number}/{otp}"
    try:
        response = requests.get(url)
        # Log the response content for debugging
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        # Check if response is JSON
        if response.headers.get("Content-Type") == "application/json":
            return response.json()
        else:
            return {"error": "Non-JSON response received", "details": response.text}
    except Exception as e:
        return {"error": "Failed to send OTP", "details": str(e)}





def generate_otp():
    """Generate a random 4-digit OTP."""
    return str(random.randint(1000, 9999))


# Add session timeout check to prevent multiple OTP requests in a short period
OTP_COOLDOWN_TIME = 45  # seconds

@csrf_protect
def send_otp_view(request):
    if request.method == "POST":
        body = json.loads(request.body)
        phone_number = body.get("phone")
        otp = str(random.randint(1000, 9999))  # Generate a dynamic OTP

        if not phone_number:
            return JsonResponse({"error": "Phone number is required"}, status=400)

        # Check if OTP was sent recently (cooldown logic)
        last_sent_time = request.session.get(f"last_otp_sent_for_{phone_number}")
        current_time = time.time()

        if last_sent_time and (current_time - last_sent_time) < OTP_COOLDOWN_TIME:
            # If OTP was sent within the cooldown period, reject the request
            remaining_time = OTP_COOLDOWN_TIME - (current_time - last_sent_time)
            return JsonResponse({
                "error": f"Please wait {int(remaining_time)} seconds before requesting OTP again."
            }, status=400)

        # Store the OTP in the session for verification
        request.session[f"otp_for_{phone_number}"] = otp
        request.session[f"last_otp_sent_for_{phone_number}"] = current_time

        # Send OTP (using your existing method for OTP sending)
        response = send_otp(phone_number, otp)

        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request method"}, status=405)



@csrf_protect
def verify_otp_view(request):
    if request.method == "POST":
        try:
            # Parse the JSON body
            body = json.loads(request.body)
            phone_number = body.get("phone")
            entered_otp = body.get("otp")

            if not phone_number or not entered_otp:
                return JsonResponse({"error": "Phone number and OTP are required"}, status=400)

            # Retrieve the stored OTP from the session
            stored_otp = request.session.get(f"otp_for_{phone_number}")

            if stored_otp == entered_otp:
                # OTP verified successfully
                # Optionally clear the OTP from the session
                del request.session[f"otp_for_{phone_number}"]

                # Create a new PatientProfile or retrieve an existing one
                profile, created = PatientProfile.objects.get_or_create(
                    number=phone_number,
                    defaults={"uuid": uuid.uuid4()},
                )
                
                # Store UUID and phone number in the session
                request.session['uuid'] = str(profile.uuid)
                request.session['phone_number'] = profile.number

                # Return success response with UUID and phone number
                return JsonResponse({
                    "success": "OTP verified successfully",
                    "uuid": str(profile.uuid),
                    "phone_number": profile.number,
                })


            # OTP does not match
            return JsonResponse({"error": "Invalid OTP"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
        except Exception as e:
            return JsonResponse({"error": "An error occurred", "details": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)













class CreateAppointmentVideoAPIView(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        disease = request.data.get('disease') or ''
        date = request.data.get('date')
        message = request.data.get('message') or ''
        uuid = request.data.get('uu_id')

        date = request.data.get('date')
        message = request.data.get('message')
        department_id = request.data.get('department')
        doctor_id = request.data.get('selected_doctor')
        payment_method = request.data.get('payment_method', 'online')  # Default to 'online' if not provided
        schedule_id = request.data.get('schedule_id')
        gender = request.data.get('gender')
        registration_fee_include = request.data.get('registration_fee')
        discount_percentage = float(request.data.get('discount', 0))  # Get discount percentage

        registration_fee = 'paid'

        if registration_fee_include == 'on':
            registration_fee = 'unpaid'

        # Debug statements
        print(f"Name: {name}, Email: {email}, Phone: {phone_number}, Disease: {disease}, Gender: {gender}")
        print(f"Date: {date}, Message: {message}, Department: {department_id}")
        print(f"Doctor: {doctor_id}, Payment Method: {payment_method}, Schedule ID: {schedule_id}")
        print(f"Discount: {discount_percentage}%")

        # Check if all required fields are present
        if not all([name, email, phone_number, date, department_id, doctor_id, schedule_id, gender]):
            return Response({"error": "Missing one or more required fields."}, status=status.HTTP_400_BAD_REQUEST)

        if not uuid:
            return Response({"error": "Not Logged In"}, status=status.HTTP_400_BAD_REQUEST)

        doctor = get_object_or_404(Doctor, id=doctor_id)
        leave_exists = Leave.objects.filter(doctor=doctor, date=date).exists()
        if leave_exists:
            return Response({"error": "The selected doctor is on leave on the specified date."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or get patient
        patient, created = Patient.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone_number': phone_number, 'disease': disease, 'gender': gender}
        )

        # Get department and doctor
        department = get_object_or_404(Department, id=department_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Determine if the schedule is monthly or weekly
        try:
            monthly_timing = MonthlyTiming.objects.get(uuid=schedule_id)
            content_type = ContentType.objects.get_for_model(MonthlyTiming)
            object_id = monthly_timing.id
            start_time = monthly_timing.start_time
        except MonthlyTiming.DoesNotExist:
            available_time = get_object_or_404(AvailableTime, uuid=schedule_id)
            content_type = ContentType.objects.get_for_model(AvailableTime)
            object_id = available_time.id
            start_time = available_time.start_time

        # Combine date and start_time to form a datetime
        appointment_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        appointment_datetime = timezone.datetime.combine(appointment_date, start_time)
        appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

        if appointment_datetime <= timezone.now():
            return Response({"error": "The appointment datetime must be in the future."}, status=status.HTTP_400_BAD_REQUEST)

        # Create appointment
        appointment = Appointment.objects.create(
            date=date,
            message=message,
            payment_id='',  # This will be filled after Razorpay payment if online
            payment_method=payment_method,
            patient=patient,
            department=department,
            selected_doctor=doctor,
            content_type=content_type,
            object_id=object_id,
            user_id = uuid,
            is_video = True,
            status='PENDING' if payment_method == 'online' else 'COMPLETED',
            discount=discount_percentage  # Save discount percentage
        )

        amount = int(doctor.fee) * 100  # amount in paise
        if registration_fee != 'paid':
            amount += 27000  # add registration fee in paise

        # Apply discount
        if discount_percentage > 0:
            discount_amount = (amount * discount_percentage) / 100
            amount -= int(discount_amount)

        if payment_method == 'cash':
            if not request.user.is_superuser:
                Notification.objects.create(
                    message=f"{appointment.patient.name} booked an appointment with {appointment.selected_doctor.name} for ₹ {amount / 100}",
                    read_status=False,
                    redirection_url=reverse('view_appointment', args=[appointment.id]),
                    object_id=appointment.id,
                    type='appointment'
                )



        if payment_method == 'online':
            # Initialize Razorpay client
            try:
                # Your business logic
                response_data = {
                    'hdfc_payment_url': f'https://vshhospital.com/static/payments/initiatePayment.php?appointment_id={appointment.id}&amount={amount}'
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': 'An error occurred: ' + str(e)}, status=500)

                
           
        else:
            # Create RazorpayPaymentDetails with custom ID for cash payments
            RazorpayPaymentDetails.objects.create(
                payment_id=str(uuid.uuid4()),  # Generate a custom UUID
                order_id='',
                signature='',
                amount=amount,
                currency='INR',
                payment_method='cash',
                status='COMPLETED',  # Directly mark as completed for cash payments
                appointment=appointment
            )

        # Return response for non-online payment method
        return Response({
            'appointment_id': appointment.id,
            'name': name,
            'email': email,
            'phone_number': phone_number,
            'description': 'Appointment Booking'
        }, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        doctors = Doctor.objects.all()
        departments = Department.objects.all()
        available_times = AvailableTime.objects.all()
        monthly_timings = MonthlyTiming.objects.all()

        data = {
            'doctors': [{'id': doctor.id, 'name': doctor.name} for doctor in doctors],
            'departments': [{'id': department.id, 'title': department.title} for department in departments],
            'available_times': [{'uuid': time.uuid, 'start_time': time.start_time, 'end_time': time.end_time} for time in available_times],
            'monthly_timings': [{'uuid': timing.uuid, 'start_time': timing.start_time, 'end_time': timing.end_time} for timing in monthly_timings],
        }
        return Response(data, status=status.HTTP_200_OK)







def online_consultation(request):
    # Get UUID from the session
    user_uuid = request.session.get('uuid')
    
    # Fetch all appointments with user_id equal to the UUID and having video consultations
    appointments = Appointment.objects.filter(user_id=user_uuid, is_video=True).order_by('-date') if user_uuid else []
    
    my_appointments = []

    
    # Process completed appointments
    for appointment in appointments:
        content_type = appointment.content_type
        
        try:
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)
        except ObjectDoesNotExist:
            related_object = 'Timing deleted'  # Set to 'Timing deleted' if object doesn't exist
        
        # Determine the appointment_datetime
        if isinstance(related_object, AvailableTime):
            appointment_datetime = timezone.datetime.combine(appointment.date, related_object.start_time)
        elif isinstance(related_object, str) and related_object == 'Timing deleted':
            # Handle the 'Timing deleted' case by assigning a default datetime for comparison
            appointment_datetime = timezone.datetime.combine(appointment.date, timezone.datetime.min.time())
        else:
            appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)

        appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

        detailed_appointment = {
            'appointment': appointment,
            'related_object': related_object
        }

        my_appointments.append(detailed_appointment)

    
    # Fetch active departments
    departments = Department.objects.filter(status=True)
    
    # Prepare context for the template
    context = {
        'departments': departments,
        'my_appointments': my_appointments,
    }
    
    return render(request, 'frontend/online-consultation.html', context)





def open_video_call(request, pk):
    # Fetch the appointment or return a 404 if it doesn't exist
    appointment = get_object_or_404(Appointment, id=pk)

    if appointment.status != 'COMPLETED':  # Assuming 'status' is a field in your Appointment model
        return render(request, 'frontend/error.html', {'error': 'Payment or completion pending.'})


    # Check if the appointment is for a video consultation
    if not appointment.is_video:
        # Return an error message if the condition is not met
        error_message = "This appointment is not a video consultation."
        return render(request, 'frontend/error.html', {'error_message': error_message})


    content_type = appointment.content_type
    
    try:
        related_object = content_type.get_object_for_this_type(id=appointment.object_id)
    except ObjectDoesNotExist:
        related_object = 'Timing deleted'  # Set to 'Timing deleted' if object doesn't exist
        
    # Determine the appointment_datetime
    if isinstance(related_object, AvailableTime):
        appointment_datetime = timezone.datetime.combine(appointment.date, related_object.end_time)
    elif isinstance(related_object, str) and related_object == 'Timing deleted':
        # Handle the 'Timing deleted' case by assigning a default datetime for comparison
        appointment_datetime = timezone.datetime.combine(appointment.date, timezone.datetime.min.time())
    else:
        appointment_datetime = timezone.datetime.combine(related_object.date, related_object.end_time)

    appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())
    meeting_end_time = appointment_datetime

    # Get the current time
    current_time = now()

    # Check if the appointment time has already passed
    if appointment_datetime < current_time:
        error_message = "Meeting has ended or is no longer available."
        return render(request, 'frontend/error.html', {'error': error_message})


    # Determine the appointment_datetime
    if isinstance(related_object, AvailableTime):
        appointment_datetime = timezone.datetime.combine(appointment.date, related_object.start_time)
    elif isinstance(related_object, str) and related_object == 'Timing deleted':
        # Handle the 'Timing deleted' case by assigning a default datetime for comparison
        appointment_datetime = timezone.datetime.combine(appointment.date, timezone.datetime.min.time())
    else:
        appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)

    appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

    # Get the current time
    current_time = now()
    

    # Check if the current time is earlier than 5 minutes before the scheduled time
    threshold_time = appointment_datetime - timedelta(minutes=5)  # Set threshold to 5 minutes before appointment

    if current_time < threshold_time:
        # Format threshold_time in 12-hour format with AM/PM
        wait_until_time = threshold_time.strftime("%I:%M %p")  # Example: "08:35 PM"
        error_message = f"Wait until {wait_until_time} to open the meeting."
        return render(request, 'frontend/error.html', {'error': error_message})


    # Pass necessary data to the frontend
    context = {
        'appointment_id': appointment.id,
        'appointment': appointment,
        'user_name': request.user.username,  # Example: pass logged-in user's name
        'room_id': appointment.id,
        'meeting_close_time': meeting_end_time.strftime("%Y-%m-%dT%H:%M:%S")  # Format for JavaScript
        # Add more context as needed
    }
    return render(request, 'frontend/video.html', context)






from django.middleware.csrf import get_token

def get_csrf_token(request):
    """
    API endpoint to return the CSRF token.
    """
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

    







@csrf_exempt  # Disable CSRF protection for simplicity (not recommended in production)
def create_callback(request):
    if request.method == 'POST':
        # Extract data from the POST request
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        date = request.POST.get('date')
        time = request.POST.get('time')

        # Validate required fields
        if not all([name, email, phone_number, date, time]):
            return HttpResponseBadRequest("All fields are required.")

        # Validate and parse the date field
        parsed_date = parse_datetime(date)
        if not parsed_date:
            return HttpResponseBadRequest("Invalid date format. Use YYYY-MM-DDTHH:MM:SS format.")

        # Create and save the CallBack instance
        callback = CallBack(
            name=name,
            email=email,
            phone_number=phone_number,
            date=parsed_date,
            time=time
        )
        callback.save()


        Notification.objects.create(
            message=f"{callback.name} Requested for a Call Back",
            read_status=False,
            redirection_url=reverse('call_back', args=[callback.id]),
            object_id = callback.id,
            type='callback'
        )

        print("Hello")

        # Return a JSON response
        return JsonResponse({"message": "CallBack created successfully.", "id": callback.id})

    return HttpResponseBadRequest("Invalid request method. Only POST is allowed.")
