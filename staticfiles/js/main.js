document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Initialize team selection
  const teamSelect = document.getElementById('team');
  if (teamSelect) {
    teamSelect.addEventListener('change', function() {
      loadTeamMembers(teamSelect.value);
    });
    
    // Load team members for initial team (if selected)
    if (teamSelect.value) {
      loadTeamMembers(teamSelect.value);
    }
  }
  
  // Add event listener for status dropdown in health checks
  document.querySelectorAll('.status-select-dropdown').forEach(dropdown => {
    dropdown.addEventListener('change', function() {
      const statusClass = this.value;
      const card = this.closest('.health-check-card');
      
      // Remove existing status classes
      card.classList.remove('border-danger', 'border-warning', 'border-success');
      
      // Add the new status class
      if (statusClass === 'needs_attention') {
        card.classList.add('border-danger');
      } else if (statusClass === 'room_for_improvement') {
        card.classList.add('border-warning');
      } else if (statusClass === 'doing_well') {
        card.classList.add('border-success');
      }
    });
  });
  
  // Toggle comment sections
  document.querySelectorAll('.toggle-comments').forEach(toggle => {
    toggle.addEventListener('click', function() {
      const commentSection = this.nextElementSibling;
      if (commentSection.style.display === 'none') {
        commentSection.style.display = 'block';
        this.textContent = 'Hide Comments';
      } else {
        commentSection.style.display = 'none';
        this.textContent = 'Show Comments';
      }
    });
  });

  // Initialize date pickers
  const datePickers = document.querySelectorAll('.datepicker');
  if (datePickers.length > 0) {
    datePickers.forEach(picker => {
      // Using bootstrap-datepicker if available, otherwise use browser default
      if (typeof $.fn.datepicker !== 'undefined') {
        $(picker).datepicker({
          format: 'yyyy-mm-dd',
          autoclose: true
        });
      }
    });
  }
  
  // Handle select all checkboxes for team members
  const selectAllButton = document.getElementById('select-all-members');
  if (selectAllButton) {
    selectAllButton.addEventListener('click', function() {
      const checkboxes = document.querySelectorAll('.member-checkbox');
      checkboxes.forEach(checkbox => {
        checkbox.checked = true;
      });
      
      // Update the counter
      updateSelectedCount();
    });
  }
  
  // Setup member checkboxes to update the counter
  const memberCheckboxes = document.querySelectorAll('.member-checkbox');
  if (memberCheckboxes.length > 0) {
    memberCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        updateSelectedCount();
      });
    });
    
    // Initial count
    updateSelectedCount();
  }
  
  // Handle "Save Responses" button in health check voting
  const saveResponsesBtn = document.getElementById('save-responses-btn');
  if (saveResponsesBtn) {
    saveResponsesBtn.addEventListener('click', function() {
      // Check if all questions have been answered
      const unansweredQuestions = document.querySelectorAll('.question-card:not(.answered)');
      if (unansweredQuestions.length > 0) {
        if (!confirm('You have ' + unansweredQuestions.length + ' unanswered questions. Do you want to continue anyway?')) {
          return;
        }
      }
      
      // Submit the form
      document.getElementById('health-check-form').submit();
    });
  }
  
  // Status selection in health check voting
  document.querySelectorAll('.status-radio').forEach(radio => {
    radio.addEventListener('change', function() {
      const questionCard = this.closest('.question-card');
      questionCard.classList.add('answered');
      
      // Add a visual indicator that the question has been answered
      const statusValue = this.value;
      questionCard.classList.remove('status-needs-attention', 'status-room-for-improvement', 'status-doing-well');
      
      switch (statusValue) {
        case 'needs_attention':
          questionCard.classList.add('status-needs-attention');
          break;
        case 'room_for_improvement':
          questionCard.classList.add('status-room-for-improvement');
          break;
        case 'doing_well':
          questionCard.classList.add('status-doing-well');
          break;
      }
    });
  });
  
  // Confirmation for delete actions
  document.querySelectorAll('.confirm-delete').forEach(button => {
    button.addEventListener('click', function(e) {
      if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });
});

// Function to load team members via AJAX
function loadTeamMembers(teamId) {
  if (!teamId) return;
  
  const participantsSelect = document.getElementById('participants');
  if (!participantsSelect) return;
  
  // Clear existing options
  participantsSelect.innerHTML = '';
  
  // Show loading indicator
  const loadingOption = document.createElement('option');
  loadingOption.textContent = 'Loading team members...';
  participantsSelect.appendChild(loadingOption);
  
  // Fetch team members
  fetch('/api/teams/' + teamId + '/members')
    .then(response => response.json())
    .then(members => {
      // Clear loading indicator
      participantsSelect.innerHTML = '';
      
      // Add members as options
      members.forEach(member => {
        const option = document.createElement('option');
        option.value = member.id;
        option.textContent = `${member.name || member.username}`;
        if (member.role === 'team_leader') {
          option.textContent += ' (Team Leader)';
        }
        participantsSelect.appendChild(option);
        option.selected = true; // Select all by default
      });
      
      // Update the selected count
      updateSelectedCount();
    })
    .catch(error => {
      console.error('Error loading team members:', error);
      participantsSelect.innerHTML = '<option>Error loading members</option>';
    });
}

// Function to update the selected members count
function updateSelectedCount() {
  const participantsSelect = document.getElementById('participants');
  const countElement = document.getElementById('selected-count');
  
  if (participantsSelect && countElement) {
    const selectedCount = Array.from(participantsSelect.options).filter(option => option.selected).length;
    const totalCount = participantsSelect.options.length;
    countElement.textContent = selectedCount + ' of ' + totalCount + ' selected';
  }
}

// Function to toggle status dropdown visibility
function toggleStatusDropdown(buttonElement) {
  const dropdownMenu = buttonElement.nextElementSibling;
  dropdownMenu.classList.toggle('show');
}

// Function to select a status from dropdown
function selectStatus(buttonElement, statusValue, statusText) {
  const card = buttonElement.closest('.question-card');
  const hiddenInput = card.querySelector('input[type="hidden"]');
  const statusButton = card.querySelector('.dropdown-toggle');
  
  // Update hidden input value
  hiddenInput.value = statusValue;
  
  // Update button text
  statusButton.innerHTML = statusText + ' <span class="caret"></span>';
  
  // Update card status
  card.classList.remove('status-needs-attention', 'status-room-for-improvement', 'status-doing-well');
  card.classList.add('status-' + statusValue.replace('_', '-'));
  
  // Mark as answered
  card.classList.add('answered');
  
  // Hide dropdown
  card.querySelector('.dropdown-menu').classList.remove('show');
}
