from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.forms import formset_factory

from .models import (
    HealthCheckCategory,
    HealthCheckQuestion,
    HealthCheck,
    HealthCheckSession,
    HealthCheckResponse
)
from teams.models import Team
from .forms import (
    HealthCheckCategoryForm,
    HealthCheckQuestionForm,
    HealthCheckForm,
    HealthCheckSessionForm,
    HealthCheckResponseForm,
    HealthCheckResponseFormSet
)


# Health Check Views
@login_required
def health_check_list(request):
    """List all health checks"""
    health_checks = HealthCheck.objects.all()
    return render(request, 'health_checks/health_check_list.html', {'health_checks': health_checks})


@login_required
def health_check_detail(request, pk):
    """Show details of a health check"""
    health_check = get_object_or_404(HealthCheck, pk=pk)
    return render(request, 'health_checks/health_check_detail.html', {'health_check': health_check})


@login_required
def create_health_check(request):
    """Create a new health check"""
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to create health checks.')
        return redirect('health_check_list')
        
    if request.method == 'POST':
        form = HealthCheckForm(request.POST)
        if form.is_valid():
            health_check = form.save(commit=False)
            health_check.created_by = request.user
            health_check.save()
            messages.success(request, f'Health check "{health_check.name}" created successfully.')
            return redirect('health_check_detail', pk=health_check.pk)
    else:
        form = HealthCheckForm()
    
    return render(request, 'health_checks/health_check_form.html', {
        'form': form,
        'title': 'Create Health Check'
    })


@login_required
def edit_health_check(request, pk):
    """Edit an existing health check"""
    health_check = get_object_or_404(HealthCheck, pk=pk)
    
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to edit health checks.')
        return redirect('health_check_detail', pk=health_check.pk)
        
    if request.method == 'POST':
        form = HealthCheckForm(request.POST, instance=health_check)
        if form.is_valid():
            health_check = form.save()
            messages.success(request, f'Health check "{health_check.name}" updated successfully.')
            return redirect('health_check_detail', pk=health_check.pk)
    else:
        form = HealthCheckForm(instance=health_check)
    
    return render(request, 'health_checks/health_check_form.html', {
        'form': form,
        'health_check': health_check,
        'title': 'Edit Health Check'
    })


@login_required
def delete_health_check(request, pk):
    """Delete a health check"""
    health_check = get_object_or_404(HealthCheck, pk=pk)
    
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to delete health checks.')
        return redirect('health_check_detail', pk=health_check.pk)
        
    if request.method == 'POST':
        health_check_name = health_check.name
        health_check.delete()
        messages.success(request, f'Health check "{health_check_name}" deleted successfully.')
        return redirect('health_check_list')
    
    return render(request, 'health_checks/health_check_confirm_delete.html', {'health_check': health_check})


# Health Check Session Views
@login_required
def session_list(request):
    """List health check sessions"""
    # Different queries based on user role
    if request.user.is_admin() or request.user.is_senior_manager():
        # Admins and senior managers see all sessions
        sessions = HealthCheckSession.objects.all()
    elif request.user.is_department_leader() and request.user.department:
        # Department leaders see sessions for teams in their department
        sessions = HealthCheckSession.objects.filter(team__department=request.user.department)
    else:
        # Team leaders see sessions for teams they lead
        leader_teams = Team.objects.filter(
            team_memberships__user=request.user,
            team_memberships__is_leader=True
        )
        # Regular users see sessions they participate in
        sessions = HealthCheckSession.objects.filter(
            Q(team__in=leader_teams) | Q(participants=request.user)
        ).distinct()
    
    # Filter active sessions
    now = timezone.now()
    active_sessions = sessions.filter(start_date__lte=now, end_date__gte=now)
    past_sessions = sessions.filter(end_date__lt=now).order_by('-end_date')
    future_sessions = sessions.filter(start_date__gt=now).order_by('start_date')
    
    context = {
        'active_sessions': active_sessions,
        'past_sessions': past_sessions,
        'future_sessions': future_sessions
    }
    
    return render(request, 'health_checks/session_list.html', context)


@login_required
def session_detail(request, pk):
    """Show details of a health check session"""
    session = get_object_or_404(HealthCheckSession, pk=pk)
    
    # Check if user has access
    user_is_participant = session.participants.filter(pk=request.user.pk).exists()
    user_is_leader = session.team.team_memberships.filter(user=request.user, is_leader=True).exists()
    user_is_dept_leader = request.user.is_department_leader() and request.user.department == session.team.department
    user_has_access = (user_is_participant or 
                       user_is_leader or 
                       user_is_dept_leader or 
                       request.user.is_admin() or 
                       request.user.is_senior_manager())
    
    if not user_has_access:
        return HttpResponseForbidden("You don't have permission to view this session.")
    
    # Get completion status for participants
    participants = session.participants.all()
    participant_statuses = []
    
    questions = HealthCheckQuestion.objects.all()
    total_questions = questions.count()
    
    for participant in participants:
        if session.anonymous and not (request.user.is_admin() or request.user == participant):
            # For anonymous sessions, only show completion status, not who completed what
            responses_count = HealthCheckResponse.objects.filter(
                session=session,
                user=participant
            ).count()
            
            participant_statuses.append({
                'participant': "Anonymous",
                'completed': responses_count == total_questions,
                'progress': int((responses_count / total_questions * 100) if total_questions > 0 else 0)
            })
        else:
            # For non-anonymous sessions or admins/self, show detailed status
            responses_count = HealthCheckResponse.objects.filter(
                session=session,
                user=participant
            ).count()
            
            participant_statuses.append({
                'participant': participant,
                'completed': responses_count == total_questions,
                'progress': int((responses_count / total_questions * 100) if total_questions > 0 else 0)
            })
    
    # Check if the session is active
    now = timezone.now()
    is_active = session.start_date <= now <= session.end_date
    
    # Get results if session is completed or user is admin/leader
    show_results = (not is_active or 
                   request.user.is_admin() or 
                   user_is_leader or 
                   user_is_dept_leader or 
                   request.user.is_senior_manager())
    
    results = None
    if show_results:
        results = session.get_results_by_category()
    
    context = {
        'session': session,
        'participant_statuses': participant_statuses,
        'is_active': is_active,
        'show_results': show_results,
        'results': results,
        'user_is_participant': user_is_participant
    }
    
    return render(request, 'health_checks/session_detail.html', context)


@login_required
def create_session(request):
    """Create a new health check session"""
    # Only admins, senior managers, department leaders, and team leaders can create sessions
    can_create = (request.user.is_admin() or 
                 request.user.is_senior_manager() or 
                 request.user.is_department_leader() or 
                 Team.objects.filter(team_memberships__user=request.user, team_memberships__is_leader=True).exists())
    
    if not can_create:
        messages.error(request, 'You do not have permission to create health check sessions.')
        return redirect('session_list')
    
    if request.method == 'POST':
        form = HealthCheckSessionForm(request.POST, user=request.user)
        if form.is_valid():
            session = form.save(commit=False)
            session.created_by = request.user
            session.save()
            
            # Save many-to-many relationships
            form.save_m2m()
            
            messages.success(request, f'Health check session for {session.team.name} created successfully.')
            return redirect('session_detail', pk=session.pk)
    else:
        form = HealthCheckSessionForm(user=request.user)
    
    return render(request, 'health_checks/session_form.html', {
        'form': form,
        'title': 'Create Health Check Session'
    })


@login_required
def participate_session(request, pk):
    """Participate in a health check session"""
    session = get_object_or_404(HealthCheckSession, pk=pk)
    
    # Check if user is a participant in this session
    if not session.participants.filter(pk=request.user.pk).exists():
        messages.error(request, 'You are not a participant in this health check session.')
        return redirect('session_list')
    
    # Check if session is active
    now = timezone.now()
    if not (session.start_date <= now <= session.end_date):
        messages.error(request, 'This health check session is not currently active.')
        return redirect('session_detail', pk=session.pk)
    
    # Get all questions
    questions = HealthCheckQuestion.objects.all().order_by('category__order', 'order')
    
    # Check if user has already responded to some questions
    existing_responses = HealthCheckResponse.objects.filter(
        session=session,
        user=request.user
    )
    
    existing_response_dict = {response.question_id: response for response in existing_responses}
    
    # Create initial data for forms
    initial_data = []
    for question in questions:
        if question.id in existing_response_dict:
            # Use existing response data
            response = existing_response_dict[question.id]
            initial_data.append({
                'question': question.id,
                'status': response.status,
                'comment': response.comment
            })
        else:
            # No response yet
            initial_data.append({
                'question': question.id,
                'status': '',
                'comment': ''
            })
    
    # Create a formset with initial data
    ResponseFormSet = formset_factory(HealthCheckResponseForm, extra=0)
    
    if request.method == 'POST':
        formset = ResponseFormSet(request.POST, initial=initial_data)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data.get('status'):  # Only save if status is selected
                    question_id = form.cleaned_data['question']
                    status = form.cleaned_data['status']
                    comment = form.cleaned_data.get('comment', '')
                    
                    # Create or update response
                    HealthCheckResponse.objects.update_or_create(
                        session=session,
                        question_id=question_id,
                        user=request.user,
                        defaults={
                            'status': status,
                            'comment': comment
                        }
                    )
            
            messages.success(request, 'Your responses have been saved successfully.')
            return redirect('session_detail', pk=session.pk)
    else:
        formset = ResponseFormSet(initial=initial_data)
    
    # Group questions by category for display
    categories = HealthCheckCategory.objects.all().order_by('order')
    categorized_forms = {}
    
    for category in categories:
        category_questions = questions.filter(category=category)
        category_form_indices = [i for i, q in enumerate(questions) if q.category == category]
        category_forms = [formset[i] for i in category_form_indices]
        categorized_forms[category] = zip(category_questions, category_forms)
    
    context = {
        'session': session,
        'formset': formset,
        'categorized_forms': categorized_forms,
        'management_form': formset.management_form
    }
    
    return render(request, 'health_checks/participate_session.html', context)


@login_required
def session_results(request, pk):
    """View detailed results of a health check session"""
    session = get_object_or_404(HealthCheckSession, pk=pk)
    
    # Check if user has access
    user_is_leader = session.team.team_memberships.filter(user=request.user, is_leader=True).exists()
    user_is_dept_leader = request.user.is_department_leader() and request.user.department == session.team.department
    user_has_access = (user_is_leader or 
                       user_is_dept_leader or 
                       request.user.is_admin() or 
                       request.user.is_senior_manager())
    
    if not user_has_access:
        return HttpResponseForbidden("You don't have permission to view detailed results.")
    
    # Get results by category
    results = session.get_results_by_category()
    
    # Get all responses
    responses = HealthCheckResponse.objects.filter(session=session).order_by(
        'question__category__order', 'question__order'
    )
    
    # Group responses by category and question
    categories = HealthCheckCategory.objects.all().order_by('order')
    categorized_responses = {}
    
    for category in categories:
        category_questions = HealthCheckQuestion.objects.filter(category=category).order_by('order')
        question_responses = {}
        
        for question in category_questions:
            question_responses[question] = responses.filter(question=question)
        
        if question_responses:
            categorized_responses[category] = question_responses
    
    context = {
        'session': session,
        'results': results,
        'categorized_responses': categorized_responses,
        'show_anonymous': not session.anonymous or request.user.is_admin()
    }
    
    return render(request, 'health_checks/session_results.html', context)


# Category Views
@login_required
def category_list(request):
    """List all health check categories"""
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to manage health check categories.')
        return redirect('health_check_list')
        
    categories = HealthCheckCategory.objects.all().order_by('order')
    return render(request, 'health_checks/category_list.html', {'categories': categories})


@login_required
def create_category(request):
    """Create a new health check category"""
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to create categories.')
        return redirect('category_list')
        
    if request.method == 'POST':
        form = HealthCheckCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('category_list')
    else:
        form = HealthCheckCategoryForm()
    
    return render(request, 'health_checks/category_form.html', {
        'form': form,
        'title': 'Create Category'
    })


@login_required
def edit_category(request, pk):
    """Edit an existing health check category"""
    category = get_object_or_404(HealthCheckCategory, pk=pk)
    
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to edit categories.')
        return redirect('category_list')
        
    if request.method == 'POST':
        form = HealthCheckCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('category_list')
    else:
        form = HealthCheckCategoryForm(instance=category)
    
    return render(request, 'health_checks/category_form.html', {
        'form': form,
        'category': category,
        'title': 'Edit Category'
    })


@login_required
def delete_category(request, pk):
    """Delete a health check category"""
    category = get_object_or_404(HealthCheckCategory, pk=pk)
    
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to delete categories.')
        return redirect('category_list')
        
    # Check if category has questions
    if category.questions.exists():
        messages.error(request, 'Cannot delete category that has questions. Delete or reassign questions first.')
        return redirect('category_list')
        
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully.')
        return redirect('category_list')
    
    return render(request, 'health_checks/category_confirm_delete.html', {'category': category})


# Question Views
@login_required
def question_list(request):
    """List all health check questions"""
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to manage health check questions.')
        return redirect('health_check_list')
        
    questions = HealthCheckQuestion.objects.all().order_by('category__order', 'order')
    return render(request, 'health_checks/question_list.html', {'questions': questions})


@login_required
def create_question(request):
    """Create a new health check question"""
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to create questions.')
        return redirect('question_list')
        
    if request.method == 'POST':
        form = HealthCheckQuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            messages.success(request, f'Question "{question.text}" created successfully.')
            return redirect('question_list')
    else:
        form = HealthCheckQuestionForm()
    
    return render(request, 'health_checks/question_form.html', {
        'form': form,
        'title': 'Create Question'
    })


@login_required
def edit_question(request, pk):
    """Edit an existing health check question"""
    question = get_object_or_404(HealthCheckQuestion, pk=pk)
    
    if not (request.user.is_admin() or request.user.is_senior_manager()):
        messages.error(request, 'You do not have permission to edit questions.')
        return redirect('question_list')
        
    if request.method == 'POST':
        form = HealthCheckQuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            messages.success(request, f'Question "{question.text}" updated successfully.')
            return redirect('question_list')
    else:
        form = HealthCheckQuestionForm(instance=question)
    
    return render(request, 'health_checks/question_form.html', {
        'form': form,
        'question': question,
        'title': 'Edit Question'
    })


@login_required
def delete_question(request, pk):
    """Delete a health check question"""
    question = get_object_or_404(HealthCheckQuestion, pk=pk)
    
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to delete questions.')
        return redirect('question_list')
        
    # Check if question has responses
    if question.responses.exists():
        messages.error(request, 'Cannot delete question that has responses.')
        return redirect('question_list')
        
    if request.method == 'POST':
        question_text = question.text
        question.delete()
        messages.success(request, f'Question "{question_text}" deleted successfully.')
        return redirect('question_list')
    
    return render(request, 'health_checks/question_confirm_delete.html', {'question': question})
