# Sky Health Check

A Django web application for team health checks with user authentication, profile management, and health check voting system.

## Project Overview

Sky Health Check is a web application that allows engineering teams to conduct health checks by voting on various health cards (e.g., Codebase Health, Team Morale). The application includes:

- User registration and authentication
- Profile management
- Dashboard for health check data
- Voting system for health cards

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git

### Setup Instructions

1. **Clone the repository**

```bash
git clone git@github.com:Bev0408/sky_health_check.git
cd sky_health_check
```

2. **Create and activate a virtual environment**

```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install django
```

4. **Apply database migrations**

```bash
python manage.py migrate
```

5. **Run the development server**

```bash
python manage.py runserver
```

6. **Access the application**

Open your browser and navigate to: http://localhost:8000

## Application Structure

The application is organized into the following components:

- **config/**: Django project configuration
- **health_app/**: Main application module
  - **models.py**: Database models
  - **views.py**: View controllers
  - **forms.py**: Form definitions
  - **urls.py**: URL routing
  - **templates/**: HTML templates
  - **templatetags/**: Custom template tags

## Models

The application uses the following primary models:

- **User**: Django's built-in user model
- **Profile**: Extends User with role and team information
- **Department**: Represents departments in the organization
- **Team**: Represents teams within departments
- **Session**: Represents a health check session period
- **HealthCard**: Represents a health check category/area
- **Vote**: Represents a user's vote for a specific card in a session

## Features

- **User Authentication**
  - Registration (sign up)
  - Login/logout
  - Password change

- **Profile Management**
  - View profile information
  - Edit profile details
  - Change password

- **Health Check Functionality** (To be implemented)
  - View health cards
  - Submit votes
  - View results
  
## Contribution Workflow

1. **Get the latest changes**

```bash
git pull origin master
```

2. **Create a new branch for your feature**

```bash
git checkout -b feature-name
```

3. **Make your changes and commit them**

```bash
git add .
git commit -m "Description of changes"
```

4. **Push your branch to GitHub**

```bash
git push origin feature-name
```

5. **Create a Pull Request on GitHub**

Navigate to the repository on GitHub and create a pull request from your feature branch to master.

## Testing

To run tests:

```bash
python manage.py test
```

## Development Environments

The project supports three environments:
- Development (default)
- Test
- Production

## Useful Django Commands

- **Create a superuser** (admin account)
```bash
python manage.py createsuperuser
```

- **Make migrations after model changes**
```bash
python manage.py makemigrations
```

- **Shell access for testing**
```bash 
python manage.py shell
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
