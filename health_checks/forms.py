from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import (
    HealthCheckCategory,
    HealthCheckQuestion,
    HealthCheck, 
    HealthCheckSession,
    HealthCheckResponse
)
from teams.models import Team
from accounts.models import User


class HealthCheckCategoryForm(forms.ModelForm):
    """Form for creating and editing health check categories"""
    class Meta:
        model = HealthCheckCategory
        fields = ['name', 'description', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class HealthCheckQuestionForm(forms.ModelForm):
    """Form for creating and editing health check questions"""
    class Meta:
        model = HealthCheckQuestion
        fields = ['text', 'detail', 'category', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class HealthCheckForm(forms.ModelForm):
    """Form for creating and editing health checks"""
    class Meta:
        model = HealthCheck
        fields = ['name', 'description', 'is_template']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_template': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HealthCheckSessionForm(forms.ModelForm):
    """Form for creating health check sessions"""
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    health_check = forms.ModelChoiceField(
        queryset=HealthCheck.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
        required=False
    )
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        initial=timezone.now
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        initial=lambda: timezone.now() + timedelta(days=7)
    )
    
    class Meta:
        model = HealthCheckSession
        fields = ['team', 'health_check', 'start_date', 'end_date', 'anonymous', 'participants']
        widgets = {
            'anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter teams based on user's role
            if user.is_admin() or user.is_senior_manager():
                # Admins and senior managers can see all teams
                pass
            elif user.is_department_leader() and user.department:
                # Department leaders can only see teams in their department
                self.fields['team'].queryset = Team.objects.filter(department=user.department)
            else:
                # Other users can only see teams they lead
                self.fields['team'].queryset = Team.objects.filter(
                    team_memberships__user=user,
                    team_memberships__is_leader=True
                )
        
        # If instance exists, update participants field
        if self.instance.pk:
            self.fields['participants'].initial = self.instance.participants.all()
            
            # If team is already selected, filter participants
            if self.instance.team:
                self.fields['participants'].queryset = self.instance.team.members.all()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        team = cleaned_data.get('team')
        participants = cleaned_data.get('participants')
        
        # Validate date range
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        # If team is selected but no participants, use all team members
        if team and not participants:
            cleaned_data['participants'] = team.members.all()
        
        return cleaned_data


class HealthCheckResponseForm(forms.ModelForm):
    """Form for submitting health check responses"""
    
    class Meta:
        model = HealthCheckResponse
        fields = ['question', 'status', 'comment']
        widgets = {
            'question': forms.HiddenInput(),
            'status': forms.Select(attrs={'class': 'form-select status-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional comment'}),
        }


HealthCheckResponseFormSet = forms.modelformset_factory(
    HealthCheckResponse,
    form=HealthCheckResponseForm,
    extra=0
)