from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg, F, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
import json

from departments.models import Department
from teams.models import Team
from health_checks.models import HealthCheckSession, HealthCheckResponse, HealthCheckCategory
from utils import get_status_color, as_date, date_ge, date_le


@login_required
def dashboard(request):
    """Analytics dashboard showing trends and metrics for health checks"""
    # Check permissions
    user = request.user
    if not (user.is_admin() or user.is_senior_manager() or user.is_department_leader()):
        return render(request, 'analytics/unauthorized.html')
    
    # Get filter parameters
    period = request.GET.get('period', '90')  # Default to 90 days
    try:
        period = int(period)
    except ValueError:
        period = 90
    
    department_id = request.GET.get('department')
    if department_id:
        try:
            department_id = int(department_id)
        except ValueError:
            department_id = None
    
    # Calculate date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period)
    
    # Prepare filter context for data retrieval
    context = {
        'start_date': start_date,
        'end_date': end_date,
    }
    
    # Filter by department if applicable
    if department_id and (user.is_admin() or user.is_senior_manager() or 
                          (user.is_department_leader() and user.department and user.department.id == department_id)):
        context['department'] = department_id
    elif user.is_department_leader() and user.department:
        # Department leaders can only see their own department
        context['department'] = user.department.id
    
    # Get analytics data
    trend_data = get_trend_data(start_date, end_date, 
                               department=context.get('department'),
                               user=user)
    
    category_health = get_category_health(start_date, end_date, 
                                         department=context.get('department'),
                                         user=user)
    
    top_concerns = get_top_concerns(start_date, end_date, 
                                   department=context.get('department'),
                                   user=user)
    
    team_performance = get_team_performance(start_date, end_date, 
                                          department=context.get('department'),
                                          user=user)
    
    # Prepare metrics data
    metrics = {
        'total_sessions': trend_data['total_sessions'],
        'total_teams': trend_data['total_teams'],
        'avg_participation_rate': trend_data['avg_participation_rate'],
        'red_percentage': trend_data['overall']['red'],
        'yellow_percentage': trend_data['overall']['yellow'],
        'green_percentage': trend_data['overall']['green'],
    }
    
    # Prepare chart data
    chart_data = {
        'trend_labels': json.dumps(trend_data['labels']),
        'red_trend': json.dumps(trend_data['red_percentage']),
        'yellow_trend': json.dumps(trend_data['yellow_percentage']),
        'green_trend': json.dumps(trend_data['green_percentage']),
        'red_count': json.dumps(trend_data['red_count']),
        'yellow_count': json.dumps(trend_data['yellow_count']),
        'green_count': json.dumps(trend_data['green_count']),
        'category_names': json.dumps(category_health['categories']),
        'category_red': json.dumps(category_health['red']),
        'category_yellow': json.dumps(category_health['yellow']),
        'category_green': json.dumps(category_health['green']),
    }
    
    # Get departments for filtering (respecting permissions)
    if user.is_admin() or user.is_senior_manager():
        departments = Department.objects.all().order_by('name')
    elif user.is_department_leader() and user.department:
        departments = Department.objects.filter(id=user.department.id)
    else:
        departments = Department.objects.none()
    
    return render(request, 'analytics/dashboard.html', {
        'metrics': metrics,
        'chart_data': chart_data,
        'top_concerns': top_concerns,
        'teams_data': team_performance,
        'departments': departments,
        'period': period,
        'selected_department': context.get('department'),
    })


def get_trend_data(start_date, end_date, department=None, user=None):
    """Get trend data for the specified time range"""
    # Calculate date points (each point will be a week or a month depending on range)
    date_range = (end_date - start_date).days
    
    if date_range <= 90:  # For shorter ranges, use weekly points
        interval = 7
        format_string = '%b %d'  # e.g., "Jan 01"
    else:  # For longer ranges, use monthly points
        interval = 30
        format_string = '%b %Y'  # e.g., "Jan 2023"
    
    date_points = []
    current_date = start_date
    while current_date <= end_date:
        date_points.append(current_date)
        current_date += timedelta(days=interval)
    
    if date_points[-1] != end_date:
        date_points.append(end_date)
    
    # Query sessions
    sessions_query = HealthCheckSession.objects.filter(
        start_date__gte=start_date,
        start_date__lte=end_date
    )
    
    # Apply filters based on permissions
    if department:
        sessions_query = sessions_query.filter(team__department_id=department)
    elif user and user.is_department_leader() and user.department:
        sessions_query = sessions_query.filter(team__department_id=user.department.id)
    
    # Get all responses for these sessions
    response_query = HealthCheckResponse.objects.filter(
        session__in=sessions_query
    ).select_related('session')
    
    # Count total sessions and teams
    total_sessions = sessions_query.count()
    total_teams = sessions_query.values('team').distinct().count()
    
    # Calculate average participation rate
    avg_participation_rate = sessions_query.annotate(
        participation_rate=Count('participants') * 100.0 / F('team__members')
    ).aggregate(avg_rate=Avg('participation_rate'))['avg_rate'] or 0
    
    # Initialize data structures
    result = {
        'labels': [],
        'red_percentage': [],
        'yellow_percentage': [],
        'green_percentage': [],
        'red_count': [],
        'yellow_count': [],
        'green_count': [],
        'total_sessions': total_sessions,
        'total_teams': total_teams,
        'avg_participation_rate': round(avg_participation_rate, 1),
        'overall': {'red': 0, 'yellow': 0, 'green': 0}
    }
    
    # Calculate overall percentages
    response_counts = response_query.values('status').annotate(count=Count('id'))
    total_responses = sum(item['count'] for item in response_counts)
    
    if total_responses > 0:
        for item in response_counts:
            status = item['status'].lower()
            percentage = round((item['count'] / total_responses) * 100, 1)
            if status in ['red', 'yellow', 'green']:
                result['overall'][status] = percentage
    
    # Format date points for display
    result['labels'] = [d.strftime(format_string) for d in date_points]
    
    # Calculate trend data for each period
    for i in range(len(date_points) - 1):
        period_start = date_points[i]
        period_end = date_points[i+1]
        
        # Get responses in this period
        period_responses = response_query.filter(
            session__start_date__gte=period_start,
            session__start_date__lt=period_end
        )
        
        # Count by status
        status_counts = {
            'red': 0,
            'yellow': 0,
            'green': 0
        }
        
        for res in period_responses.values('status').annotate(count=Count('id')):
            status_counts[res['status'].lower()] = res['count']
        
        total_period = sum(status_counts.values())
        
        # Calculate percentages
        red_percentage = round((status_counts['red'] / total_period * 100), 1) if total_period > 0 else 0
        yellow_percentage = round((status_counts['yellow'] / total_period * 100), 1) if total_period > 0 else 0
        green_percentage = round((status_counts['green'] / total_period * 100), 1) if total_period > 0 else 0
        
        # Add to result
        result['red_percentage'].append(red_percentage)
        result['yellow_percentage'].append(yellow_percentage)
        result['green_percentage'].append(green_percentage)
        result['red_count'].append(status_counts['red'])
        result['yellow_count'].append(status_counts['yellow'])
        result['green_count'].append(status_counts['green'])
    
    return result


def get_category_health(start_date, end_date, department=None, user=None):
    """Get health metrics by category"""
    # Query sessions
    sessions_query = HealthCheckSession.objects.filter(
        start_date__gte=start_date,
        start_date__lte=end_date
    )
    
    # Apply filters based on permissions
    if department:
        sessions_query = sessions_query.filter(team__department_id=department)
    elif user and user.is_department_leader() and user.department:
        sessions_query = sessions_query.filter(team__department_id=user.department.id)
    
    # Get all categories
    categories = HealthCheckCategory.objects.all().order_by('order')
    category_names = [cat.name for cat in categories]
    
    # Initialize results
    result = {
        'categories': category_names,
        'red': [],
        'yellow': [],
        'green': []
    }
    
    # For each category, calculate the percentages
    for category in categories:
        responses = HealthCheckResponse.objects.filter(
            session__in=sessions_query,
            question__category=category
        ).values('status').annotate(count=Count('id'))
        
        total_responses = sum(item['count'] for item in responses)
        status_counts = {
            'red': 0,
            'yellow': 0,
            'green': 0
        }
        
        for res in responses:
            status_counts[res['status'].lower()] = res['count']
        
        # Calculate percentages
        if total_responses > 0:
            red_pct = round((status_counts['red'] / total_responses * 100), 1)
            yellow_pct = round((status_counts['yellow'] / total_responses * 100), 1)
            green_pct = round((status_counts['green'] / total_responses * 100), 1)
        else:
            red_pct = yellow_pct = green_pct = 0
        
        result['red'].append(red_pct)
        result['yellow'].append(yellow_pct)
        result['green'].append(green_pct)
    
    return result


def get_top_concerns(start_date, end_date, department=None, user=None, limit=10):
    """Get top concerns (questions with highest red percentage)"""
    # Query sessions
    sessions_query = HealthCheckSession.objects.filter(
        start_date__gte=start_date,
        start_date__lte=end_date
    )
    
    # Apply filters based on permissions
    if department:
        sessions_query = sessions_query.filter(team__department_id=department)
    elif user and user.is_department_leader() and user.department:
        sessions_query = sessions_query.filter(team__department_id=user.department.id)
    
    # Group responses by question and calculate red percentage
    responses_by_question = HealthCheckResponse.objects.filter(
        session__in=sessions_query
    ).values(
        'question__id', 
        'question__text', 
        'question__category__name'
    ).annotate(
        total_responses=Count('id'),
        red_responses=Count(Case(
            When(status='red', then=1),
            output_field=IntegerField()
        ))
    ).filter(total_responses__gt=0)
    
    # Calculate percentages and sort
    concerns = []
    for item in responses_by_question:
        red_percentage = round((item['red_responses'] / item['total_responses'] * 100), 1)
        concerns.append({
            'question_id': item['question__id'],
            'question_text': item['question__text'],
            'category_name': item['question__category__name'],
            'red_percentage': red_percentage,
            'total_responses': item['total_responses']
        })
    
    # Sort by red percentage (highest first) and take top N
    concerns = sorted(concerns, key=lambda x: x['red_percentage'], reverse=True)[:limit]
    
    return concerns


def get_team_performance(start_date, end_date, department=None, user=None):
    """Get performance data for teams"""
    # Query sessions
    sessions_query = HealthCheckSession.objects.filter(
        start_date__gte=start_date,
        start_date__lte=end_date
    )
    
    # Apply filters based on permissions
    if department:
        sessions_query = sessions_query.filter(team__department_id=department)
    elif user and user.is_department_leader() and user.department:
        sessions_query = sessions_query.filter(team__department_id=user.department.id)
    
    # Get list of teams with sessions
    team_ids = sessions_query.values_list('team_id', flat=True).distinct()
    teams = Team.objects.filter(id__in=team_ids).select_related('department')
    
    team_performance = []
    
    for team in teams:
        team_sessions = sessions_query.filter(team=team).order_by('-start_date')
        
        if not team_sessions.exists():
            continue
        
        # Calculate health metrics for this team
        team_responses = HealthCheckResponse.objects.filter(
            session__in=team_sessions
        ).values('status').annotate(count=Count('id'))
        
        total_responses = sum(item['count'] for item in team_responses)
        status_counts = {
            'red': 0,
            'yellow': 0,
            'green': 0
        }
        
        for res in team_responses:
            status_counts[res['status'].lower()] = res['count']
        
        # Calculate percentages
        if total_responses > 0:
            red_pct = round((status_counts['red'] / total_responses * 100), 1)
            yellow_pct = round((status_counts['yellow'] / total_responses * 100), 1)
            green_pct = round((status_counts['green'] / total_responses * 100), 1)
        else:
            red_pct = yellow_pct = green_pct = 0
        
        # Calculate trend (compare current with previous period)
        last_session = team_sessions.first()
        mid_point = start_date + (end_date - start_date) / 2
        
        # Get responses for first and second half of the period
        recent_responses = HealthCheckResponse.objects.filter(
            session__team=team,
            session__start_date__gt=mid_point,
            session__start_date__lte=end_date
        )
        earlier_responses = HealthCheckResponse.objects.filter(
            session__team=team,
            session__start_date__gte=start_date,
            session__start_date__lte=mid_point
        )
        
        # Calculate green percentages for both periods
        recent_total = recent_responses.count()
        earlier_total = earlier_responses.count()
        
        recent_green = recent_responses.filter(status='green').count()
        earlier_green = earlier_responses.filter(status='green').count()
        
        recent_green_pct = (recent_green / recent_total * 100) if recent_total > 0 else 0
        earlier_green_pct = (earlier_green / earlier_total * 100) if earlier_total > 0 else 0
        
        # Calculate trend
        trend = round(recent_green_pct - earlier_green_pct, 1) if recent_total > 0 and earlier_total > 0 else 0
        
        team_performance.append({
            'id': team.id,
            'name': team.name,
            'department_name': team.department.name if team.department else 'No Department',
            'sessions_count': team_sessions.count(),
            'last_session_date': last_session.start_date.strftime('%Y-%m-%d') if last_session else 'N/A',
            'red_percentage': red_pct,
            'yellow_percentage': yellow_pct,
            'green_percentage': green_pct,
            'trend': trend
        })
    
    # Sort by health score (green percentage) descending
    team_performance = sorted(team_performance, key=lambda x: x['green_percentage'], reverse=True)
    
    return team_performance