from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department
from .forms import DepartmentForm
from django.db.models import Count


@login_required
def department_list(request):
    """Display list of all departments"""
    departments = Department.objects.annotate(
        team_count=Count('teams', distinct=True),
        user_count=Count('users', distinct=True)
    )
    
    return render(request, 'departments/department_list.html', {'departments': departments})


@login_required
def department_detail(request, pk):
    """Display details of a specific department"""
    department = get_object_or_404(Department, pk=pk)
    teams = department.teams.all()
    users = department.users.all()
    
    context = {
        'department': department,
        'teams': teams,
        'users': users
    }
    
    return render(request, 'departments/department_detail.html', context)


@login_required
def create_department(request):
    """Create a new department"""
    # Only admins and senior managers can create departments
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to create departments.')
        return redirect('department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Department "{department.name}" created successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'departments/department_form.html', {
        'form': form,
        'title': 'Create Department'
    })


@login_required
def edit_department(request, pk):
    """Edit an existing department"""
    department = get_object_or_404(Department, pk=pk)
    
    # Only admins and senior managers can edit departments
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to edit departments.')
        return redirect('department_detail', pk=department.pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Department "{department.name}" updated successfully.')
            return redirect('department_detail', pk=department.pk)
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'departments/department_form.html', {
        'form': form,
        'department': department,
        'title': 'Edit Department'
    })


@login_required
def delete_department(request, pk):
    """Delete a department"""
    department = get_object_or_404(Department, pk=pk)
    
    # Only admins can delete departments
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to delete departments.')
        return redirect('department_detail', pk=department.pk)
    
    if request.method == 'POST':
        # Check if department has teams
        if department.teams.exists():
            messages.error(request, 'Cannot delete department that contains teams. Move or delete the teams first.')
            return redirect('department_detail', pk=department.pk)
        
        # Check if department has users
        if department.users.exists():
            messages.error(request, 'Cannot delete department that has assigned users. Reassign users first.')
            return redirect('department_detail', pk=department.pk)
        
        department_name = department.name
        department.delete()
        messages.success(request, f'Department "{department_name}" deleted successfully.')
        return redirect('department_list')
    
    return render(request, 'departments/department_confirm_delete.html', {'department': department})
