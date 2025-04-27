Product Requirements Document: User Authentication & Profiles
Version: 1.0
Date: April 27, 2025
Author: Bev

1. Introduction
This document outlines the requirements for the User Authentication and Profile Management module of the SKY Health Check web application. This module is responsible for handling user self-registration (specifically for Engineers as per initial scope), secure login/logout, and basic profile viewing and updating capabilities. This forms a core part of the individual contribution for Coursework 2.

2. Goals
Allow Engineers to securely create their own accounts.

Provide a secure mechanism for registered users to log in and access the application.

Allow users to log out securely.

Enable users to view and update their basic profile information (name, email).

Allow users to change their password securely.

Establish the foundation for user session management within the Django application.

3. Functional Requirements
3.1. Phase 0: Project Setup & Foundation
(Based on agreed setup steps)

Set up the main project directory (sky_health_check).

Initialize and activate a Python virtual environment (venv).

Install Django.

Create the main Django project configuration (config).

Create the primary Django app (health_app).

Integrate the agreed-upon database models into health_app/models.py.

Configure settings.py (add health_app to INSTALLED_APPS, verify database).

Initialize Git repository and configure .gitignore.

Generate and apply initial database migrations based on the agreed models.

Perform the first Git commit and share the repository.

3.2. User Self-Registration (Engineer Focus)
R1.1: Provide a public-facing registration page/form.

R1.2: The form must collect: First Name, Last Name, Username, Email Address, Password, Password Confirmation.

R1.3: Perform basic validation: required fields, valid email format, password complexity (optional but recommended), passwords match.

R1.4: Ensure usernames and email addresses are unique across the system.

R.1.5: Securely hash the password before saving it to the database.

R1.6: Upon successful registration, create a new user record (linked to the appropriate User model defined in models.py).

R1.7: Redirect the user to a success page or the login page after registration.

3.3. User Login
R2.1: Provide a login page/form.

R2.2: The form must collect: Username (or Email) and Password.

R2.3: Authenticate the user against the stored credentials using Django's authentication system.

R2.4: Upon successful login, establish a user session.

R2.5: Redirect the user to their main dashboard or landing page.

R2.6: Display appropriate error messages for invalid credentials without revealing whether the username or password was incorrect.

3.4. User Logout
R3.1: Provide a mechanism (e.g., a button or link) for logged-in users to log out.

R3.2: Terminate the user's session upon logout.

R3.3: Redirect the user to the login page or homepage after logout.

3.5. Profile Management
R4.1: Provide a page accessible only to logged-in users to view their profile.

R4.2: Display the user's current First Name, Last Name, Username, and Email Address.

R4.3: Provide an interface (e.g., an "Edit Profile" page/form) to update First Name and Last Name.

R4.4: Save updated profile information to the database.

R4.5: Provide a separate interface/form for changing the password.

R4.6: Password change form must require the user's current password and a new password (with confirmation).

R4.7: Validate the current password before allowing the change.

R4.8: Securely hash and save the new password.

4. Non-Functional Requirements
NF1: Security: Passwords must be securely hashed. Use Django's built-in authentication and security features (e.g., CSRF protection). Prevent common web vulnerabilities related to authentication.

NF2: Usability: Forms should be clear and provide helpful validation messages. Navigation between login, registration, and profile pages should be intuitive.
