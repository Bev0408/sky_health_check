from django.contrib import admin
from .models import Department, Team, Profile, Session, HealthCard, Vote

# Register your models here
admin.site.register(Department)
admin.site.register(Team)
admin.site.register(Profile)
admin.site.register(Session)
admin.site.register(HealthCard)
admin.site.register(Vote)
