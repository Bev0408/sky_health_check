from django import forms
from .models import Team, TeamMember
from departments.models import Department
from accounts.models import User


class TeamForm(forms.ModelForm):
    """Form for creating and editing teams"""
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    team_leader = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'})
    )
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'department']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        department_id = kwargs.pop('department_id', None)
        super().__init__(*args, **kwargs)
        
        # If editing an existing team, initialize with current members
        if self.instance.pk:
            self.fields['members'].initial = self.instance.members.all()
            leader = self.instance.get_leader()
            if leader:
                self.fields['team_leader'].initial = leader
            
            # Set the department field initial value
            self.fields['department'].initial = self.instance.department
            
        # If a department is preselected, filter users by department
        if department_id:
            self.fields['department'].initial = Department.objects.get(pk=department_id)
            self.fields['team_leader'].queryset = User.objects.filter(department_id=department_id)
            self.fields['members'].queryset = User.objects.filter(department_id=department_id)


class TeamMemberForm(forms.Form):
    """Form for adding members to a team"""
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="User",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_leader = forms.BooleanField(
        required=False,
        label="Set as team leader",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        
        if team:
            # Filter users by department and exclude existing members
            department_users = User.objects.filter(department=team.department)
            existing_members = team.members.all()
            available_users = department_users.exclude(pk__in=[member.pk for member in existing_members])
            
            self.fields['user'].queryset = available_users