document.addEventListener('DOMContentLoaded', function() {
  // Status option selection in health check voting
  document.querySelectorAll('.status-option').forEach(option => {
    option.addEventListener('click', function() {
      // First, remove the active class from all options in this question group
      const questionCard = this.closest('.question-card');
      questionCard.querySelectorAll('.status-option').forEach(opt => {
        opt.classList.remove('active');
      });
      
      // Add active class to the selected option
      this.classList.add('active');
      
      // Mark question as answered
      questionCard.classList.add('answered');
      
      // Get the status value
      const statusValue = this.querySelector('input').value;
      
      // Update question card styling
      questionCard.classList.remove('status-needs-attention', 'status-room-for-improvement', 'status-doing-well');
      questionCard.classList.add('status-' + statusValue.replace('_', '-'));
      
      // Update completion count
      updateCompletionCount();
    });
  });
  
  // Initialize status from existing responses
  document.querySelectorAll('.status-radio:checked').forEach(radio => {
    const questionCard = radio.closest('.question-card');
    const statusOption = radio.closest('.status-option');
    
    if (statusOption) {
      statusOption.classList.add('active');
      questionCard.classList.add('answered');
      
      const statusValue = radio.value;
      questionCard.classList.add('status-' + statusValue.replace('_', '-'));
    }
  });
  
  // Initial completion count
  updateCompletionCount();
  
  // Filter health check categories
  const categoryTabs = document.querySelectorAll('.category-tab');
  if (categoryTabs.length > 0) {
    categoryTabs.forEach(tab => {
      tab.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Remove active class from all tabs
        categoryTabs.forEach(t => t.classList.remove('active'));
        
        // Add active class to clicked tab
        this.classList.add('active');
        
        // Get the category
        const category = this.getAttribute('data-category');
        
        // Show/hide questions based on category
        if (category === 'all') {
          // Show all questions
          document.querySelectorAll('.question-card').forEach(card => {
            card.style.display = 'block';
          });
        } else {
          // Show only questions in this category
          document.querySelectorAll('.question-card').forEach(card => {
            if (card.getAttribute('data-category') === category) {
              card.style.display = 'block';
            } else {
              card.style.display = 'none';
            }
          });
        }
      });
    });
  }
  
  // Flag issues button
  const flagIssuesBtn = document.getElementById('flag-issues-btn');
  if (flagIssuesBtn) {
    flagIssuesBtn.addEventListener('click', function() {
      // Get all questions without responses
      const unansweredQuestions = document.querySelectorAll('.question-card:not(.answered)');
      
      if (unansweredQuestions.length === 0) {
        alert('All questions have been answered!');
        return;
      }
      
      // Scroll to first unanswered question
      unansweredQuestions[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Highlight unanswered questions
      unansweredQuestions.forEach(question => {
        question.classList.add('highlight-unanswered');
        
        // Remove highlight after 2 seconds
        setTimeout(() => {
          question.classList.remove('highlight-unanswered');
        }, 2000);
      });
    });
  }
  
  // Save responses button
  const saveResponsesBtn = document.getElementById('save-responses-btn');
  if (saveResponsesBtn) {
    saveResponsesBtn.addEventListener('click', function() {
      // Get all questions without responses
      const unansweredQuestions = document.querySelectorAll('.question-card:not(.answered)');
      
      if (unansweredQuestions.length > 0) {
        if (!confirm('You have ' + unansweredQuestions.length + ' unanswered question(s). Do you want to save your responses anyway?')) {
          return;
        }
      }
      
      // Submit the form
      document.getElementById('health-check-form').submit();
    });
  }
  
  // Auto-resize comment textareas
  document.querySelectorAll('textarea.autosize').forEach(textarea => {
    textarea.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Initial height
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight) + 'px';
  });
});

// Function to update the completion count
function updateCompletionCount() {
  const totalQuestions = document.querySelectorAll('.question-card').length;
  const answeredQuestions = document.querySelectorAll('.question-card.answered').length;
  const progressElement = document.getElementById('completion-progress');
  const progressTextElement = document.getElementById('completion-text');
  
  if (progressElement && progressTextElement) {
    const percentage = Math.round((answeredQuestions / totalQuestions) * 100);
    progressElement.style.width = percentage + '%';
    progressTextElement.textContent = answeredQuestions + ' of ' + totalQuestions + ' completed';
  }
}

// Function to handle status selection
function selectStatus(questionId, status) {
  const questionCard = document.querySelector(`.question-card[data-question-id="${questionId}"]`);
  if (!questionCard) return;
  
  // Find the radio input with the specified status
  const radioInput = questionCard.querySelector(`input[value="${status}"]`);
  if (radioInput) {
    radioInput.checked = true;
    
    // Trigger a click event on the parent option to apply styling
    const statusOption = radioInput.closest('.status-option');
    if (statusOption) {
      statusOption.click();
    }
  }
}

// Function to toggle comment visibility
function toggleComments(buttonElement) {
  const commentsSection = buttonElement.nextElementSibling;
  
  if (commentsSection.style.display === 'none' || commentsSection.style.display === '') {
    commentsSection.style.display = 'block';
    buttonElement.textContent = 'Hide Comments';
  } else {
    commentsSection.style.display = 'none';
    buttonElement.textContent = 'Show Comments';
  }
}
