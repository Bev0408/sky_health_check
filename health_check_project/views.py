from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

def index(request):
    """Homepage view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')