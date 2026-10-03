/**
 * Django Todo App — Main JavaScript
 * Handles: delete confirmation modal, form validation, Bootstrap init
 */

'use strict';

(function () {

  // -------------------------------------------------------------------------
  // 1. Delete Confirmation Modal
  // -------------------------------------------------------------------------

  /**
   * Populate and show the delete confirmation modal when a delete button
   * is clicked. The button must carry:
   *   data-bs-toggle="modal"
   *   data-bs-target="#deleteModal"
   *   data-todo-title="<escaped title>"
   *   data-delete-url="<POST url>"
   */
  function initDeleteModal() {
    var deleteModal = document.getElementById('deleteModal');
    if (!deleteModal) return;

    deleteModal.addEventListener('show.bs.modal', function (event) {
      var triggerButton = event.relatedTarget;
      if (!triggerButton) return;

      var todoTitle = triggerButton.getAttribute('data-todo-title') || 'this todo';
      var deleteUrl = triggerButton.getAttribute('data-delete-url') || '';

      // Populate modal title text
      var titleEl = deleteModal.querySelector('#deleteTodoTitle');
      if (titleEl) {
        titleEl.textContent = '"' + todoTitle + '"';
      }

      // Set the form action URL
      var deleteForm = deleteModal.querySelector('#deleteForm');
      if (deleteForm && deleteUrl) {
        deleteForm.setAttribute('action', deleteUrl);
      }
    });

    // Return focus to the trigger button after modal closes
    deleteModal.addEventListener('hidden.bs.modal', function () {
      var activeEl = document.activeElement;
      if (activeEl && activeEl.tagName === 'BODY') {
        // Find the last focused delete button and restore focus
        var firstDeleteBtn = document.querySelector('[data-bs-target="#deleteModal"]');
        if (firstDeleteBtn) {
          firstDeleteBtn.focus();
        }
      }
    });
  }

  // -------------------------------------------------------------------------
  // 2. Form Validation Enhancement
  // -------------------------------------------------------------------------

  /**
   * Add Bootstrap's native validation styles on submit attempt.
   * Prevents double-submit by disabling the submit button after first click.
   */
  function initFormValidation() {
    var forms = document.querySelectorAll('#todoForm');

    forms.forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        } else {
          // Disable submit button to prevent double-submit
          var submitBtn = form.querySelector('[type="submit"]');
          if (submitBtn) {
            submitBtn.setAttribute('disabled', 'disabled');
            submitBtn.setAttribute('data-loading', 'true');
            var originalText = submitBtn.innerHTML;
            submitBtn.innerHTML =
              '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>Saving...';
            // Re-enable after 5s as a safety net
            setTimeout(function () {
              submitBtn.removeAttribute('disabled');
              submitBtn.removeAttribute('data-loading');
              submitBtn.innerHTML = originalText;
            }, 5000);
          }
        }
        form.classList.add('was-validated');
      });
    });
  }

  // -------------------------------------------------------------------------
  // 3. Auto-dismiss Flash Messages
  // -------------------------------------------------------------------------

  /**
   * Automatically dismiss success/info alerts after 5 seconds.
   */
  function initAutoDismissMessages() {
    var alerts = document.querySelectorAll(
      '#messages-container .alert-success, #messages-container .alert-info'
    );

    alerts.forEach(function (alert) {
      setTimeout(function () {
        // Use Bootstrap's Alert API if available
        if (window.bootstrap && window.bootstrap.Alert) {
          var bsAlert = window.bootstrap.Alert.getOrCreateInstance(alert);
          bsAlert.close();
        } else {
          alert.style.transition = 'opacity 0.5s ease';
          alert.style.opacity = '0';
          setTimeout(function () {
            alert.remove();
          }, 500);
        }
      }, 5000);
    });
  }

  // -------------------------------------------------------------------------
  // 4. Toggle Form Inline Feedback
  // -------------------------------------------------------------------------

  /**
   * Live character counter for the title input.
   */
  function initCharacterCounter() {
    var titleInput = document.querySelector('#id_title');
    if (!titleInput) return;

    var maxLength = parseInt(titleInput.getAttribute('maxlength'), 10) || 255;
    var helpText = titleInput.nextElementSibling;

    // Only attach if the next sibling is the help text (not an error)
    if (!helpText || helpText.classList.contains('invalid-feedback')) return;

    function updateCounter() {
      var remaining = maxLength - titleInput.value.length;
      var icon = '<i class="bi bi-info-circle me-1"></i>';
      helpText.innerHTML = icon + remaining + ' characters remaining.';
      if (remaining < 20) {
        helpText.classList.add('text-warning');
        helpText.classList.remove('text-muted');
      } else if (remaining < 0) {
        helpText.classList.add('text-danger');
        helpText.classList.remove('text-warning');
      } else {
        helpText.classList.remove('text-warning', 'text-danger');
        helpText.classList.add('text-muted');
      }
    }

    titleInput.addEventListener('input', updateCounter);
    updateCounter(); // Run once on load
  }

  // -------------------------------------------------------------------------
  // 5. Search Input — Submit on Status Change
  // -------------------------------------------------------------------------

  /**
   * Auto-submit the filter form when the status dropdown changes.
   */
  function initStatusAutoSubmit() {
    var statusSelect = document.getElementById('statusFilter');
    if (!statusSelect) return;

    statusSelect.addEventListener('change', function () {
      var form = statusSelect.closest('form');
      if (form) {
        form.submit();
      }
    });
  }

  // -------------------------------------------------------------------------
  // 6. Bootstrap Tooltip Initialization
  // -------------------------------------------------------------------------

  function initTooltips() {
    if (!window.bootstrap || !window.bootstrap.Tooltip) return;
    var tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(function (el) {
      new window.bootstrap.Tooltip(el);
    });
  }

  // -------------------------------------------------------------------------
  // Init — run after DOM is ready
  // -------------------------------------------------------------------------

  function init() {
    initDeleteModal();
    initFormValidation();
    initAutoDismissMessages();
    initCharacterCounter();
    initStatusAutoSubmit();
    initTooltips();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
