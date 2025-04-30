# Quick Start Guide

This guide provides step-by-step instructions to get the Team Health Check application running on your local machine.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database server
- Git (optional, for cloning)

## Setup Steps

### 1. Install Required Software

- **Python**: Download and install from [python.org](https://www.python.org/downloads/)
- **PostgreSQL**: Download and install from [postgresql.org](https://www.postgresql.org/download/)

### 2. Get the Code

Either clone the repository:

```bash
git clone https://github.com/yourusername/team-health-check.git
cd team-health-check
```

Or download and extract the ZIP file from the repository.

### 3. Set Up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements_local.txt
```

### 5. Create a PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create a database
CREATE DATABASE health_check_db;

# Create a user (optional)
CREATE USER health_app WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE health_check_db TO health_app;

# Exit PostgreSQL
\q
```

### 6. Configure Environment Variables

Create a `.env` file in the project root with:

```
FLASK_APP=main.py
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:password@localhost:5432/health_check_db
SESSION_SECRET=your_random_secret_key
```

Adjust the DATABASE_URL as needed for your PostgreSQL setup.

### 7. Initialize and Seed the Database

```bash
# Create tables
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()

# Add initial data
python seed_data.py

# Add health check categories and questions
python add_health_checks.py

# (Optional) Add test data
python generate_test_data.py
```

### 8. Run the Application

```bash
flask run
```

### 9. Access the Application

Open your browser and go to: [http://localhost:5000](http://localhost:5000)

### 10. Login with Default Credentials

- **Administrator**:
  - Username: `admin`
  - Password: `admin123`

- **Regular User**:
  - Username: `user1`
  - Password: `password123`

## Troubleshooting

- **Database Connection Issues**: Verify your PostgreSQL server is running and the DATABASE_URL is correct.
- **Module Import Errors**: Ensure your virtual environment is activated.
- **Missing Tables**: Run `db.create_all()` in the Flask shell if tables are missing.

## Next Steps

After setting up, explore:

1. Creating departments and teams
2. Adding users with different roles
3. Creating health check sessions
4. Submitting responses
5. Viewing reports and visualizations