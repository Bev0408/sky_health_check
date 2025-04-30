from datetime import datetime, timedelta
from django.utils import timezone
from accounts.models import User
from teams.models import Team
from departments.models import Department
from health_checks.models import (
    HealthCheck, HealthCheckSession, HealthCheckCategory, 
    HealthCheckQuestion, HealthCheckResponse
)

def format_date(date):
    """Format a date to display format"""
    if isinstance(date, datetime):
        return date.strftime('%b %d, %Y')
    return date

def as_date(dt):
    """Convert datetime to date for comparison"""
    if isinstance(dt, datetime):
        return dt.date()
    return dt

def date_ge(a, b):
    """Compare dates safely (greater than or equal)"""
    if isinstance(a, datetime):
        a = a.date()
    if isinstance(b, datetime):
        b = b.date()
    return a >= b

def date_gt(a, b):
    """Compare dates safely (greater than)"""
    if isinstance(a, datetime):
        a = a.date()
    if isinstance(b, datetime):
        b = b.date()
    return a > b

def date_lt(a, b):
    """Compare dates safely (less than)"""
    if isinstance(a, datetime):
        a = a.date()
    if isinstance(b, datetime):
        b = b.date()
    return a < b

def date_le(a, b):
    """Compare dates safely (less than or equal)"""
    if isinstance(a, datetime):
        a = a.date()
    if isinstance(b, datetime):
        b = b.date()
    return a <= b

def get_user_teams(user):
    """Get teams a user belongs to, with proper filtering based on role"""
    if user.is_admin() or user.is_senior_manager():
        return Team.objects.all()
    elif user.is_department_leader() and user.department:
        return Team.objects.filter(department=user.department)
    else:
        return user.teams.all()

def get_status_color(status):
    """Get the color class for a status"""
    colors = {
        'red': 'danger',
        'yellow': 'warning',
        'green': 'success'
    }
    return colors.get(status.lower(), 'secondary')

def get_status_badge(status):
    """Get the Bootstrap badge class for a status"""
    return f"bg-{get_status_color(status)}"

def calculate_overall_health(team_ids):
    """Calculate overall health metrics for teams"""
    overall_health = {
        'team_collaboration': {'red': 0, 'yellow': 0, 'green': 0, 'total': 0},
        'technical_health': {'red': 0, 'yellow': 0, 'green': 0, 'total': 0},
        'process_health': {'red': 0, 'yellow': 0, 'green': 0, 'total': 0}
    }
    
    # Get categories
    team_collaboration = HealthCheckCategory.objects.filter(name="Team Collaboration").first()
    technical_excellence = HealthCheckCategory.objects.filter(name="Technical Excellence").first()
    delivery_process = HealthCheckCategory.objects.filter(name="Delivery Process").first()
    
    if team_ids:
        # Get recent health check data (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        
        # Team Collaboration metrics
        if team_collaboration:
            team_collab_responses = HealthCheckResponse.objects.filter(
                question__category=team_collaboration,
                session__team__in=team_ids,
                session__created_at__gte=thirty_days_ago
            )
            
            for resp in team_collab_responses:
                overall_health['team_collaboration']['total'] += 1
                overall_health['team_collaboration'][resp.status.lower()] += 1
        
        # Technical Excellence metrics
        if technical_excellence:
            tech_responses = HealthCheckResponse.objects.filter(
                question__category=technical_excellence,
                session__team__in=team_ids,
                session__created_at__gte=thirty_days_ago
            )
            
            for resp in tech_responses:
                overall_health['technical_health']['total'] += 1
                overall_health['technical_health'][resp.status.lower()] += 1
        
        # Delivery Process metrics
        if delivery_process:
            process_responses = HealthCheckResponse.objects.filter(
                question__category=delivery_process,
                session__team__in=team_ids,
                session__created_at__gte=thirty_days_ago
            )
            
            for resp in process_responses:
                overall_health['process_health']['total'] += 1
                overall_health['process_health'][resp.status.lower()] += 1
    
    # Calculate percentages
    for category, data in overall_health.items():
        total = data['total']
        if total > 0:
            data['red_percent'] = round((data['red'] / total) * 100)
            data['yellow_percent'] = round((data['yellow'] / total) * 100)
            data['green_percent'] = round((data['green'] / total) * 100)
        else:
            data['red_percent'] = 0
            data['yellow_percent'] = 0
            data['green_percent'] = 0
    
    return overall_health
