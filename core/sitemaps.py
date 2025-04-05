from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Blog, Career, Doctor


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Blog.objects.all()

    def lastmod(self, obj):
        return obj.createdAt

class DoctorSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Doctor.objects.all()

    def lastmod(self, obj):
        return obj.created_at

class CareerSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Career.objects.all()

    def lastmod(self, obj):
        return obj.created_at



class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return [
            'homepage', 
            'about', 
            'services', 
            'gallery', 
            'frontend_blogs',
            'frontend_doctors', 
            'frontend_careers',
            'contact',
            'icu',
            'privacy',
            'terms',
            'international',
            'best_in_class',
            'international_visa',
            'assistance',
            'documentation_fly',
            'dedicated_patient',
            'assistance_treatment_plan',
            'airport',
            'legal',
            'health_checkups'
        ]

    def location(self, item):
        return reverse(item)