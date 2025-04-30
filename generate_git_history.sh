#!/bin/bash

# Script to generate GitHub contribution history
# Creates a series of commits from Jan 1, 2025 to today (April 30, 2025)

# Create temporary directory for fake commit history
mkdir -p git_history_generator
cd git_history_generator

# Initialize git repo if not already initialized
if [ ! -d .git ]; then
  git init
  git config user.name "Your Name"
  git config user.email "your.email@example.com"
  echo "# Health Check Project" > README.md
  git add README.md
  git commit -m "Initial commit"
fi

# Define commit messages
declare -a commit_messages=(
  "Initial project setup with Django"
  "Set up database models and relations"
  "Add user authentication system"
  "Create basic templates and views"
  "Implement department management"
  "Add team management functionality"
  "Create health check models"
  "Implement health check templates"
  "Add session creation functionality"
  "Implement response collection"
  "Add dashboard views"
  "Create analytics visualizations"
  "Fix pagination in dashboard"
  "Improve user interface"
  "Add Bootstrap styling"
  "Implement team leader features"
  "Add department leader dashboard"
  "Create admin management panel"
  "Fix session response bugs"
  "Implement health check report exports"
  "Add data visualization charts"
  "Improve mobile responsiveness"
  "Refactor health check models"
  "Add automated testing"
  "Fix database migration issues"
  "Improve search functionality"
  "Add user profile features"
  "Implement session history"
  "Add trend analysis in analytics"
  "Fix permission issues"
  "Final deployment preparations"
)

# Define date range (Jan 1, 2025 to today)
start_date="2025-01-01"
end_date=$(date +%Y-%m-%d)

# Convert dates to timestamps
start_ts=$(date -j -f "%Y-%m-%d" "$start_date" "+%s")
end_ts=$(date -j -f "%Y-%m-%d" "$end_date" "+%s")

# Calculate time interval for distributing commits
total_seconds=$((end_ts - start_ts))
total_commits=${#commit_messages[@]}
interval=$((total_seconds / total_commits))

echo "Generating $total_commits commits from $start_date to $end_date..."

# Loop through and create commits with specified dates
for (( i=0; i<${#commit_messages[@]}; i++ )); do
  # Calculate commit timestamp
  commit_ts=$((start_ts + (i * interval)))
  
  # Format date for commit
  commit_date=$(date -j -f "%s" "$commit_ts" "+%Y-%m-%d %H:%M:%S")
  
  # Create a file change
  file_name="file_${i}.txt"
  echo "Update for commit $i on $(date -j -f "%s" "$commit_ts" "+%Y-%m-%d")" > "$file_name"
  
  # Add and commit with specific date
  git add "$file_name"
  
  # Use GIT_AUTHOR_DATE and GIT_COMMITTER_DATE to set the date
  export GIT_AUTHOR_DATE="$commit_date"
  export GIT_COMMITTER_DATE="$commit_date"
  
  git commit -m "${commit_messages[i]}"
  
  echo "Created commit: ${commit_messages[i]} with date $commit_date"
done

echo ""
echo "All commits generated successfully!"
echo "To push these commits to GitHub, create a new repo and run:"
echo "git remote add origin <your-github-repo-url>"
echo "git push -u origin main"
echo ""
echo "Note: This has created a local repository in ./git_history_generator"
echo "You may want to connect it to your actual project repository before pushing."