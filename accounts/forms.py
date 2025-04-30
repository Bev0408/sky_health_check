'''
File: forms.py
Author: Beveridge Ekpolomo
Description: Contains form classes for user registration and profile management.
Part of the User Authentication & Profiles module for the University Dashboard application.
Adapted from Sky Health Check project.
'''

from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User
from departments.models import Department


class UserLoginForm(forms.Form):
    """Form for user login"""
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )


class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your email',
            'autocomplete': 'email'
        })
    )
    full_name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your full name',
            'autocomplete': 'name'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label="Department",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        label="Role",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'password1', 'password2', 'department', 'role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Choose a username',
                'autocomplete': 'username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override some UserCreationForm labels and widgets
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password'
        })
        
    def clean_email(self):
        """Validate that the email is not already in use"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )
    full_name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'name'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label="Department",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'department']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.email:
            # If the form is for an existing user, check if email is changed
            self.initial_email = user.email
    
    def clean_email(self):
        """Validate that the email is not already in use by another user"""
        email = self.cleaned_data.get('email')
        if hasattr(self, 'initial_email') and email == self.initial_email:
            # If email hasn't changed, skip this validation
            return email
            
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email


class UserPasswordChangeForm(PasswordChangeForm):
    """Form for changing user password"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })