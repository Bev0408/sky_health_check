'''
File: urls.py
Author: Beveridge Ekpolomo
Description: URL routes for user authentication and profile management.
Part of the User Authentication & Profiles module for the University Dashboard application.
Adapted from Sky Health Check project.
'''

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # Profile management
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Password management - function-based view (legacy support)
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Password management - class-based views (improved implementation)
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/', views.UserPasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # User dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]