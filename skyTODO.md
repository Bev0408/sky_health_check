To-Do List: User Authentication & Profiles Module
Goal: Implement user registration, login, logout, and basic profile management by end of Monday, April 28th.

Phase 0: Project Setup (Complete Tonight/Very Early Monday)
[ ] Create project directory: mkdir sky_health_check && cd sky_health_check

[ ] Create virtual environment: python -m venv venv

[ ] Activate virtual environment (source venv/bin/activate or venv\Scripts\activate)

[ ] Install Django: pip install django

[ ] Create Django project: django-admin startproject config .

[ ] Create Django app: python manage.py startapp health_app

[ ] Add agreed models to health_app/models.py

[ ] Add health_app to INSTALLED_APPS in config/settings.py

[ ] Verify DATABASES setting in config/settings.py

[ ] Initialize Git: git init

[ ] Create and configure .gitignore file

[ ] Create migrations: python manage.py makemigrations health_app

[ ] Apply migrations: python manage.py migrate

[ ] Commit initial setup: git add . && git commit -m "Initial project setup"

[ ] (Optional) Push to remote repository: git remote add origin ... && git push -u origin main

Phase 1: User Registration (Monday)
Forms:

[ ] Create forms.py in health_app.

[ ] Define a UserRegistrationForm using django.forms or django.contrib.auth.forms.UserCreationForm as a base.

[ ] Include fields: first_name, last_name, username, email, password, password2 (for confirmation).

[ ] Add validation logic (e.g., check if passwords match, potentially add custom validation).

Views:

[ ] Create a function-based or class-based view for registration in health_app/views.py.

[ ] Handle GET requests: Display an empty UserRegistrationForm.

[ ] Handle POST requests:

[ ] Instantiate the form with POST data.

[ ] Check if the form is valid (form.is_valid()).

[ ] If valid:

[ ] Save the new user (form.save()). Ensure password gets hashed correctly (automatic with UserCreationForm).

[ ] Redirect to a success page or login page.

[ ] If invalid: Re-render the registration page with the form containing errors.

URLs:

[ ] Create urls.py in health_app.

[ ] Define a URL pattern for the registration view (e.g., path('register/', views.registration_view, name='register')).

[ ] Include health_app.urls in the main config/urls.py.

Templates:

[ ] Create templates/health_app/ directory.

[ ] Create register.html template.

[ ] Render the registration form using Django template tags (e.g., {{ form.as_p }}).

[ ] Include CSRF token ({% csrf_token %}).

[ ] Add basic HTML structure and submit button.

[ ] Create a simple registration_done.html template (optional success page).

Testing:

[ ] Manually test registration with valid data.

[ ] Manually test registration with invalid data (passwords mismatch, existing username/email).

Phase 2: User Login & Logout (Monday)
Views (Login):

[ ] Import LoginView from django.contrib.auth.views.

[ ] Use LoginView directly in health_app/urls.py or create a simple wrapper view if customization needed later.

Views (Logout):

[ ] Import LogoutView from django.contrib.auth.views.

[ ] Use LogoutView directly in health_app/urls.py.

URLs:

[ ] Add URL patterns for login and logout using the built-in views (e.g., path('login/', LoginView.as_view(template_name='health_app/login.html'), name='login')).

[ ] Add URL pattern for logout (e.g., path('logout/', LogoutView.as_view(), name='logout')).

Templates:

[ ] Create login.html template.

[ ] Render the login form (Django provides this via LoginView).

[ ] Include CSRF token.

[ ] Add basic HTML structure and submit button.

Settings:

[ ] Define LOGIN_REDIRECT_URL and LOGOUT_REDIRECT_URL in config/settings.py (e.g., LOGIN_REDIRECT_URL = '/dashboard/', LOGOUT_REDIRECT_URL = '/login/').

Basic Dashboard/Landing Page:

[ ] Create a simple view for the post-login landing page (e.g., dashboard view).

[ ] Add URL pattern for the dashboard (e.g., /dashboard/).

[ ] Create dashboard.html template.

[ ] Add a welcome message (e.g., Welcome, {{ user.username }}) and a Logout link.

[ ] Protect this view using @login_required decorator or LoginRequiredMixin.

Testing:

[ ] Manually test login with correct credentials.

[ ] Manually test login with incorrect credentials.

[ ] Manually test logout.

[ ] Verify redirection after login/logout.

[ ] Verify dashboard is inaccessible when logged out.

Phase 3: Profile Management (Monday)
Forms:

[ ] Create UserProfileUpdateForm (fields: first_name, last_name). Consider using forms.ModelForm.

[ ] Use Django's built-in PasswordChangeForm from django.contrib.auth.forms.

Views:

[ ] Create profile_view to display user info. Protect with @login_required.

[ ] Create profile_edit_view to handle profile updates (GET displays form, POST processes it). Protect with @login_required.

[ ] Use Django's built-in PasswordChangeView and PasswordChangeDoneView or create simple wrappers. Protect with @login_required.

URLs:

[ ] Add URL pattern for viewing profile (e.g., path('profile/', views.profile_view, name='profile')).

[ ] Add URL pattern for editing profile (e.g., path('profile/edit/', views.profile_edit_view, name='profile_edit')).

[ ] Add URL patterns for password change using PasswordChangeView and PasswordChangeDoneView.

Templates:

[ ] Create profile.html to display user data and links to edit/change password.

[ ] Create profile_edit.html to render the UserProfileUpdateForm.

[ ] Create password_change_form.html (used by PasswordChangeView).

[ ] Create password_change_done.html (used by PasswordChangeDoneView).

Testing:

[ ] Manually view profile.

[ ] Manually edit profile information and verify changes.

[ ] Manually change password (test with correct/incorrect current password) and verify login with new password.

Phase 4: Final Commit (End of Monday)
[ ] Stage all changes: git add .

[ ] Commit completed work: git commit -m "Implement user authentication and profile management"

[ ] (Optional) Push to remote repository: git push
