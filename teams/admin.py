from django.contrib import admin
from .models import Team, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    autocomplete_fields = ['user']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'get_leader_display', 'created_at')
    list_filter = ('department',)
    search_fields = ('name',)
    inlines = [TeamMemberInline]
    autocomplete_fields = ['department']

    def get_leader_display(self, obj):
        leader = obj.get_leader()
        return leader.username if leader else "No leader assigned"
    get_leader_display.short_description = 'Team Leader'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'is_leader', 'joined_at')
    list_filter = ('is_leader', 'team', 'team__department')
    search_fields = ('user__username', 'user__email', 'team__name')
    autocomplete_fields = ['user', 'team']
