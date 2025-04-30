from departments.models import Department

# Create initial departments
departments = [
    {'name': 'Engineering', 'description': 'Software development and engineering department'},
    {'name': 'Marketing', 'description': 'Marketing and communications department'},
    {'name': 'Finance', 'description': 'Finance and accounting department'},
    {'name': 'Human Resources', 'description': 'HR and employee management'},
    {'name': 'Operations', 'description': 'Operations and logistics department'}
]

# Create each department
for dept in departments:
    Department.objects.get_or_create(
        name=dept['name'],
        defaults={'description': dept['description']}
    )
    print(f"Department '{dept['name']}' created or found.")

print("Initial departments created successfully!")
