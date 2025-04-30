from django.urls import path
from . import views

urlpatterns = [
    path('', views.department_list, name='department_list'),
    path('create/', views.create_department, name='create_department'),
    path('<int:pk>/', views.department_detail, name='department_detail'),
    path('<int:pk>/edit/', views.edit_department, name='edit_department'),
    path('<int:pk>/delete/', views.delete_department, name='delete_department'),
]