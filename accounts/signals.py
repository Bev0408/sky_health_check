from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def update_user_related_entities(sender, instance, created, **kwargs):
    """
    Signal handler to update related entities when a user is saved.
    For example, if a user's role is changed to team_leader, this could update team memberships.
    """
    if not created:
        # Check if the user's role has been changed to team_leader
        if instance.is_team_leader():
            # This is just a placeholder for future functionality
            # You could automatically add logic here to handle role changes
            pass
        
        # Handle department changes
        # If user changes department, they might need to be removed from teams in old department
        # This would be implemented based on your specific business logic
        pass