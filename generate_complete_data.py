"""
ALL-IN-ONE COMPLETE DATA GENERATION SCRIPT

This script creates ALL data needed for the health check application in one file:
- Departments (multiple)
- Users with all roles (admin, senior manager, department leader, team leader, engineer)
- Teams with members
- Health check categories and questions
- Health check templates
- Health check sessions with responses for all teams
- Historical data for analytics

USAGE:
- Simply run: python generate_complete_data.py
- Admin login: Username: admin, Password: admin123
"""

import os
import sys
import random
import datetime
from django.core.wsgi import get_wsgi_application

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_check_project.settings')
application = get_wsgi_application()

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db.models import Count
from accounts.models import User
from departments.models import Department
from teams.models import Team, TeamMember
from health_checks.models import (
    HealthCheckCategory, HealthCheckQuestion, 
    HealthCheck, HealthCheckSession, 
    HealthCheckResponse
)

# Configuration - adjust these values to generate more or less data
NUM_DEPARTMENTS = 10  # Number of departments
USERS_PER_ROLE = {
    'admin': 3,
    'senior_manager': 5,
    'department_leader': 10,
    'team_leader': 20, 
    'engineer': 100
}
TEAMS_PER_DEPARTMENT = 3  # Teams per department
ENGINEERS_PER_TEAM = 6  # Engineers per team
SESSIONS_PER_TEAM = 12  # Health check sessions per team
HISTORY_MONTHS = 6  # How many months of historical data

# Initialize log file
log_file = open("data_generation.log", "w")
def log(message):
    """Print to both console and file for logging"""
    print(message)
    log_file.write(message + "\n")
    log_file.flush()

@transaction.atomic
def create_admin_users():
    """Create admin users"""
    log("CREATING ADMIN USERS")
    
    admin_users = []
    # Ensure the primary admin exists
    try:
        admin = User.objects.get(username='admin')
        log(f"Using existing admin user: {admin.username}")
        
        # Update admin permissions to ensure they are correct
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.set_password('admin123')  # Reset admin password
        admin.save()
        log("Admin permissions and password updated")
        
        admin_users.append(admin)
    except User.DoesNotExist:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            full_name='Administrator',
            role=User.ADMIN
        )
        log(f"Created admin user: {admin.username}")
        admin_users.append(admin)
    
    # Create additional admin users
    for i in range(1, USERS_PER_ROLE['admin']):
        admin_name = f"admin{i}"
        try:
            admin_user = User.objects.get(username=admin_name)
            log(f"Using existing admin user: {admin_user.username}")
        except User.DoesNotExist:
            admin_user = User.objects.create_superuser(
                username=admin_name,
                email=f"{admin_name}@example.com",
                password='admin123',
                full_name=f"Administrator {i}",
                role=User.ADMIN
            )
            log(f"Created additional admin user: {admin_user.username}")
        admin_users.append(admin_user)
    
    log(f"Total admin users: {len(admin_users)}")
    return admin_users

@transaction.atomic
def create_departments():
    """Create departments"""
    log("\nCREATING DEPARTMENTS")
    
    departments = []
    # Core departments that should always exist
    core_department_names = [
        "Engineering", "Product Development", "Quality Assurance", 
        "DevOps", "Design", "Research", "Data Science", 
        "Customer Support", "Marketing", "Finance"
    ]
    
    # Additional department names for more variety
    additional_department_names = [
        "Human Resources", "Operations", "Sales", "Legal", 
        "Business Development", "Strategic Planning", "IT Infrastructure",
        "Mobile Development", "Web Development", "Analytics",
        "Machine Learning", "AI", "Cybersecurity",
        "Cloud Services", "Enterprise Solutions", "Backend Development",
        "Frontend Development", "Embedded Systems", "Blockchain",
        "AR/VR Development", "Network Operations", "Technical Support"
    ]
    
    # Combined list, using as many as needed
    all_department_names = core_department_names + additional_department_names
    department_names_to_use = all_department_names[:NUM_DEPARTMENTS]
    
    # Create each department
    for i, name in enumerate(department_names_to_use):
        dept, created = Department.objects.get_or_create(
            name=name,
            defaults={
                "description": f"The {name} department handles all {name.lower()}-related activities and initiatives across the organization.",
                "created_at": timezone.now() - datetime.timedelta(days=random.randint(100, 500))
            }
        )
        if created:
            log(f"Created department: {dept.name}")
        else:
            log(f"Using existing department: {dept.name}")
        departments.append(dept)
    
    log(f"Total departments: {len(departments)}")
    return departments

@transaction.atomic
def create_users_for_departments(departments):
    """Create users with different roles for all departments"""
    log("\nCREATING USERS FOR DEPARTMENTS")
    
    senior_managers = []
    department_leaders = []
    team_leaders = []
    engineers = []
    
    # Create senior managers (not assigned to departments)
    for i in range(USERS_PER_ROLE['senior_manager']):
        sm_name = f"seniormanager{i+1}"
        try:
            sm = User.objects.get(username=sm_name)
            log(f"Using existing senior manager: {sm.username}")
        except User.DoesNotExist:
            sm = User.objects.create_user(
                username=sm_name,
                email=f"{sm_name}@example.com",
                password='password123',
                full_name=f"Senior Manager {i+1}",
                role=User.SENIOR_MANAGER
            )
            log(f"Created senior manager: {sm.username}")
        senior_managers.append(sm)
    
    # For each department, create department leaders
    dept_leader_count = 0
    for dept in departments:
        # Determine how many leaders for this department (1-2)
        num_leaders = min(2, (USERS_PER_ROLE['department_leader'] // len(departments)) + 1)
        
        for i in range(num_leaders):
            if dept_leader_count >= USERS_PER_ROLE['department_leader']:
                break
                
            dl_name = f"deptlead_{dept.name.lower().replace(' ', '')}_{i+1}"
            try:
                dept_leader = User.objects.get(username=dl_name)
                log(f"Using existing department leader: {dept_leader.username}")
            except User.DoesNotExist:
                dept_leader = User.objects.create_user(
                    username=dl_name,
                    email=f"{dl_name}@example.com",
                    password='password123',
                    full_name=f"{dept.name} Department Leader {i+1}",
                    department=dept,
                    role=User.DEPARTMENT_LEADER
                )
                log(f"Created department leader: {dept_leader.username} for {dept.name}")
            department_leaders.append(dept_leader)
            dept_leader_count += 1
    
    # Create team leaders (will be assigned to teams later)
    for i in range(USERS_PER_ROLE['team_leader']):
        dept = random.choice(departments)
        tl_name = f"teamlead_{i+1}"
        try:
            team_leader = User.objects.get(username=tl_name)
            log(f"Using existing team leader: {team_leader.username}")
        except User.DoesNotExist:
            team_leader = User.objects.create_user(
                username=tl_name,
                email=f"{tl_name}@example.com",
                password='password123',
                full_name=f"Team Leader {i+1}",
                department=dept,
                role=User.TEAM_LEADER
            )
            log(f"Created team leader: {team_leader.username}")
        team_leaders.append(team_leader)
    
    # Create engineers (will be assigned to teams later)
    for i in range(USERS_PER_ROLE['engineer']):
        dept = random.choice(departments)
        eng_name = f"engineer{i+1}"
        try:
            engineer = User.objects.get(username=eng_name)
            log(f"Using existing engineer: {engineer.username}")
        except User.DoesNotExist:
            engineer = User.objects.create_user(
                username=eng_name,
                email=f"{eng_name}@example.com",
                password='password123',
                full_name=f"Engineer {i+1}",
                department=dept,
                role=User.ENGINEER
            )
            log(f"Created engineer: {engineer.username}")
        engineers.append(engineer)
    
    log(f"Created users - Senior Managers: {len(senior_managers)}, Department Leaders: {len(department_leaders)}, Team Leaders: {len(team_leaders)}, Engineers: {len(engineers)}")
    return senior_managers, department_leaders, team_leaders, engineers

@transaction.atomic
def create_teams_and_assign_members(departments, team_leaders, engineers):
    """Create teams for departments and assign members"""
    log("\nCREATING TEAMS AND ASSIGNING MEMBERS")
    
    teams = []
    assigned_team_leaders = []
    assigned_engineers = []
    
    # Create teams for each department
    for dept in departments:
        for i in range(1, TEAMS_PER_DEPARTMENT + 1):
            team_name = f"{dept.name} Team {i}"
            team, created = Team.objects.get_or_create(
                name=team_name,
                defaults={
                    "description": f"Team {i} within the {dept.name} department, focused on key initiatives and projects.",
                    "department": dept,
                    "created_at": timezone.now() - datetime.timedelta(days=random.randint(30, 300))
                }
            )
            if created:
                log(f"Created team: {team.name}")
            else:
                log(f"Using existing team: {team.name}")
            teams.append(team)
            
            # Assign a team leader if available
            available_leaders = [tl for tl in team_leaders if tl not in assigned_team_leaders and tl.department == dept]
            if not available_leaders:
                available_leaders = [tl for tl in team_leaders if tl not in assigned_team_leaders]
            
            if available_leaders:
                team_leader = random.choice(available_leaders)
                assigned_team_leaders.append(team_leader)
                
                # Add team leader as member
                TeamMember.objects.get_or_create(
                    team=team,
                    user=team_leader,
                    defaults={
                        "is_leader": True,
                        "joined_at": timezone.now() - datetime.timedelta(days=random.randint(30, 250))
                    }
                )
                log(f"Assigned {team_leader.username} as leader of {team.name}")
            
            # Assign engineers
            team_size = min(ENGINEERS_PER_TEAM, len(engineers) - len(assigned_engineers))
            if team_size <= 0:
                log(f"Warning: Not enough engineers left to assign to {team.name}")
                continue
                
            # Prefer engineers from same department
            dept_engineers = [eng for eng in engineers if eng not in assigned_engineers and eng.department == dept]
            other_engineers = [eng for eng in engineers if eng not in assigned_engineers and eng not in dept_engineers]
            
            # Use department engineers first, then others
            available_engineers = dept_engineers + other_engineers
            team_engineers = available_engineers[:team_size]
            
            for engineer in team_engineers:
                assigned_engineers.append(engineer)
                
                # Add engineer to team
                TeamMember.objects.get_or_create(
                    team=team,
                    user=engineer,
                    defaults={
                        "is_leader": False,
                        "joined_at": timezone.now() - datetime.timedelta(days=random.randint(1, 200))
                    }
                )
                log(f"Added {engineer.username} to {team.name}")
    
    log(f"Total teams created: {len(teams)}")
    log(f"Team leaders assigned: {len(assigned_team_leaders)}")
    log(f"Engineers assigned: {len(assigned_engineers)}")
    return teams

@transaction.atomic
def create_health_check_categories_and_questions():
    """Create or verify health check categories and questions"""
    log("\nCREATING HEALTH CHECK CATEGORIES AND QUESTIONS")
    
    categories = []
    # Spotify Health Check model categories and questions
    spotify_categories = [
        {
            "name": "Delivering Value",
            "description": "How efficiently the team delivers value to customers",
            "questions": [
                "We deliver great stuff! We're proud of it and our stakeholders are really happy.",
                "We deliver value regularly, at a sustainable pace.",
                "We have a clear understanding of the value we deliver.",
                "We monitor key metrics to track the value we deliver.",
                "We regularly reflect on how we can deliver more value."
            ]
        },
        {
            "name": "Easy to Release",
            "description": "How easily the team can release their changes",
            "questions": [
                "Releasing is simple, safe, painless and mostly automated.",
                "We can easily roll back and deploy a previous version if needed.",
                "We have a clear release process that all team members understand.",
                "Our CI/CD pipeline is well-maintained and reliable.",
                "We release small, incremental changes frequently."
            ]
        },
        {
            "name": "Fun",
            "description": "How much fun the team has working together",
            "questions": [
                "We love going to work and have great fun working together!",
                "Our team has a positive and supportive atmosphere.",
                "We celebrate our successes together.",
                "We organize team activities and social events regularly.",
                "We maintain a healthy work-life balance."
            ]
        },
        {
            "name": "Health of Codebase",
            "description": "The technical health of the codebase",
            "questions": [
                "Our code is clean, well-structured and maintainable.",
                "We're proud of the quality of our code! It's clear, concise and tested.",
                "We have good test coverage and confidence in our test suite.",
                "We follow consistent coding standards and best practices.",
                "Technical debt is managed well and doesn't hinder development."
            ]
        },
        {
            "name": "Learning",
            "description": "How the team learns and grows together",
            "questions": [
                "We're learning lots all the time!",
                "We actively share knowledge within the team.",
                "We have dedicated time for learning and exploration.",
                "We experiment with new technologies and approaches.",
                "We conduct regular retrospectives and implement improvements."
            ]
        },
        {
            "name": "Mission",
            "description": "The clarity and alignment of the team's mission",
            "questions": [
                "We know exactly why we are here, and we're really excited about it!",
                "Everyone on the team understands our mission and goals.",
                "Our mission is aligned with the organization's objectives.",
                "We regularly revisit and refine our mission.",
                "Our work directly contributes to our mission."
            ]
        },
        {
            "name": "Pawns or Players",
            "description": "How much control the team has over their destiny",
            "questions": [
                "We are in control of our own destiny! We decide what to build, how to build it, and when to release it.",
                "We have autonomy to make technical decisions.",
                "We have influence over product priorities and roadmap.",
                "We feel empowered to suggest and implement improvements.",
                "Management trusts our decisions and supports us."
            ]
        },
        {
            "name": "Speed",
            "description": "How quickly the team can deliver",
            "questions": [
                "We get stuff done really quickly! No waiting, no delays.",
                "Our development process has minimal bottlenecks.",
                "We can quickly respond to changing requirements.",
                "Our team structure and roles enable efficient work.",
                "We continuously look for ways to increase our velocity."
            ]
        },
        {
            "name": "Suitable Process",
            "description": "How suitable the development process is",
            "questions": [
                "Our way of working is effective and fits us perfectly!",
                "Our process adapts to the team's changing needs.",
                "Everyone understands and follows our process.",
                "Our process focuses on delivering value, not just following rules.",
                "We regularly review and improve our process."
            ]
        },
        {
            "name": "Support",
            "description": "How well the team is supported",
            "questions": [
                "We always get great support and help when we ask for it!",
                "We have the tools and resources we need to do our job effectively.",
                "Management addresses our concerns and roadblocks quickly.",
                "We have access to the necessary expertise when needed.",
                "Cross-team dependencies are managed effectively."
            ]
        },
        {
            "name": "Teamwork",
            "description": "How well the team works together",
            "questions": [
                "We are a cohesive team! We trust each other and can depend upon each other.",
                "Team members help each other and share the workload.",
                "We communicate effectively and openly.",
                "We provide constructive feedback to each other.",
                "We have strong collaboration across different roles."
            ]
        }
    ]
    
    # Create all categories and questions
    for i, category_data in enumerate(spotify_categories):
        category, created = HealthCheckCategory.objects.get_or_create(
            name=category_data["name"],
            defaults={
                "description": category_data["description"],
                "order": i
            }
        )
        
        if created:
            log(f"Created category: {category.name}")
        else:
            log(f"Using existing category: {category.name}")
        
        categories.append(category)
        
        # Create questions for this category
        for j, question_text in enumerate(category_data["questions"]):
            question, created = HealthCheckQuestion.objects.get_or_create(
                text=question_text,
                defaults={
                    "category": category,
                    "detail": f"Detailed explanation: {question_text}",
                    "order": j
                }
            )
            
            if created:
                log(f"Created question: {question.text[:50]}...")
    
    log(f"Total categories: {len(categories)} with {HealthCheckQuestion.objects.count()} questions")
    return categories

@transaction.atomic
def create_health_check_templates(admin_users, categories):
    """Create health check templates"""
    log("\nCREATING HEALTH CHECK TEMPLATES")
    
    templates = []
    
    # Standard templates for all teams
    standard_templates = [
        {
            "name": "Agile Team Health Check",
            "description": "A comprehensive health check for agile software development teams"
        },
        {
            "name": "DevOps Team Assessment",
            "description": "Assessment focused on DevOps practices and culture"
        },
        {
            "name": "Cross-functional Team Evaluation",
            "description": "Evaluation for cross-functional product teams"
        },
        {
            "name": "Software Development Team Health",
            "description": "Health check for software development teams"
        },
        {
            "name": "Product Team Health Check",
            "description": "Health check for product development teams"
        },
        {
            "name": "Quarterly Team Assessment",
            "description": "Standard quarterly assessment for all teams"
        },
        {
            "name": "Monthly Team Health Check",
            "description": "Monthly check-in on team health indicators"
        }
    ]
    
    # Create standard templates
    for template_info in standard_templates:
        template, created = HealthCheck.objects.get_or_create(
            name=template_info["name"],
            defaults={
                "description": template_info["description"],
                "created_by": random.choice(admin_users),
                "created_at": timezone.now() - datetime.timedelta(days=random.randint(60, 300)),
                "is_template": True
            }
        )
        
        if created:
            log(f"Created template: {template.name}")
        else:
            log(f"Using existing template: {template.name}")
        
        templates.append(template)
    
    # Create department-specific templates
    departments = Department.objects.all()
    for dept in departments:
        template_name = f"{dept.name} Department Health Check"
        template, created = HealthCheck.objects.get_or_create(
            name=template_name,
            defaults={
                "description": f"Health check template specifically for {dept.name} teams",
                "created_by": random.choice(admin_users),
                "created_at": timezone.now() - datetime.timedelta(days=random.randint(30, 120)),
                "is_template": True
            }
        )
        
        if created:
            log(f"Created department-specific template: {template.name}")
        else:
            log(f"Using existing department-specific template: {template.name}")
        
        templates.append(template)
    
    log(f"Total templates: {len(templates)}")
    return templates

@transaction.atomic
def create_health_check_sessions(templates, teams):
    """Create health check sessions and responses"""
    log("\nCREATING HEALTH CHECK SESSIONS WITH RESPONSES")
    
    # Get all questions
    questions = list(HealthCheckQuestion.objects.all())
    if not questions:
        log("ERROR: No questions found! Cannot create sessions.")
        return
    log(f"Found {len(questions)} questions for health checks")
    
    # Generate session dates for historical data
    today = timezone.now().date()
    session_dates = []
    current_date = today - datetime.timedelta(days=30 * HISTORY_MONTHS)  # Start X months ago
    
    # Create weekly dates
    while current_date <= today:
        session_dates.append(current_date)
        current_date += datetime.timedelta(days=7)  # Weekly dates
    
    log(f"Planning to create sessions for {len(session_dates)} dates ({HISTORY_MONTHS} months of history)")
    
    sessions_created = 0
    responses_created = 0
    
    # Get response comments for variety
    needs_attention_comments = [
        "This is a significant problem area for us.",
        "We need to address this urgently.",
        "This has been a consistent issue that needs attention.",
        "I'm concerned about our performance in this area.",
        "We've been struggling with this for some time.",
        "There are critical gaps that need to be addressed.",
        "This is a bottleneck for our team.",
        "We need a complete revamp of our approach here.",
        "There are serious deficiencies in this area."
    ]
    
    improvement_comments = [
        "We're making progress, but still have work to do.",
        "This is improving, but isn't where it needs to be yet.",
        "We've made some good changes, but more is needed.",
        "There's been inconsistent improvement in this area.",
        "Some aspects work well, others need attention.",
        "We've addressed some issues, but new ones have emerged.",
        "Progress is slower than expected in this area."
    ]
    
    doing_well_comments = [
        "This is one of our strongest areas!",
        "The whole team excels in this aspect.",
        "We've made significant progress here recently.",
        "Our approach to this is working very effectively.",
        "This has been a focus area and the results show.",
        "We consistently perform well on this dimension.",
        "The team takes pride in how we handle this."
    ]
    
    # Process teams in batches to avoid memory issues
    batch_size = 5
    team_batches = [teams[i:i+batch_size] for i in range(0, len(teams), batch_size)]
    
    for batch_idx, team_batch in enumerate(team_batches):
        log(f"Processing team batch {batch_idx+1}/{len(team_batches)} ({len(team_batch)} teams)")
        
        # For each team in this batch
        for team in team_batch:
            # Get team members
            team_members = list(TeamMember.objects.filter(team=team))
            if not team_members:
                log(f"No members found for {team.name}, skipping")
                continue
            
            # Get team leader
            team_leader = None
            for member in team_members:
                if member.is_leader:
                    team_leader = member.user
                    break
            
            if not team_leader and team_members:
                team_leader = team_members[0].user
            
            # Choose templates to use for this team (1-2 templates)
            available_templates = random.sample(templates, min(2, len(templates)))
            
            # For each template, create sessions on some of the dates
            for template in available_templates:
                # Skip some dates randomly (40% chance)
                skip_probability = random.uniform(0.4, 0.6)
                
                team_session_dates = [date for date in session_dates if random.random() > skip_probability]
                log(f"Creating {len(team_session_dates)} sessions for team {team.name} with template {template.name}")
                
                for session_idx, session_date in enumerate(team_session_dates):
                    # Convert to datetime for session creation
                    start_datetime = timezone.make_aware(datetime.datetime.combine(session_date, datetime.time()))
                    end_datetime = start_datetime + datetime.timedelta(days=7)  # Sessions last 1 week
                    
                    # Create session
                    try:
                        session = HealthCheckSession.objects.create(
                            health_check=template,
                            team=team,
                            start_date=start_datetime,
                            end_date=end_datetime,
                            anonymous=True,
                            created_by=team_leader,
                            created_at=start_datetime
                        )
                        
                        sessions_created += 1
                        
                        # Add all team members as participants
                        for member in team_members:
                            session.participants.add(member.user)
                        
                        # Add responses - more recent sessions have higher completion rate
                        days_since_session = (today - session_date).days
                        days_since_relative = days_since_session / (30 * HISTORY_MONTHS)  # Normalize to 0-1
                        completion_rate = 0.6 + (1 - days_since_relative) * 0.4  # Newer sessions have higher completion
                        
                        # Special case: make some recent sessions incomplete
                        if days_since_session < 7 and random.random() < 0.3:
                            completion_rate *= random.uniform(0.1, 0.5)  # Recent but incomplete session
                        
                        # For each team member, add responses with the determined completion rate
                        for member in team_members:
                            # Skip some members randomly based on completion rate
                            if random.random() > completion_rate:
                                continue
                            
                            for question in questions:
                                # For incomplete sessions, skip some questions randomly
                                if completion_rate < 0.9 and random.random() > 0.9:
                                    continue
                                
                                # Weight responses - more positive for newer dates
                                recency_factor = 1 - days_since_relative  # 1 for newest, 0 for oldest
                                
                                # Team performance improves over time
                                positivity_bias = 0.3 + recency_factor * 0.4
                                
                                if random.random() < positivity_bias:
                                    status = 'doing_well'
                                    comments = doing_well_comments
                                elif random.random() < 0.5:
                                    status = 'room_for_improvement'
                                    comments = improvement_comments
                                else:
                                    status = 'needs_attention'
                                    comments = needs_attention_comments
                                
                                # Add comment for some responses (40% chance)
                                comment = ""
                                if random.random() < 0.4:
                                    comment = random.choice(comments)
                                
                                # Create response
                                HealthCheckResponse.objects.create(
                                    session=session,
                                    question=question,
                                    user=member.user,
                                    status=status,
                                    comment=comment,
                                    created_at=start_datetime + datetime.timedelta(hours=random.randint(1, 72))
                                )
                                
                                responses_created += 1
                        
                    except Exception as e:
                        log(f"Error creating session: {str(e)}")
            
        # Log progress after each team batch
        log(f"Progress: Created {sessions_created} sessions with {responses_created} responses")
    
    log(f"Completed! Created {sessions_created} health check sessions with {responses_created} responses")
    return sessions_created, responses_created

def main():
    """Main function to generate all test data"""
    start_time = datetime.datetime.now()
    log(f"Starting complete data generation at {start_time}")
    
    try:
        # Step 1: Create admin users
        admin_users = create_admin_users()
        
        # Step 2: Create departments
        departments = create_departments()
        
        # Step 3: Create users for departments (all roles)
        senior_managers, department_leaders, team_leaders, engineers = create_users_for_departments(departments)
        
        # Step 4: Create teams and assign members
        teams = create_teams_and_assign_members(departments, team_leaders, engineers)
        
        # Step 5: Create/verify health check categories and questions
        categories = create_health_check_categories_and_questions()
        
        # Step 6: Create health check templates
        templates = create_health_check_templates(admin_users, categories)
        
        # Step 7: Create health check sessions and responses
        sessions_created, responses_created = create_health_check_sessions(templates, teams)
        
        # Done!
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        log(f"\nData generation completed successfully in {duration}!")
        
        log("\n------ FINAL STATISTICS ------")
        log(f"Departments: {Department.objects.count()}")
        log(f"Users by role:")
        log(f"  - Admins: {User.objects.filter(role=User.ADMIN).count()}")
        log(f"  - Senior Managers: {User.objects.filter(role=User.SENIOR_MANAGER).count()}")
        log(f"  - Department Leaders: {User.objects.filter(role=User.DEPARTMENT_LEADER).count()}")
        log(f"  - Team Leaders: {User.objects.filter(role=User.TEAM_LEADER).count()}")
        log(f"  - Engineers: {User.objects.filter(role=User.ENGINEER).count()}")
        log(f"  - Total Users: {User.objects.count()}")
        log(f"Teams: {Team.objects.count()}")
        log(f"Team Members: {TeamMember.objects.count()}")
        log(f"Health Check Categories: {HealthCheckCategory.objects.count()}")
        log(f"Health Check Questions: {HealthCheckQuestion.objects.count()}")
        log(f"Health Check Templates: {HealthCheck.objects.filter(is_template=True).count()}")
        log(f"Health Check Sessions: {HealthCheckSession.objects.count()}")
        log(f"Health Check Responses: {HealthCheckResponse.objects.count()}")
        
        log("\n------ ADMIN LOGIN INFORMATION ------")
        log("To access the admin panel:")
        log("1. Go to /admin in your browser")
        log("2. Use the following credentials:")
        log("   Username: admin")
        log("   Password: admin123")
        
    except Exception as e:
        log(f"ERROR in data generation: {str(e)}")
        import traceback
        log(traceback.format_exc())
    finally:
        # Close log file
        log_file.close()

if __name__ == "__main__":
    main()