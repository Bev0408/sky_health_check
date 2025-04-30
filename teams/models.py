from django.db import models
from django.utils import timezone
from django.conf import settings


class Team(models.Model):
    """Team model for organizing users."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        'departments.Department', 
        on_delete=models.CASCADE,
        related_name='teams'
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    # Many-to-many relationship with User
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='TeamMember',
        related_name='teams'
    )
    
    def __str__(self):
        return self.name
    
    def get_leader(self):
        """Get the team leader"""
        leader_membership = self.team_memberships.filter(is_leader=True).first()
        return leader_membership.user if leader_membership else None
    
    def add_member(self, user, is_leader=False):
        """Add a member to the team"""
        membership, created = TeamMember.objects.get_or_create(
            team=self,
            user=user,
            defaults={'is_leader': is_leader}
        )
        if not created and is_leader:
            membership.is_leader = is_leader
            membership.save()
        return membership
    
    def remove_member(self, user):
        """Remove a member from the team"""
        TeamMember.objects.filter(team=self, user=user).delete()
    
    def set_leader(self, user):
        """Set a user as the team leader"""
        # First, remove any existing leader
        TeamMember.objects.filter(team=self, is_leader=True).update(is_leader=False)
        
        # Then set the new leader
        membership, created = TeamMember.objects.get_or_create(
            team=self,
            user=user,
            defaults={'is_leader': True}
        )
        if not created:
            membership.is_leader = True
            membership.save()
        return membership
    
    class Meta:
        ordering = ['name']


class TeamMember(models.Model):
    """Intermediary model for Team-User many-to-many relationship."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    is_leader = models.BooleanField(default=False)
    joined_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'team')
        ordering = ['-is_leader', 'joined_at']
    
    def __str__(self):
        leader_status = " (Leader)" if self.is_leader else ""
        return f"{self.user.username} in {self.team.name}{leader_status}"
