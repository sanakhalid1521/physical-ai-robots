/**
 * Text Selection Utility for RAG Chatbot
 * Provides functionality to capture and manage selected text
 */

class TextSelectionManager {
  constructor() {
    this.selectedText = '';
    this.onSelectionChange = null;
    this.isActive = false;
  }

  /**
   * Initialize the text selection manager
   * @param {Function} callback - Function to call when selection changes
   */
  init(callback) {
    this.onSelectionChange = callback;
    this.attachEventListeners();
  }

  /**
   * Attach event listeners for text selection
   */
  attachEventListeners() {
    document.addEventListener('mouseup', this.handleSelection.bind(this));
    document.addEventListener('keyup', (e) => {
      if (e.key === 'Escape') {
        this.clearSelection();
      }
    });
  }

  /**
   * Handle text selection event
   */
  handleSelection() {
    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (text) {
      this.selectedText = text;
      if (this.onSelectionChange) {
        this.onSelectionChange(text);
      }
    }
  }

  /**
   * Get the currently selected text
   * @returns {string} The selected text
   */
  getSelectedText() {
    return this.selectedText;
  }

  /**
   * Clear the current selection
   */
  clearSelection() {
    this.selectedText = '';
    if (this.onSelectionChange) {
      this.onSelectionChange('');
    }
  }

  /**
   * Highlight selected text in the DOM (visual feedback)
   */
  highlightSelection() {
    // Create a temporary span to wrap the selection
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      if (!range.collapsed) {
        const span = document.createElement('span');
        span.style.backgroundColor = 'yellow';
        span.style.opacity = '0.5';
        range.surroundContents(span);

        // Remove the highlight after a short delay
        setTimeout(() => {
          if (span.parentNode) {
            const content = span.childNodes;
            const parent = span.parentNode;

            // Move all child nodes out of the span
            while (content.length > 0) {
              parent.insertBefore(content[0], span);
            }

            // Remove the empty span
            parent.removeChild(span);
          }
        }, 1000);
      }
    }
  }

  /**
   * Get selection context (surrounding text)
   * @param {number} contextLength - Number of characters before/after selection
   * @returns {Object} Object containing selected text and context
   */
  getSelectionWithContext(contextLength = 50) {
    const selection = window.getSelection();
    if (!selection.rangeCount || selection.toString().trim() === '') {
      return { text: '', context: '' };
    }

    const range = selection.getRangeAt(0);
    const selectedText = selection.toString();

    // Get surrounding context
    const startRange = document.createRange();
    startRange.setStart(range.startContainer, 0);
    startRange.setEnd(range.startContainer, range.startOffset);
    const beforeText = startRange.toString().slice(-contextLength);

    const endRange = document.createRange();
    endRange.setStart(range.endContainer, range.endOffset);
    endRange.setEnd(range.endContainer, range.endContainer.length || range.endContainer.textContent?.length || 0);
    const afterText = endRange.toString().substring(0, contextLength);

    return {
      text: selectedText,
      context: `${beforeText}${selectedText}${afterText}`,
      before: beforeText,
      after: afterText
    };
  }

  /**
   * Check if text is currently selected
   * @returns {boolean} True if text is selected, false otherwise
   */
  hasSelection() {
    return this.selectedText && this.selectedText.length > 0;
  }

  /**
   * Deactivate the text selection manager
   */
  destroy() {
    document.removeEventListener('mouseup', this.handleSelection.bind(this));
    this.selectedText = '';
    this.onSelectionChange = null;
    this.isActive = false;
  }
}

// Create a singleton instance
const textSelectionManager = new TextSelectionManager();

export default textSelectionManager;