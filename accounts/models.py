from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as the unique identifier instead of username."""
    
    username = models.CharField(_('username'), max_length=64, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('full name'), max_length=100, blank=True)
    
    # Define role choices
    ENGINEER = 'engineer'
    TEAM_LEADER = 'team_leader'
    DEPARTMENT_LEADER = 'department_leader'
    SENIOR_MANAGER = 'senior_manager'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (ENGINEER, _('Engineer')),
        (TEAM_LEADER, _('Team Leader')),
        (DEPARTMENT_LEADER, _('Department Leader')),
        (SENIOR_MANAGER, _('Senior Manager')),
        (ADMIN, _('Administrator')),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        default=ENGINEER,
    )
    
    department = models.ForeignKey(
        'departments.Department', 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='users'
    )
    
    objects = UserManager()
    
    def __str__(self):
        return self.username
    
    def is_admin(self):
        return self.role == self.ADMIN
    
    def is_senior_manager(self):
        return self.role == self.SENIOR_MANAGER
    
    def is_department_leader(self):
        return self.role == self.DEPARTMENT_LEADER
    
    def is_team_leader(self):
        return self.role == self.TEAM_LEADER
    
    def get_led_teams(self):
        """Get teams where user is a leader"""
        return self.teams_led.all()
