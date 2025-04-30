from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('test/', views.test_page, name='test_page'),

    # Profile management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/', views.UserPasswordChangeDoneView.as_view(), name='password_change_done'),

    #voting feature
    path('vote/', views.engineer_vote_view, name='engineer_vote'),
]
