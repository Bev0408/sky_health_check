from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.forms import PasswordChangeForm

from .forms import UserRegistrationForm, UserProfileUpdateForm
from .models import HealthCard, Session, Vote, Team, Profile  # ← added here

# Create your views here.

def home(request):
    """Home view that redirects to dashboard if authenticated or login if not"""
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return redirect('/login/')

def test_page(request):
    """A simple test page to verify routing is working"""
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Test Page Works!</h1>
        <p>If you can see this, your Django server is running correctly.</p>
        <p>Try these links:</p>
        <ul>
            <li><a href='/login/'>Login Page</a></li>
            <li><a href='/register/'>Registration Page</a></li>
        </ul>
    </body>
    </html>"""
    return HttpResponse(html)

def register(request):
    """View for user registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'health_app/register.html', {'form': form})

@login_required(login_url='login')
def dashboard(request):
    """View for the user dashboard"""
    return render(request, 'health_app/dashboard.html')

@login_required(login_url='login')
def profile_view(request):
    """View user profile information"""
    return render(request, 'health_app/profile.html')

@login_required(login_url='login')
def profile_edit_view(request):
    """Edit user profile information"""
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    return render(request, 'health_app/profile_edit.html', {'form': form})

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'health_app/password_change_form.html'
    success_url = '/password-change-done/'

class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'health_app/password_change_done.html'

# ------------------------------------------
# ✅ Engineer Voting View - Your Feature
# ------------------------------------------
@login_required(login_url='login')
def engineer_vote_view(request):
    # Allow only engineers
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ENG':
        return redirect('dashboard')

    cards = HealthCard.objects.all()
    sessions = Session.objects.filter(is_active=True)
    team = request.user.profile.team

    if request.method == 'POST':
        session_id = request.POST.get('session')
        session = Session.objects.get(id=session_id)

        for card in cards:
            vote_value = request.POST.get(f'vote_{card.id}')
            progress_opinion = request.POST.get(f'progress_{card.id}')
            if vote_value:
                Vote.objects.update_or_create(
                    user=request.user,
                    card=card,
                    session=session,
                    defaults={
                        'vote_value': vote_value,
                        'progress_opinion': progress_opinion,
                    }
                )
        messages.success(request, "Your votes have been submitted.")
        return redirect('dashboard')

    return render(request, 'health_app/vote.html', {
        'cards': cards,
        'sessions': sessions,
        'team': team,
    })
