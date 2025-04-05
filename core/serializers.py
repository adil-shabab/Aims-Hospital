
from rest_framework import serializers
from .models import *

class AvailableTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTime
        fields = '__all__'

class MonthlyTimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyTiming
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'name', 'slug']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'read_status', 'redirection_url']
        



class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ['user', 'role', 'created_at']

    user = serializers.CharField(source='user.username')  # To include the username in the response





class RazorpayPaymentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RazorpayPaymentDetails
        fields = ['payment_id', 'order_id', 'signature', 'amount', 'currency', 'payment_method', 'status', 'created_at', 'updated_at', 'appointment', 'payment_for', 'booking']





class InternationalMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternationalMessage
        fields = ['name', 'number', 'email', 'message', 'passport', 'visa', 'medical_documents']





class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'selected_doctor', 'patient', 'department',]






class DepartmentApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'title', 'speciality_type', 'icon', 'opening_hours', 'description']



class DoctorApiSerializer(serializers.ModelSerializer):
    department = DepartmentApiSerializer()  # Nested serializer for department details

    class Meta:
        model = Doctor
        fields = ['id', 'name', 'experience_years', 'email', 'number', 'gender', 'education', 'photo', 'description', 'department', 'area_of_expertise_description', 'education_description', 'experience_description', 'award_description']