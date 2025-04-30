"""
This file is maintained for compatibility with the existing workflow.
It's a simple wrapper around the Django WSGI application.
"""
from health_check_project.wsgi import application

app = application