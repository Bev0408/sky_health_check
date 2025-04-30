from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Team, TeamMember
from .forms import TeamForm, TeamMemberForm
from accounts.models import User
from django.db.models import Count


@login_required
def team_list(request):
    """Display list of all teams"""
    # For admins and senior managers, show all teams
    if request.user.is_admin() or request.user.is_senior_manager():
        teams = Team.objects.all()
    # For department leaders, show teams in their department
    elif request.user.is_department_leader() and request.user.department:
        teams = Team.objects.filter(department=request.user.department)
    # For everyone else, show only teams they're members of
    else:
        teams = request.user.teams.all()
    
    # Annotate with member count
    teams = teams.annotate(member_count=Count('members'))
    
    return render(request, 'teams/team_list.html', {'teams': teams})


@login_required
def team_detail(request, pk):
    """Display details of a specific team"""
    team = get_object_or_404(Team, pk=pk)
    
    # Check if user has access to this team
    if not (request.user.is_admin() or 
            request.user.is_senior_manager() or
            (request.user.is_department_leader() and request.user.department == team.department) or
            team.members.filter(id=request.user.id).exists()):
        return HttpResponseForbidden("You don't have permission to view this team.")
    
    # Get team members with leader status
    team_members = TeamMember.objects.filter(team=team).select_related('user')
    
    # Get health check sessions for this team
    from health_checks.models import HealthCheckSession
    health_check_sessions = HealthCheckSession.objects.filter(team=team).order_by('-start_date')
    
    context = {
        'team': team,
        'team_members': team_members,
        'leader': team.get_leader(),
        'health_check_sessions': health_check_sessions
    }
    
    return render(request, 'teams/team_detail.html', context)


@login_required
def create_team(request):
    """Create a new team"""
    # Check permissions
    if not (request.user.is_admin() or 
            request.user.is_senior_manager() or 
            request.user.is_department_leader()):
        messages.error(request, 'You do not have permission to create teams.')
        return redirect('team_list')
    
    # If department leader, preselect their department
    department_id = None
    if request.user.is_department_leader() and request.user.department:
        department_id = request.user.department.id
    
    if request.method == 'POST':
        form = TeamForm(request.POST, department_id=department_id)
        if form.is_valid():
            team = form.save()
            
            # Add members
            for member in form.cleaned_data['members']:
                team.add_member(member)
            
            # Set leader if specified
            if form.cleaned_data['team_leader']:
                team.set_leader(form.cleaned_data['team_leader'])
            
            messages.success(request, f'Team "{team.name}" created successfully.')
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm(department_id=department_id)
    
    return render(request, 'teams/team_form.html', {
        'form': form,
        'title': 'Create Team'
    })


@login_required
def edit_team(request, pk):
    """Edit an existing team"""
    team = get_object_or_404(Team, pk=pk)
    
    # Check permissions
    if not (request.user.is_admin() or 
            request.user.is_senior_manager() or 
            (request.user.is_department_leader() and request.user.department == team.department) or
            (request.user.is_team_leader() and request.user == team.get_leader())):
        messages.error(request, 'You do not have permission to edit this team.')
        return redirect('team_detail', pk=team.pk)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            team = form.save()
            
            # Update team memberships
            current_members = set(team.members.all())
            new_members = set(form.cleaned_data['members'])
            
            # Remove members no longer in the team
            for member in current_members - new_members:
                team.remove_member(member)
            
            # Add new members
            for member in new_members - current_members:
                team.add_member(member)
            
            # Update team leader
            new_leader = form.cleaned_data['team_leader']
            if new_leader:
                team.set_leader(new_leader)
            
            messages.success(request, f'Team "{team.name}" updated successfully.')
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm(instance=team)
    
    return render(request, 'teams/team_form.html', {
        'form': form,
        'team': team,
        'title': 'Edit Team'
    })


@login_required
def delete_team(request, pk):
    """Delete a team"""
    team = get_object_or_404(Team, pk=pk)
    
    # Only admins, senior managers, and department leaders can delete teams
    if not (request.user.is_admin() or 
            request.user.is_senior_manager() or 
            (request.user.is_department_leader() and request.user.department == team.department)):
        messages.error(request, 'You do not have permission to delete this team.')
        return redirect('team_detail', pk=team.pk)
    
    if request.method == 'POST':
        team_name = team.name
        team.delete()
        messages.success(request, f'Team "{team_name}" deleted successfully.')
        return redirect('team_list')
    
    return render(request, 'teams/team_confirm_delete.html', {'team': team})


@login_required
def add_team_member(request, pk):
    """Add a member to a team"""
    team = get_object_or_404(Team, pk=pk)
    
    # Check permissions
    if not (request.user.is_admin() or 
            request.user.is_senior_manager() or 
            (request.user.is_department_leader() and request.user.department == team.department) or
            (request.user.is_team_leader() and request.user == team.get_leader())):
        messages.error(request, 'You do not have permission to add members to this team.')
        return redirect('team_detail', pk=team.pk)
    
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, team=team)
        if form.is_valid():
            user = form.cleaned_data['user']
            is_leader = form.cleaned_data['is_leader']
            
            # Add user to team
            team.add_member(user, is_leader)
            
            messages.success(request, f'{user.username} added to the team successfully.')
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamMemberForm(team=team)
    
    # If there are no available users, show a message
    if not form.fields['user'].queryset.exists():
        messages.warning(request, 'No available users to add to this team.')
        return redirect('team_detail', pk=team.pk)
    
    return render(request, 'teams/add_team_member.html', {
        'form': form,
        'team': team
    })


@login_required
def remove_team_member(request, team_pk, user_pk):
    """Remove a member from a team"""
    team = get_object_or_404(Team, pk=team_pk)
    user = get_object_or_404(User, pk=user_pk)
    
    # Check permissions
    if not (request.user.is_admin() or 
            request.user.is_senior_manager() or 
            (request.user.is_department_leader() and request.user.department == team.department) or
            (request.user.is_team_leader() and request.user == team.get_leader())):
        messages.error(request, 'You do not have permission to remove members from this team.')
        return redirect('team_detail', pk=team.pk)
    
    # Check if user is a member of the team
    if not team.members.filter(pk=user.pk).exists():
        messages.error(request, f'{user.username} is not a member of this team.')
        return redirect('team_detail', pk=team.pk)
    
    if request.method == 'POST':
        team.remove_member(user)
        messages.success(request, f'{user.username} removed from the team successfully.')
        return redirect('team_detail', pk=team.pk)
    
    return render(request, 'teams/remove_team_member.html', {
        'team': team,
        'user': user
    })


@login_required
def set_team_leader(request, team_pk, user_pk):
    """Set a user as team leader"""
    team = get_object_or_404(Team, pk=team_pk)
    user = get_object_or_404(User, pk=user_pk)
    
    # Check permissions
    if not (request.user.is_admin() or 
            request.user.is_senior_manager() or 
            (request.user.is_department_leader() and request.user.department == team.department)):
        messages.error(request, 'You do not have permission to set team leader.')
        return redirect('team_detail', pk=team.pk)
    
    # Check if user is a member of the team
    if not team.members.filter(pk=user.pk).exists():
        messages.error(request, f'{user.username} is not a member of this team.')
        return redirect('team_detail', pk=team.pk)
    
    if request.method == 'POST':
        team.set_leader(user)
        messages.success(request, f'{user.username} set as team leader successfully.')
        return redirect('team_detail', pk=team.pk)
    
    return render(request, 'teams/set_team_leader.html', {
        'team': team,
        'user': user
    })
