from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('create/', views.create_team, name='create_team'),
    path('<int:pk>/', views.team_detail, name='team_detail'),
    path('<int:pk>/edit/', views.edit_team, name='edit_team'),
    path('<int:pk>/delete/', views.delete_team, name='delete_team'),
    path('<int:pk>/add-member/', views.add_team_member, name='add_team_member'),
    path('<int:team_pk>/remove-member/<int:user_pk>/', views.remove_team_member, name='remove_team_member'),
    path('<int:team_pk>/set-leader/<int:user_pk>/', views.set_team_leader, name='set_team_leader'),
]