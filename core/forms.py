# forms.py

from django import forms
from .models import *
from ckeditor.widgets import CKEditorWidget


STATUS_CHOICES = [
    (True, 'Active'),
    (False, 'Inactive')
]

class BannerForm(forms.ModelForm):

    class Meta:
        model = Banner
        fields = [
            'heading',
            'description',
            'button_text',
            'button_url',
            'image_for_desktop',
            'image_for_mobile',
            'status',
            'color'
        ]
        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES),
            'image_for_desktop': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
            'image_for_mobile': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL2(this)",
                "accept": "image/*"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['heading'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control description_class'
        self.fields['button_text'].widget.attrs['class'] = 'form-control'
        self.fields['color'].widget.attrs['class'] = 'form-control'
        self.fields['button_url'].widget.attrs['class'] = 'form-control'





class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['image']

        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
   
        }





class AdBannerForm(forms.ModelForm):
    
    class Meta:
        model = AdBanner
        fields = ['department', 'doctor', 'image', 'status', 'button_url', 'button_text', 'mobile_image']

        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES, attrs={
                'class': 'select'
                }),
            'image': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
            'mobile_image': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL2(this)",
                "accept": "image/*"
            }),

            
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].widget.attrs['class'] = 'form-control'
        self.fields['doctor'].widget.attrs['class'] = 'form-control'
        self.fields['button_text'].widget.attrs['class'] = 'form-control'
        self.fields['button_url'].widget.attrs['class'] = 'form-control'





class DepartmentForm(forms.ModelForm):
    
    description = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Department
        fields = ['title', 'breadcamp', 'icon', 'show_on_homepage', 'speciality_type', 'banner', 'opening_hours', 'description', 'status', 'meta_description', 'meta_keyword','meta_title', 'slug']

        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES, attrs={
                'class': 'select'
                }),
            'banner': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
            'opening_hours': forms.TextInput(attrs={
                'placeholder': 'Eg: 8:00 AM to 5:00 PM'
            }),
            'breadcamp': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL2(this)",
                "accept": "image/*"
            }),
            'icon': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL3(this)",
                "accept": "image/*"
            }),
            
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['speciality_type'].widget.attrs['class'] = 'form-control'
        self.fields['opening_hours'].widget.attrs['class'] = 'form-control'
        self.fields['show_on_homepage'].widget.attrs['class'] = 'form-check-input'  # Added this line
        self.fields['meta_title'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['meta_keyword'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['meta_description'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['slug'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['slug'].required = True






class CheckupForm(forms.ModelForm):
    
    class Meta:
        model = HealthCheckupPlan
        fields = ['title', 'price', 'image', 'total_test_include', 'priority', 'description', 'status']

        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES, attrs={
                'class': 'select'
                }),
            'image': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
            'price': forms.TextInput(attrs={
                'placeholder': '₹'
            })
            
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['price'].widget.attrs['class'] = 'form-control'
        self.fields['total_test_include'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['priority'].widget.attrs['class'] = 'form-control'





class DoctorForm(forms.ModelForm):

    class Meta:
        model = Doctor
        fields = [
            'name', 'department', 'priority', 'designation', 'experience_years', 'email', 'number', 'gender',
            'education', 'city', 'photo', 'status', 'show_on_homepage',  'description', 'meta_description', 'meta_keyword', 'meta_title', 'slug'
        ]
        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES),
            'photo': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['department'].widget.attrs['class'] = 'form-control'
        self.fields['designation'].widget.attrs['class'] = 'form-control'
        self.fields['experience_years'].widget.attrs['class'] = 'form-control'
        self.fields['priority'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['number'].widget.attrs['class'] = 'form-control'
        self.fields['gender'].widget.attrs['class'] = 'form-control'
        self.fields['education'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['show_on_homepage'].widget.attrs['class'] = 'form-check-input'  # Added this line
        self.fields['meta_title'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['meta_keyword'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['meta_description'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['slug'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['slug'].required = True


class AvailableTimeForm(forms.ModelForm):
    class Meta:
        model = AvailableTime
        fields = ['day', 'start_time', 'end_time', 'slot']



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['day'].widget.attrs['class'] = 'form-control'
        self.fields['start_time'].widget.attrs['class'] = 'form-control'
        self.fields['end_time'].widget.attrs['class'] = 'form-control'
        self.fields['slot'].widget.attrs['class'] = 'form-control'



class MonthlyTimeForm(forms.ModelForm):
    class Meta:
        model = MonthlyTiming
        fields = ['date', 'start_time', 'end_time', 'slot']



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['start_time'].widget.attrs['class'] = 'form-control'
        self.fields['end_time'].widget.attrs['class'] = 'form-control'
        self.fields['slot'].widget.attrs['class'] = 'form-control'



class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['heading', 'slug', 'show_on_homepage', 'image', 'category', 'author', 'content', 'status', 'tags', 'author_designation']
        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES),
            'image': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['heading'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['author_designation'].widget.attrs['class'] = 'form-control'
        self.fields['author'].widget.attrs['class'] = 'form-control'
        self.fields['content'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['show_on_homepage'].widget.attrs['class'] = 'form-check-input'  # Added this line




        
    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        tags = tags.replace(' ', '')  # Remove any spaces around commas
        return tags



class CareerForm(forms.ModelForm):
    responsibilities = forms.CharField(widget=CKEditorWidget())
    skills = forms.CharField(widget=CKEditorWidget())
    job_summary = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Career
        fields = [
            'job_title', 'department', 'experience', 'salary',
            'responsibilities', 'skills', 'job_summary', 
            'qualifications', 'status'
        ]

        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES),
        }



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['job_title'].widget.attrs['class'] = 'form-control'
        self.fields['department'].widget.attrs['class'] = 'form-control'
        self.fields['experience'].widget.attrs['class'] = 'form-control'
        self.fields['salary'].widget.attrs['class'] = 'form-control'
        self.fields['qualifications'].widget.attrs['class'] = 'form-control'




class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['date', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['reason'].widget.attrs['class'] = 'form-control'



class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'email', 'phone_number', 'disease', 'gender']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['phone_number'].widget.attrs['class'] = 'form-control'
        self.fields['disease'].widget.attrs['class'] = 'form-control'
        self.fields['gender'].widget.attrs['class'] = 'form-control'


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['name', 'email', 'phone_number', 'content']



class DepartmentAppointmentForm(forms.ModelForm):
    class Meta:
        model = DepartmentAppointment
        fields = ['name', 'number', 'message', 'department']









class InternationalMessageForm(forms.ModelForm):
    class Meta:
        model = InternationalMessage
        fields = ['name', 'number', 'email', 'message', 'passport', 'visa', 'medical_documents']


        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['number'].widget.attrs['class'] = 'form-control'
        self.fields['message'].widget.attrs['class'] = 'form-control'

