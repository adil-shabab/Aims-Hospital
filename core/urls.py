from django.urls import path
from .import views
from .views import *
from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap
from .sitemaps import BlogSitemap, StaticViewSitemap, DoctorSitemap, CareerSitemap
from .views import create_timing_api


sitemaps = {
    'static': StaticViewSitemap,
    'blogs': BlogSitemap,
    'doctors': DoctorSitemap,
    'careers': CareerSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),


    path('', views.homepage, name='homepage'), 
    path('healthy-2025/', views.healthy_2025, name='healthy_2025'), 
    path('pulse-of-life/', views.heart_day, name='heart_day'), 
    path('acl-surgery-treatment-bangalore/', views.acl, name='acl'), 
    path('acl-surgery-treatment-bangalore/success/', views.acl_payment_success, name='acl_payment_success'), 
    path('kidney-stone-and-bph-screening-package-bangalore/', views.urology, name='urology'), 
    path('best-health-checkup-in-bangalore/', views.heart_day_seo, name='heart_day_seo'), 
    path('about-us/', views.about, name='about'), 
    path('our-departments/', views.services, name='services'), 
    path('services/', views.services, name='services'), 
    path('super-specialities/', views.services, name='services'), 
    path('services/<slug:slug>/', views.single_service, name='single_service'), 
    path('blogs/', views.frontend_blogs, name='frontend_blogs'), 
    path('autism/', views.autism, name='autism'), 
    path('create_callback/', views.create_callback, name='create_callback'), 

    path('gallery/', views.gallery_frontend, name='gallery_frontend'), 
    path('insurance/', views.insurance, name='insurance'), 
    path('patient-rights-responsibilities/', views.patient, name='patient'), 
    path('patient-feedback-system/', views.patient_feedback, name='patient_feedback'), 
    path('special-services/', views.facilities, name='facilities'), 
    
    path('blogs/<slug:slug>/', views.single_blog, name='single_blog'), 
    path('doctors/', views.frontend_doctors, name='frontend_doctors'), 
    path('career/', views.frontend_careers, name='frontend_careers'), 
    path('career/<slug:slug>/', views.single_career, name='single_career'), 
    path('doctors/<slug:slug>/', views.single_doctor, name='single_doctor'), 
    path('doctors/backup/<slug:slug>/', views.single_doctor_backup, name='single_doctor_backup'), 
    path('contact-us/', views.contact, name='contact'), 
    path('contact/', views.contact, name='contact'), 
    path('intensive-care-unit/', views.icu, name='icu'), 
    path('privacy-policy/', views.privacy, name='privacy'), 
    path('terms-condition/', views.terms, name='terms'), 
    path('international-patient/', views.international, name='international'), 
    path('best-in-class-consultants/', views.best_in_class, name='best_in_class'), 
    path('information-on-medical-visa/', views.international_visa, name='international_visa'), 
    path('assistance-on-accommodation/', views.assistance, name='assistance'), 
    path('documentation-for-fit-to-fly/', views.documentation_fly, name='documentation_fly'), 
    path('dedicated-patient-coordinators-and-atient-assistance/', views.dedicated_patient, name='dedicated_patient'), 
    path('assistance-with-consultant-opinion-and-treatment-plan/', views.assistance_treatment_plan, name='assistance_treatment_plan'), 
    path('complimentary-airport-pickup-and-drop-facility-for-patient-coming-to-vsh/', views.airport, name='airport'), 
    path('assistance-with-medical-visa-invitation-letter/', views.legal, name='legal'),
    path('health-checkups/', views.health_checkups, name='frontend_health_checkups'),
    path('view-appointment/', views.view_user_appointment, name='view_user_appointment'),
    path('online-consultation/', views.online_consultation, name='online_consultation'),
    path('online-consultation/<str:pk>/', views.open_video_call, name='open_video_call'),
    path("send-otp/", send_otp_view, name="send_otp"),
    path("verify-otp/", verify_otp_view, name="verify_otp"),
    path('check-new-appointments/', views.check_new_appointments, name='check_new_appointments'),
    path('update-alarm-status/', views.update_alarm_status, name='update_alarm_status'),  # New URL



    path('account/', views.dashboard, name='dashboard'), 
    path('account/banners/', views.banners, name='banners'), 
    path('account/banners/create/', views.create_banner, name='create_banner'), 
    path('account/banners/update/<str:pk>/', views.update_banner, name='update_banner'), 
    path('account/banners/delete/<str:pk>/', views.delete_banner, name='delete_banner'), 

    path('account/departments/', views.departments, name='departments'), 
    path('account/departments/create/', views.create_department, name='create_department'), 
    path('account/departments/update/<slug:slug>/', views.update_department, name='update_department'), 
    path('account/departments/delete/<slug:slug>/', views.delete_department, name='delete_department'), 


    path('account/second-banner/', views.ad_banners, name='ad_banners'), 
    path('account/second-banner/create/', views.create_adbanner, name='create_adbanner'), 
    path('account/second-banner/update/<slug:slug>/', views.update_adbanner, name='update_adbanner'), 
    path('account/second-banner/delete/<slug:slug>/', views.delete_adbanner, name='delete_adbanner'), 


    path('account/campaign/appointments/', views.campaign_appointments, name='campaign_appointments'), 
    path('account/campaign/appointments/<str:pk>', views.campaign_appointments_view, name='campaign_appointments_view'), 

    path('account/health-checkup/', views.health_checkup_plans, name='health_checkup_plans'), 
    path('account/health-checkup/create/', views.create_health_checkup_plans, name='create_health_checkup_plans'), 
    path('account/health-checkup/update/<slug:slug>/', views.update_health_checkup_plans, name='update_health_checkup_plans'), 
    path('account/health-checkup/appointments/<slug:slug>/', views.health_checkup_appointments, name='health_checkup_appointments'), 
    path('account/health-checkup/delete/<slug:slug>/', views.delete_health_checkup_plan, name='delete_health_checkup_plan'), 
    path('account/health-checkup/appointment/<str:pk>/', views.view_checkup_appointment, name='view_checkup_appointment'), 


    path('account/heart-day/health-checkup/', views.heart_day_health_checkup_plans, name='heart_day_health_checkup_plans'), 
    path('account/heart-day/health-checkup/create/', views.heart_day_create_health_checkup_plans, name='heart_day_create_health_checkup_plans'), 
    path('account/heart-day/health-checkup/update/<str:pk>/', views.heart_day_update_health_checkup_plans, name='heart_day_update_health_checkup_plans'), 
    path('account/heart-day/health-checkup/appointments/<slug:slug>/', views.heart_day_health_checkup_appointments, name='heart_day_health_checkup_appointments'), 
    path('account/heart-day/health-checkup/delete/<str:pk>/', views.heart_day_delete_health_checkup_plan, name='heart_day_delete_health_checkup_plan'), 
    path('account/heart-day/health-checkup/appointment/<str:pk>/', views.heart_day_view_checkup_appointment, name='heart_day_view_checkup_appointment'), 
    path('account/heart-day/change-payment-status/<str:pk>/', views.change_payment_status, name='change_payment_status'), 

    path('api/heart-day/create-health-checkup-booking/', CreateHeartHealthCheckupBookingAPIView.as_view(), name='create_health_checkup_booking_heart'),
    path('api/heart-day/handle-health-checkup-payment/', views.handle_health_checkup_payment, name='handle_health_checkup_payment'),
    path('heart-day/health-checkup/payment-success/<int:booking_id>/', views.heart_health_checkup_payment_success, name='heart_health_checkup_payment_success'),
    path('heart-day/health-checkup/payment-failure/', views.heart_health_checkup_payment_failure, name='heart_health_checkup_payment_failure'),



    path('account/gallery/create/', views.create_gallery, name='create_gallery'),
    path('account/gallery/link/create/', views.create_gallery_link, name='create_gallery_link'),
    path('account/gallery/delete/<int:gallery_id>/', views.delete_gallery, name='delete_gallery'),
    path('account/gallery/', views.gallery_list, name='gallery_list'),  \


    path('account/doctors/', views.doctors, name='doctors'), 
    path('account/doctors/create/', views.create_doctor, name='create_doctor'), 
    path('account/doctors/update/<slug:slug>/', views.update_doctor, name='update_doctor'), 
    path('account/doctors/delete/<slug:slug>/', views.delete_doctor, name='delete_doctor'), 

    path('account/doctors/<int:doctor_id>/appointments/', views.doctor_appointments, name='doctor_appointments'),

    path('account/timing/<slug:slug>/', views.create_timing, name='create_timing'), 
    path('account/timing/delete/<str:pk>/', views.delete_timing, name='delete_timing'), 
    path('account/timing/delete/monthly/<str:pk>/', views.delete_timing_monthly, name='delete_timing_monthly'), 
    path('account/timing/monthly/create/<str:pk>/', views.create_monthly_timing, name='create_monthly_timing'), 
    path('account/leave/<slug:slug>/', views.create_leave, name='create_leave'), 
    path('account/leave/delete/<str:pk>/', views.delete_leave, name='delete_leave'), 

    
    
    path('account/blogs/', views.blogs, name='blogs'),
    path('account/blogs/create/', views.create_blog, name='create_blog'),
    path('account/blogs/update/<slug:slug>/', views.update_blog, name='update_blog'),
    path('account/blogs/delete/<str:pk>/', views.delete_blog, name='delete_blog'),
    path('account/blogs/<slug:slug>/', views.view_blog_comments, name='view_blog_comments'),
    path('account/blogs/<slug:blogSlug>/comments/<slug:commentSlug>/', views.view_blog_comment, name='view_blog_comment'),


    path('account/messages/', views.messages, name='messages'), 
    path('account/messages/<slug:slug>/', views.message, name='message'), 
    path('account/callbacks/', views.call_backs, name='call_backs'), 
    path('account/callback/<str:pk>/', views.call_back, name='call_back'), 


    path('account/careers/', views.careers, name='careers'), 
    path('account/careers/create/', views.create_career, name='create_career'), 
    path('account/careers/update/<slug:slug>/', views.update_career, name='update_career'), 
    path('account/careers/delete/<str:pk>/', views.delete_career, name='delete_career'), 
    path('account/careers/<slug:slug>/', views.view_career_applications, name='view_career_applications'), 
    path('account/careers/<slug:careerslug>/application/<slug:applicationslug>/', views.view_career_application, name='view_career_application'),

    path('account/international/application/<str:pk>/', views.view_international_application, name='view_international_application'), 
    path('account/international/application/', views.view_international_applications, name='view_international_applications'), 
    
    path('account/login/', views.login, name='login'), 
    path('account/logout/', views.logout_user, name='logout_user'), 

    path('account/appointments/', views.appointments, name='appointments'), 
    path('account/appointments/add/', views.create_appointment_backend, name='create_appointment_backend'), 
    path('account/appointments/<str:pk>/details/', views.view_appointment, name='view_appointment'),
    path('api/doctors/department/', DoctorsByDepartmentAPIView.as_view(), name='doctors-by-department'),

    path('api/create-timing/<slug:doctor_slug>/', create_timing_api, name='create_timing_api'),

    path('account/appointments/cancel/<str:pk>/', views.cancel_appointment, name='cancel_appointment'), 
    
    path('appointments/add/', views.create_appointement_page, name='create_appointement_page'), 
    path('api/create-appointment/', CreateAppointmentAPIView.as_view(), name='create_appointment_api'),
    path('api/video/create-appointment/', CreateAppointmentVideoAPIView.as_view(), name='create_appointment_api_video'),
    path('api/handle-payment/', HandlePaymentAPIView.as_view(), name='handle_payment_api'),
    path('handle-payment/', views.handle_payment, name='handle_payment'),
    path('collect-cash-appointment/<str:pk>/', views.collect_cash_appointment, name='collect_cash_appointment'),



    path('api/check-timings/<int:doctor_id>/<str:date>/', views.check_available_timings, name='check-available-timings'),

    path('account/payments/', PaymentListView.as_view(), name='payments'),

    
    path('account/patients/', views.patients, name='patients'), 
    path('account/patients/<int:patient_id>/appointments/', views.patient_appointments, name='patient_appointments'),
    path('account/patients/<int:patient_id>/appointments/create/', views.patient_appointments_create, name='patient_appointments_create'),
    path('api/create-appointment/patient/', CreateAppointmentPatientAPIView.as_view(), name='create_appointment_patient'),


    path('account/patients/add/', views.create_patient, name='create_patient'), 
    path('account/patients/update/<str:pk>/', views.update_patient, name='update_patient'), 



    path('api/notifications/unread/', UnreadNotificationsView.as_view(), name='unread-notifications'),
    path('api/notifications/mark-read/<int:notification_id>/', MarkNotificationAsReadView.as_view(), name='mark-notification-as-read'),
    path('api/notifications/mark-all-read/', MarkAllNotificationsAsReadView.as_view(), name='mark-all-notifications-as-read'),

    path('account/notifications/', views.notifications, name='notifications'), 


    path('account/health-checkup/', views.health_checkups, name='health_checkups'), 
    path('api/create-health-checkup-booking/', CreateHealthCheckupBookingAPIView.as_view(), name='create_health_checkup_booking'),
    path('api/handle-health-checkup-payment/', views.handle_health_checkup_payment, name='handle_health_checkup_payment'),
    path('health-checkup/payment-success/<int:booking_id>/', views.health_checkup_payment_success, name='health_checkup_payment_success'),
    path('health-checkup/payment-failure/', views.health_checkup_payment_failure, name='health_checkup_payment_failure'),

    path('account/success/payment/<int:appointment_id>/', views.payment_success_account, name='payment_success_account'),
    path('appointment/success/payment/<int:appointment_id>/', views.payment_success_pay_at_hospital, name='payment_success_pay_at_hospital'),
    path('account/failure/payment/', views.payment_failure_account, name='payment_failure_account'),

    path('update-appointment-status/', views.update_appointment_status, name='update_appointment_status'),
    path('update-appointment-status-api/', views.update_appointment_status_api, name='update_appointment_status_api'),
    path('update-health-checkup-status/', views.update_checkup_status, name='update_checkup_status'),
    path('update-heart-day-health-checkup-status/', views.update_heart_day_checkup_status, name='update_heart_day_checkup_status'),

    path('api/international/patient/message/', InternationalMessageCreateAPIView.as_view(), name='api_create_message'),

    path('api/payment-details/<str:order_id>/', GetPaymentDetailsByOrderId.as_view(), name='get_payment_details_by_order_id'),




]