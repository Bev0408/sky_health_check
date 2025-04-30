"""
URL configuration for health_check_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Set admin site header, title and index title
admin.site.site_header = 'Health Check Administration'
admin.site.site_title = 'Health Check Admin Portal'
admin.site.index_title = 'Welcome to Health Check Portal'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('departments/', include('departments.urls')),
    path('teams/', include('teams.urls')),
    path('health-checks/', include('health_checks.urls'), name='health_checks'),
    path('analytics/', include('analytics.urls')),
    
    # Root URL to index view
    path('', views.index, name='index'),
]

# Add static file serving during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
