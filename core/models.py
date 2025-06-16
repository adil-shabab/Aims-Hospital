from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
import uuid
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django.utils.timezone import now
from datetime import timedelta
from .helpers import *


class Summary(models.Model):
    ROLE_CHOICES = [
        ('frontdesk', 'Front Desk'),
        ('hr', 'HR'),
        ('media', 'Media'),
        ('admin', 'Admin')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user.username} Profile'
    



class AdBanner(models.Model):
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='ad_banners/')
    mobile_image = models.ImageField(upload_to='ad_banners_mobile/', null=True, blank=True, default='static/images/placeholder.png')
    created_at = models.DateTimeField(auto_now_add=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='ad_banners', null=True, blank=True)
    button_text = models.CharField(max_length=100, default='Book Appointment', null=True, blank=True)
    button_url = models.URLField(null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='ad_banners', null=True, blank=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.department:
                # If department exists, create slug based on department title
                self.slug = slugify(f'{self.department.title}-ad')
            else:
                # If no department, use UUID for the slug
                self.slug = str(uuid.uuid4())

            original_slug = self.slug
            counter = 1
            while AdBanner.objects.filter(slug=self.slug).exists():
                if self.department:
                    self.slug = f'{original_slug}-{counter}'
                else:
                    self.slug = f'{uuid.uuid4()}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor.name if self.doctor else 'No Doctor'} - {self.department.title if self.department else 'No Department'} - {self.status}"

    @property
    def redirect_url(self):
        if self.doctor:
            return reverse('single_doctor', args=[self.doctor.slug])
        elif self.department:
            return f"{reverse('frontend_doctors')}?department={self.department.title}"
        elif self.button_url:
            return self.button_url
        else:
            return reverse('frontend_doctors')
     

class Banner(models.Model):
    COLOR_CHOICES = [
        ('black', 'black'),
        ('white', 'white'),
    ]
    heading = models.CharField(max_length=255, default='',  null=True, blank=True)
    description = models.TextField( null=True, blank=True, default='')
    button_text = models.CharField(max_length=100,  null=True, blank=True, default='')
    button_url = models.URLField(default='https://vshhospital.com/',  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_for_desktop = models.ImageField(upload_to='banners/desktop/')
    image_for_mobile = models.ImageField(upload_to='banners/mobile/')
    status = models.BooleanField(default=True)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='black')


    def __str__(self):
        return self.heading




class Department(models.Model):
    SPECIALITY_CHOICES = [
        ('Clinical Services', 'Clinical Services'),
        ('Emergency & Critical Care', 'Emergency & Critical Care'),
        ('Super Speciality Services', 'Super Speciality Services'),
        ('Professions Allied to Medicine', 'Professions Allied to Medicine'),
        ('Laboratory Services', 'Laboratory Services'),
        ('Radiology Services', 'Radiology Services'),
        ('Other Diagnostic Services', 'Other Diagnostic Services'),
    ]

    h1 = models.CharField(null=True, blank=True, max_length=255)
    title = models.CharField(max_length=200)
    speciality_type = models.CharField(max_length=200, choices=SPECIALITY_CHOICES, null=True, blank=True)
    banner = models.FileField(upload_to='departments', null=True, blank=True)
    breadcamp = models.FileField(upload_to='dep-banner', default='static/images/default.png')
    opening_hours = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    description = RichTextField()
    show_on_homepage = models.BooleanField(default=False)  # Control homepage display

    meta_title = models.TextField(null=True, blank=True)
    meta_keyword = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)



    def __str__(self):
        return self.title

        



def validate_youtube_url(value):
    """
    Validates that the provided URL is a valid YouTube URL.
    """
    youtube_regex = re.compile(
        r'(https?://)?(www\.)?'
        r'(youtube\.com|youtu\.be)/(watch\?v=|embed/|v/|.+\?v=)?([A-Za-z0-9_-]{11})'
    )
    if not youtube_regex.match(value):
        raise ValidationError("Enter a valid YouTube URL.")

class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery Image - {self.id}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'
        
        

    
class Doctor(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    h1 = models.CharField(null=True, blank=True, max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField()
    priority = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    email = models.EmailField()
    number = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    education = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='doctors')
    slug = models.SlugField(unique=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = RichTextField()
    show_on_homepage = models.BooleanField(default=False)  # New field to control homepage display

    meta_title = models.TextField(null=True, blank=True)
    meta_keyword = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)





    def __str__(self):
        return self.name



    def get_absolute_url(self):
        return reverse('single_doctor', args=[self.slug])



class AvailableTime(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='available_times')
    day = models.CharField(max_length=9, choices=DAY_CHOICES)
    start_time = models.TimeField()
    slot = models.PositiveIntegerField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, default='active')
    remaining_slots = models.PositiveIntegerField(default=5)


    def __str__(self):
        return f'{self.doctor.name} - {self.day} {self.start_time} to {self.end_time}'

class MonthlyTiming(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()    
    status = models.CharField(max_length=10, default='active')
    end_time = models.TimeField()
    slot = models.PositiveIntegerField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='available_monthly_times')
    remaining_slots = models.PositiveIntegerField(default=5)


    def __str__(self):
        return f"{self.doctor.name} - {self.date} ({self.slot})"




class Blog(models.Model):
    image = models.ImageField(upload_to='blog_images/')
    category = models.CharField(max_length=50)
    createdAt = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=50)
    author_designation = models.CharField(max_length=50)
    content = RichTextField()
    status = models.BooleanField(default=True)
    tags = models.CharField(max_length=50, blank=True)  # Field to store tags
    slug = models.SlugField(unique=True, blank=True)
    heading = models.TextField()
    show_on_homepage = models.BooleanField(default=False)  # New field to control homepage display


    def get_absolute_url(self):
        return reverse('single_blog', args=[self.slug])


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.heading)
            original_slug = self.slug
            counter = 1
            while Blog.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)


    def __str__(self):
        return self.heading


    def get_tags(self):
        """Return the list of tags."""
        return self.tags.split(',') if self.tags else []




class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Message.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)



    def __str__(self):
        return self.name
    
    




class CallBack(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    date = models.DateTimeField()
    time = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name
    
    



class Career(models.Model):

    job_title = models.CharField(max_length=200)
    department = models.CharField(max_length=200, null=True, blank=True)
    experience = models.PositiveIntegerField(help_text="Years of experience required", null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    responsibilities = RichTextField(null=True, blank=True)
    skills = RichTextField(null=True, blank=True)
    job_summary = RichTextField(null=True, blank=True)
    qualifications = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.job_title)
            original_slug = self.slug
            counter = 1
            while Career.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)



    def __str__(self):
        return self.job_title


    def get_absolute_url(self):
        return reverse('single_career', args=[self.slug])



class CareerApplication(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=15)
    email = models.EmailField()
    cover_letter = models.TextField(blank=True, null=True)
    cv = models.FileField(upload_to='cvs/')
    created_at = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='career_application')
    slug = models.SlugField(unique=True, blank=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while CareerApplication.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)






class BlogComment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while BlogComment.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.name} on {self.blog.heading}"




class Leave(models.Model):
    date = models.DateField(default=timezone.now)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='leave_date')
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()

    def __str__(self):
        return f"{self.doctor} - {self.date}"






class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    disease = models.CharField(max_length=255, null=True, blank=True, default='')
    slug = models.SlugField(unique=True, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')  # Add gender field

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Patient.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Appointment(models.Model):

    created_at = models.DateTimeField(default=timezone.now)
    message = models.TextField(null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    selected_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True, null=True)

        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.patient.name}-{self.department.title}')
            original_slug = self.slug
            counter = 1
            while Appointment.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(Appointment, self).save(*args, **kwargs)

    def __str__(self):
        return f'Appointment of {self.patient.name} with {self.selected_doctor}'



    
    
class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    read_status = models.BooleanField(default=False)
    redirection_url = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=200, default='appointment')
    object_id = models.PositiveIntegerField(default=1)
    is_alarmed = models.BooleanField(default=False)  # New field
    first_read_by = models.ForeignKey(User, related_name='first_read_notifications', null=True, blank=True, on_delete=models.SET_NULL)  # New field


    def __str__(self):
        return self.message





class HealthCheckupPlan(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, default=10)
    slug = models.SlugField(unique=True)
    status = models.BooleanField(default=True)
    total_test_include = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='health_checkup_plans/', blank=True, null=True)
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.title}')
            original_slug = self.slug
            counter = 1
            while HealthCheckupPlan.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(HealthCheckupPlan, self).save(*args, **kwargs)

    def __str__(self):
        return self.title




class HealthCheckupBooking(models.Model):
    plan = models.ForeignKey(HealthCheckupPlan, on_delete=models.CASCADE, related_name='bookings')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='health_checkup_bookings')
    payment_id = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f"{self.patient.name} - {self.plan.title}"





    
    
    
    
    

class HeartDayCheckup(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discounted Price")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Original Price")
    updated_at = models.DateTimeField(auto_now=True) 

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.title}')
            original_slug = self.slug
            counter = 1
            while HeartDayCheckup.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(HeartDayCheckup, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class CheckupDescription(models.Model):
    heart_day_checkup = models.ForeignKey(HeartDayCheckup, related_name='descriptions', on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.description





class HeartDayCheckupBooking(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('PAY_AT_HOSPITAL', 'Pay at Hospital'),
        ('ONLINE_PAY_NOW', 'Online Pay Now')
    ]
    plan = models.ForeignKey(HeartDayCheckup, on_delete=models.CASCADE, related_name='heart_day_bookings')
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='health_checkup_bookings_heart_day')
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='PAY_AT_HOSPITAL')


    def __str__(self):
        return f"{self.patient.name} - {self.plan.title}"





class RazorpayPaymentDetails(models.Model):

    PAYMENT_FOR = (
        ('APPOINTMENT', 'APPOINTMENT'),
        ('CHECKUP', 'CHECKUP'),
        ('OFFER', 'OFFER'),
    )

    payment_id = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()  # Amount in paise
    currency = models.CharField(max_length=10, default='INR')
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='razorpay_payment_details', null=True, blank=True)
    payment_for = models.CharField(max_length=12, choices=PAYMENT_FOR, default='APPOINTMENT')
    booking = models.OneToOneField(HealthCheckupBooking, on_delete=models.CASCADE, related_name='razorpay_payment_details', null=True, blank=True)
    offer = models.OneToOneField(HeartDayCheckupBooking, on_delete=models.CASCADE, related_name='razorpay_payment_details_offer', null=True, blank=True)

    

    def __str__(self):
        return f'Payment {self.payment_id} for Appointment {self.payment_for}'
    
    
    

class DepartmentAppointment(models.Model):
    name = models.CharField(max_length=225)
    number = models.CharField(max_length=15)
    message = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=225, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name








class InternationalMessage(models.Model):
    name = models.CharField(max_length=225)
    number = models.CharField(max_length=15)
    message = models.TextField(blank=True, null=True)
    email = models.EmailField()
    passport =  models.FileField(upload_to='passport/')
    visa =  models.FileField(upload_to='visa/', null=True, blank=True)
    medical_documents =  models.FileField(upload_to='medical-documents/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name






class PatientProfile(models.Model):
    number = models.CharField(max_length=15)
    uuid = models.UUIDField(default=uuid.uuid4)



