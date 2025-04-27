from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Represents a Department within the organization
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True) # Department name [cite: 31]

    def __str__(self):
        return self.name

# Represents a Team, which belongs to a Department
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True) # Team name [cite: 26]
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams') # Link to Department [cite: 27, 31]

    def __str__(self):
        return f"{self.name} ({self.department.name})"

# Extends the built-in Django User model to add role and team information
class Profile(models.Model):
    # Role choices based on requirements [cite: 26, 27, 30, 32]
    ROLE_CHOICES = [
        ('ENG', 'Engineer'),
        ('TL', 'Team Leader'),
        ('DL', 'Department Leader'),
        ('SM', 'Senior Manager'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Link to the standard Django user [cite: 26]
    role = models.CharField(max_length=3, choices=ROLE_CHOICES, default='ENG') # User role [cite: 26, 27, 30, 32]
    # Team association - nullable=True because Dept Leaders/Senior Managers might not belong to a specific team [cite: 26, 30, 32]
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

# Represents a Health Check session/period
class Session(models.Model):
    name = models.CharField(max_length=100) # e.g., "Q1 2025" [cite: 26]
    start_date = models.DateField() # Start date for the session [cite: 25]
    end_date = models.DateField() # End date for the session [cite: 25]
    is_active = models.BooleanField(default=True) # To control which sessions are open for voting

    def __str__(self):
        return self.name

# Represents a specific Health Check area/card
class HealthCard(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g., "Codebase Health" [cite: 3]
    description = models.TextField(blank=True, null=True) # Optional description

    def __str__(self):
        return self.name

# Represents a single vote cast by a user for a specific card during a specific session
class Vote(models.Model):
    # Choices for the vote value [cite: 27]
    VOTE_CHOICES = [
        ('R', 'Red'),
        ('A', 'Amber'),
        ('G', 'Green'),
    ]
    # Choices for progress opinion [cite: 27]
    PROGRESS_CHOICES = [
        ('B', 'Better'),
        ('S', 'Same'),
        ('W', 'Worse'),
        (None, 'N/A'), # Optional: If no opinion given
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes') # User who cast the vote [cite: 26, 27]
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='votes') # Session the vote belongs to [cite: 26]
    card = models.ForeignKey(HealthCard, on_delete=models.CASCADE, related_name='votes') # Health card being voted on [cite: 27]
    vote_value = models.CharField(max_length=1, choices=VOTE_CHOICES) # The actual vote (Red/Amber/Green) [cite: 27]
    progress_opinion = models.CharField(max_length=1, choices=PROGRESS_CHOICES, null=True, blank=True) # Opinion on progress [cite: 27]
    timestamp = models.DateTimeField(default=timezone.now) # When the vote was last saved/updated

    class Meta:
        # Ensures a user can only vote once per card per session
        unique_together = ('user', 'session', 'card')

    def __str__(self):
        return f"{self.user.username} - {self.card.name} ({self.session.name}): {self.get_vote_value_display()}"
