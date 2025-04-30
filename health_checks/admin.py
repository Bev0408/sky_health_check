from django.contrib import admin
from .models import (
    HealthCheckCategory, 
    HealthCheckQuestion, 
    HealthCheck, 
    HealthCheckSession,
    HealthCheckResponse
)


@admin.register(HealthCheckCategory)
class HealthCheckCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    search_fields = ('name',)
    ordering = ('order', 'name')


class HealthCheckQuestionInline(admin.TabularInline):
    model = HealthCheckQuestion
    extra = 1


@admin.register(HealthCheckQuestion)
class HealthCheckQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'order')
    list_filter = ('category',)
    search_fields = ('text',)
    ordering = ('category__order', 'order', 'text')


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_template', 'created_by', 'created_at')
    list_filter = ('is_template',)
    search_fields = ('name',)
    date_hierarchy = 'created_at'


class HealthCheckResponseInline(admin.TabularInline):
    model = HealthCheckResponse
    extra = 0
    readonly_fields = ('created_at',)
    autocomplete_fields = ['user', 'question']


@admin.register(HealthCheckSession)
class HealthCheckSessionAdmin(admin.ModelAdmin):
    list_display = ('health_check', 'team', 'start_date', 'end_date', 'anonymous', 'created_by')
    list_filter = ('anonymous', 'team', 'health_check')
    search_fields = ('health_check__name', 'team__name')
    date_hierarchy = 'start_date'
    filter_horizontal = ('participants',)
    inlines = [HealthCheckResponseInline]
    

@admin.register(HealthCheckResponse)
class HealthCheckResponseAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'user', 'status', 'created_at')
    list_filter = ('status', 'session', 'question__category')
    search_fields = ('user__username', 'question__text', 'comment')
    date_hierarchy = 'created_at'
    autocomplete_fields = ['user', 'question', 'session']
