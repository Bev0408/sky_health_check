import logging
from app import app
from datetime import datetime

from models import User, Department, Team, TeamMember, HealthCheckSession, HealthCheckResponse
from models import HealthCheck, HealthCheckCategory, HealthCheckQuestion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_all_features():
    """Test all major features of the application"""
    logger.info("Starting feature test suite")
    
    with app.app_context():
        # Test database connection and models
        test_database()
        
        # Test user authentication
        test_users()
        
        # Test team and department structure
        test_teams_and_departments()
        
        # Test health check functionality
        test_health_checks()
        
        logger.info("All tests completed")

def test_database():
    """Test database connection and basic models"""
    logger.info("Testing database connection and models...")
    
    # Check if database is accessible
    try:
        user_count = User.query.count()
        logger.info(f"Database connection successful. Found {user_count} users.")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
    
    # Check if all models exist and have data
    models_to_check = [
        (User, "users"),
        (Department, "departments"),
        (Team, "teams"),
        (TeamMember, "team members"),
        (HealthCheck, "health checks"),
        (HealthCheckCategory, "health check categories"),
        (HealthCheckQuestion, "health check questions"),
        (HealthCheckSession, "health check sessions"),
        (HealthCheckResponse, "health check responses")
    ]
    
    for model, name in models_to_check:
        count = model.query.count()
        logger.info(f"Found {count} {name}")
        if count == 0:
            logger.warning(f"No {name} found in database")
    
    return True

def test_users():
    """Test user authentication features"""
    logger.info("Testing user authentication...")
    
    # Check admin user exists
    admin = User.query.filter_by(username="admin").first()
    if admin:
        logger.info(f"Admin user exists: {admin.username} (role: {admin.role})")
    else:
        logger.warning("Admin user not found")
    
    # Check user roles
    roles = ['engineer', 'team_leader', 'department_leader', 'senior_manager', 'admin']
    for role in roles:
        users = User.query.filter_by(role=role).all()
        logger.info(f"Found {len(users)} users with role '{role}'")
    
    # Test password check for admin
    if admin and admin.check_password("admin123"):
        logger.info("Admin password verification successful")
    else:
        logger.warning("Admin password verification failed")
    
    return True

def test_teams_and_departments():
    """Test team and department structure"""
    logger.info("Testing team and department structure...")
    
    # Check departments
    departments = Department.query.all()
    logger.info(f"Found {len(departments)} departments")
    
    # Check teams
    teams = Team.query.all()
    logger.info(f"Found {len(teams)} teams")
    
    # Check team membership
    for team in teams[:5]:  # Check first 5 teams
        members = TeamMember.query.filter_by(team_id=team.id).all()
        leader = next((m for m in members if m.is_leader), None)
        logger.info(f"Team '{team.name}': {len(members)} members, has leader: {leader is not None}")
        
        if leader:
            leader_user = User.query.get(leader.user_id)
            logger.info(f"  Team leader: {leader_user.username} ({leader_user.full_name})")
    
    return True

def test_health_checks():
    """Test health check functionality"""
    logger.info("Testing health check functionality...")
    
    # Check health check categories
    categories = HealthCheckCategory.query.all()
    logger.info(f"Found {len(categories)} health check categories")
    for category in categories:
        questions = HealthCheckQuestion.query.filter_by(category_id=category.id).all()
        logger.info(f"  Category '{category.name}': {len(questions)} questions")
    
    # Check health check sessions
    now = datetime.now()
    active_sessions = HealthCheckSession.query.filter(HealthCheckSession.end_date >= now).all()
    past_sessions = HealthCheckSession.query.filter(HealthCheckSession.end_date < now).all()
    logger.info(f"Found {len(active_sessions)} active health check sessions and {len(past_sessions)} past sessions")
    
    # Check responses
    for session in active_sessions[:3]:  # Check first 3 active sessions
        responses = HealthCheckResponse.query.filter_by(session_id=session.id).all()
        participants = session.participants
        logger.info(f"Health check '{session.health_check.name}' for team '{session.team.name}':")
        logger.info(f"  Participation: {len(set([r.user_id for r in responses]))} of {len(participants)} participants ({session.get_completion_percentage()}%)")
        
        # Group responses by status
        status_counts = {'needs_attention': 0, 'room_for_improvement': 0, 'doing_well': 0}
        for resp in responses:
            status_counts[resp.status] = status_counts.get(resp.status, 0) + 1
        
        logger.info(f"  Response breakdown: ")
        for status, count in status_counts.items():
            percentage = round((count / len(responses)) * 100) if responses else 0
            logger.info(f"    {status}: {count} ({percentage}%)")
    
    return True

if __name__ == "__main__":
    test_all_features()
