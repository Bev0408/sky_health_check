from django.db import models
from django.utils import timezone
from django.conf import settings


class HealthCheckCategory(models.Model):
    """Categories for health check questions."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Health Check Categories"
        ordering = ['order', 'name']


class HealthCheckQuestion(models.Model):
    """Questions used in health checks."""
    
    text = models.CharField(max_length=200)
    detail = models.TextField(blank=True)
    category = models.ForeignKey(
        HealthCheckCategory,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.text
    
    class Meta:
        ordering = ['category__order', 'order', 'text']


class HealthCheck(models.Model):
    """Health check template."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_template = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_health_checks'
    )
    
    def __str__(self):
        return self.name
    
    def get_active_session(self, team_id=None):
        """Get the active session for this health check, optionally for a specific team."""
        now = timezone.now()
        sessions = self.sessions.filter(
            start_date__lte=now,
            end_date__gte=now
        )
        if team_id:
            sessions = sessions.filter(team_id=team_id)
        return sessions.first()
    
    def get_categories(self):
        """Get all categories that have questions in this health check."""
        # This would likely need a more complex implementation 
        # if questions are associated with health checks
        return HealthCheckCategory.objects.all()
    
    class Meta:
        verbose_name_plural = "Health Checks"
        ordering = ['-created_at']


class HealthCheckSession(models.Model):
    """An instance of a health check for a specific team."""
    
    health_check = models.ForeignKey(
        HealthCheck,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='health_check_sessions'
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    anonymous = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sessions'
    )
    created_at = models.DateTimeField(default=timezone.now)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_sessions'
    )
    
    def __str__(self):
        return f"{self.health_check.name} for {self.team.name} ({self.start_date.date()})"
    
    def get_completion_percentage(self):
        """Calculate the percentage of responses received."""
        if not self.participants.exists():
            return 0
            
        total_participants = self.participants.count()
        total_questions = HealthCheckQuestion.objects.count()
        
        if total_participants == 0 or total_questions == 0:
            return 0
            
        responses_count = self.responses.values('user').distinct().count()
        return int((responses_count / total_participants) * 100)
    
    def get_results_by_category(self):
        """Get aggregated results by category and overall."""
        responses = self.responses.all()
        
        # Map status values to red/yellow/green for template
        status_mapping = {
            'needs_attention': 'red',
            'room_for_improvement': 'yellow',
            'doing_well': 'green'
        }
        
        # Count all responses by status
        all_red = responses.filter(status='needs_attention').count()
        all_yellow = responses.filter(status='room_for_improvement').count()
        all_green = responses.filter(status='doing_well').count()
        
        total_responses = all_red + all_yellow + all_green
        
        # Calculate percentages
        if total_responses > 0:
            red_percentage = round((all_red / total_responses) * 100)
            yellow_percentage = round((all_yellow / total_responses) * 100)
            green_percentage = round((all_green / total_responses) * 100)
        else:
            red_percentage = yellow_percentage = green_percentage = 0
        
        # Calculate participation rate
        total_participants = self.participants.count()
        # Fix: Use all questions instead of trying to access via health_check
        total_questions = HealthCheckQuestion.objects.count()
        
        expected_responses = total_participants * total_questions
        participation_rate = round((total_responses / expected_responses) * 100) if expected_responses > 0 else 0
        
        # Prepare results dictionary
        results = {
            'red_count': all_red,
            'yellow_count': all_yellow,
            'green_count': all_green,
            'red_percentage': red_percentage,
            'yellow_percentage': yellow_percentage,
            'green_percentage': green_percentage,
            'total_responses': total_responses,
            'participation_rate': participation_rate,
            'categories': {}
        }
        
        # Group by category
        for category in HealthCheckCategory.objects.all():
            category_responses = responses.filter(question__category=category)
            
            if not category_responses.exists():
                continue
                
            # Count by status for this category
            cat_red = category_responses.filter(status='needs_attention').count()
            cat_yellow = category_responses.filter(status='room_for_improvement').count()
            cat_green = category_responses.filter(status='doing_well').count()
            
            cat_total = cat_red + cat_yellow + cat_green
            
            # Calculate percentages for this category
            if cat_total > 0:
                cat_red_pct = round((cat_red / cat_total) * 100)
                cat_yellow_pct = round((cat_yellow / cat_total) * 100)
                cat_green_pct = round((cat_green / cat_total) * 100)
            else:
                cat_red_pct = cat_yellow_pct = cat_green_pct = 0
            
            results['categories'][category.name] = {
                'red_count': cat_red,
                'yellow_count': cat_yellow,
                'green_count': cat_green,
                'red_percentage': cat_red_pct,
                'yellow_percentage': cat_yellow_pct,
                'green_percentage': cat_green_pct,
                'total': cat_total
            }
            
        return results
    
    class Meta:
        ordering = ['-start_date']


class HealthCheckResponse(models.Model):
    """Individual response to a health check question."""
    
    STATUS_CHOICES = [
        ('needs_attention', 'Needs Attention'),
        ('room_for_improvement', 'Room for Improvement'),
        ('doing_well', 'Doing Well'),
    ]
    
    # Mapping for template display (used in templates via the status_color property)
    STATUS_COLOR_MAPPING = {
        'needs_attention': 'red',
        'room_for_improvement': 'yellow',
        'doing_well': 'green',
    }
    
    session = models.ForeignKey(
        HealthCheckSession,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        HealthCheckQuestion,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Response by {self.user.username} for {self.question.text}"
    
    def status_label(self):
        """Return human-readable status."""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
        
    @property
    def status_color(self):
        """Return the color representation (red/yellow/green) of this status."""
        return self.STATUS_COLOR_MAPPING.get(self.status, 'secondary')
    
    class Meta:
        unique_together = ('session', 'question', 'user')
        ordering = ['session', 'question__category__order', 'question__order']
