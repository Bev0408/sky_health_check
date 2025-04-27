from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import UserRegistrationForm

# Create your views here.

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

@login_required
def dashboard(request):
    """View for the user dashboard"""
    return render(request, 'health_app/dashboard.html')
