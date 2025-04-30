from django.urls import path
from . import views

urlpatterns = [
    # Health check management
    path('', views.health_check_list, name='health_check_list'),
    path('create/', views.create_health_check, name='create_health_check'),
    path('<int:pk>/', views.health_check_detail, name='health_check_detail'),
    path('<int:pk>/edit/', views.edit_health_check, name='edit_health_check'),
    path('<int:pk>/delete/', views.delete_health_check, name='delete_health_check'),
    
    # Health check sessions
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/create/', views.create_session, name='create_session'),
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),
    path('sessions/<int:pk>/participate/', views.participate_session, name='participate_session'),
    path('sessions/<int:pk>/results/', views.session_results, name='session_results'),
    
    # Health check categories and questions
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    
    path('questions/', views.question_list, name='question_list'),
    path('questions/create/', views.create_question, name='create_question'),
    path('questions/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('questions/<int:pk>/delete/', views.delete_question, name='delete_question'),
]