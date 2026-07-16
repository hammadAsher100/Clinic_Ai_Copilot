/**
 * Custom Modal System for Clinical AI Co-Pilot
 * Beautiful replacements for alert(), confirm(), and prompt()
 */

class CustomModal {
  constructor() {
    this.overlay = null;
    this.currentResolver = null;
    this.init();
  }

  init() {
    // Create modal overlay if it doesn't exist
    if (!document.getElementById('custom-modal-overlay')) {
      const overlay = document.createElement('div');
      overlay.id = 'custom-modal-overlay';
      overlay.className = 'modal-overlay';
      overlay.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-header">
            <div class="modal-icon" id="modal-icon">ℹ️</div>
            <div class="modal-title-block">
              <h3 class="modal-title" id="modal-title">Notification</h3>
              <p class="modal-subtitle" id="modal-subtitle"></p>
            </div>
          </div>
          <div class="modal-body">
            <p class="modal-message" id="modal-message"></p>
            <div class="modal-input-group" id="modal-input-group" style="display: none;">
              <label id="modal-input-label">Enter value:</label>
              <input type="text" class="modal-input" id="modal-input" />
            </div>
          </div>
          <div class="modal-footer" id="modal-footer"></div>
        </div>
      `;
      document.body.appendChild(overlay);
      this.overlay = overlay;

      // Close on overlay click (outside dialog)
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          this.close(null);
        }
      });

      // Close on ESC key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.overlay.classList.contains('active')) {
          this.close(null);
        }
      });
    } else {
      this.overlay = document.getElementById('custom-modal-overlay');
    }
  }

  show(config) {
    return new Promise((resolve) => {
      this.currentResolver = resolve;

      // Set icon and type
      const iconElement = document.getElementById('modal-icon');
      const iconMap = {
        info: { emoji: 'ℹ️', class: 'info' },
        success: { emoji: '✅', class: 'success' },
        warning: { emoji: '⚠️', class: 'warning' },
        error: { emoji: '❌', class: 'error' },
        question: { emoji: '❓', class: 'question' },
      };
      const iconData = iconMap[config.type] || iconMap.info;
      iconElement.textContent = iconData.emoji;
      iconElement.className = `modal-icon ${iconData.class}`;

      // Set title and subtitle
      document.getElementById('modal-title').textContent = config.title || 'Notification';
      const subtitleElement = document.getElementById('modal-subtitle');
      if (config.subtitle) {
        subtitleElement.textContent = config.subtitle;
        subtitleElement.style.display = 'block';
      } else {
        subtitleElement.style.display = 'none';
      }

      // Set message
      document.getElementById('modal-message').textContent = config.message || '';

      // Handle input for prompt
      const inputGroup = document.getElementById('modal-input-group');
      const input = document.getElementById('modal-input');
      if (config.input) {
        inputGroup.style.display = 'block';
        document.getElementById('modal-input-label').textContent = config.inputLabel || 'Enter value:';
        input.value = config.defaultValue || '';
        input.placeholder = config.placeholder || '';
        // Focus input after modal opens
        setTimeout(() => input.focus(), 100);
      } else {
        inputGroup.style.display = 'none';
      }

      // Create buttons
      const footer = document.getElementById('modal-footer');
      footer.innerHTML = '';

      if (config.buttons) {
        config.buttons.forEach((btn) => {
          const button = document.createElement('button');
          button.className = `btn ${btn.class || 'btn-secondary'}`;
          button.textContent = btn.text;
          button.addEventListener('click', () => {
            if (config.input && btn.value === true) {
              this.close(input.value);
            } else {
              this.close(btn.value);
            }
          });
          footer.appendChild(button);
        });
      }

      // Handle Enter key for input
      if (config.input) {
        input.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') {
            this.close(input.value);
          }
        });
      }

      // Show modal with animation
      this.overlay.classList.add('active');
    });
  }

  close(value) {
    this.overlay.classList.remove('active');
    if (this.currentResolver) {
      this.currentResolver(value);
      this.currentResolver = null;
    }
  }

  // Alert - just shows a message with OK button
  alert(message, title = 'Alert', type = 'info') {
    return this.show({
      type,
      title,
      message,
      buttons: [
        { text: 'OK', value: true, class: 'btn-primary' }
      ]
    });
  }

  // Confirm - shows a message with Yes/No buttons
  confirm(message, title = 'Confirm', type = 'question') {
    return this.show({
      type,
      title,
      message,
      buttons: [
        { text: 'Cancel', value: false, class: 'btn-secondary' },
        { text: 'Confirm', value: true, class: 'btn-primary' }
      ]
    });
  }

  // Prompt - shows an input field
  prompt(message, defaultValue = '', title = 'Input Required', placeholder = '') {
    return this.show({
      type: 'question',
      title,
      message,
      input: true,
      defaultValue,
      placeholder,
      inputLabel: message,
      buttons: [
        { text: 'Cancel', value: null, class: 'btn-secondary' },
        { text: 'OK', value: true, class: 'btn-primary' }
      ]
    });
  }

  // Success notification
  success(message, title = 'Success') {
    return this.alert(message, title, 'success');
  }

  // Error notification
  error(message, title = 'Error') {
    return this.alert(message, title, 'error');
  }

  // Warning notification
  warning(message, title = 'Warning') {
    return this.alert(message, title, 'warning');
  }

  // Info notification
  info(message, title = 'Information') {
    return this.alert(message, title, 'info');
  }
}

// Create global instance
const modal = new CustomModal();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = modal;
}

// Make available globally
window.modal = modal;
