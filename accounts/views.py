'''
File: views.py
Author: Beveridge Ekpolomo
Description: View functions for user authentication and profile management.
Part of the User Authentication & Profiles module for the University Dashboard application.
Adapted from Sky Health Check project.
'''

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm, UserPasswordChangeForm
from teams.models import Team
from health_checks.models import HealthCheckSession
from django.utils import timezone


def user_logout(request):
    """Custom logout function that doesn't require CSRF token for testing"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def user_login(request):
    """Handle user login with secure redirection"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                # Get the 'next' parameter or default to dashboard
                next_url = request.GET.get('next', 'dashboard')
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form, 'title': 'Login'})


def register(request):
    """Handle user registration with validation and secure redirection"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in with your new account.')
            return redirect('login')
        else:
            # Form errors will be displayed on the template
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'title': 'Register'})


@login_required
def dashboard(request):
    """User dashboard showing teams and health checks"""
    user = request.user
    
    # For admins and senior managers, show all teams
    if user.is_admin() or user.is_senior_manager():
        teams = Team.objects.all()
    # For department leaders, show teams in their department
    elif user.is_department_leader() and user.department:
        teams = Team.objects.filter(department=user.department)
    # Otherwise, show teams the user belongs to
    else:
        teams = user.teams.all()
    
    # Get active health check sessions (either for all teams or just user's teams)
    now = timezone.now()
    active_sessions_query = HealthCheckSession.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    )
    
    if not (user.is_admin() or user.is_senior_manager()):
        active_sessions_query = active_sessions_query.filter(team__in=teams)
    
    active_sessions = active_sessions_query.distinct()
    
    # Get recent sessions (for all accessible teams)
    recent_sessions_query = HealthCheckSession.objects.all()
    
    if not (user.is_admin() or user.is_senior_manager()):
        recent_sessions_query = recent_sessions_query.filter(team__in=teams)
    
    recent_sessions = recent_sessions_query.order_by('-start_date')[:5]
    
    # Get teams led by user
    teams_led = Team.objects.filter(team_memberships__user=user, team_memberships__is_leader=True)
    
    context = {
        'teams': teams,
        'active_sessions': active_sessions,
        'recent_sessions': recent_sessions,
        'teams_led': teams_led,
        'now': now
    }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile(request):
    """Display user profile with comprehensive information"""
    # Get additional user-related data that might be useful in the profile view
    teams = Team.objects.filter(team_memberships__user=request.user)
    # Check if user is a team leader
    is_team_leader = Team.objects.filter(team_memberships__user=request.user, team_memberships__is_leader=True).exists()
    
    context = {
        'user': request.user,
        'teams': teams,
        'is_team_leader': is_team_leader,
        'title': 'Profile'
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile with validation and error handling"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user, user=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form, 'title': 'Edit Profile'})


# Class-based views for password change, matching your Sky Health Check implementation
class UserPasswordChangeView(PasswordChangeView):
    """Custom password change view with improved template and success url"""
    template_name = 'accounts/change_password.html'
    success_url = '/password-change-done/'
    
    def form_valid(self, form):
        # Add success message before redirecting
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    """Custom password change done view with improved template"""
    template_name = 'accounts/password_change_done.html'


@login_required
def change_password(request):
    """Function-based view for password change (legacy support)"""
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important: prevent the user from being logged out after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully. Your login session has been maintained.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form, 'title': 'Change Password'})
