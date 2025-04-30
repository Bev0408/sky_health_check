from django.db import models
from django.utils import timezone


class Department(models.Model):
    """Department model for organizing teams and users."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
        
    class Meta:
        ordering = ['name']
