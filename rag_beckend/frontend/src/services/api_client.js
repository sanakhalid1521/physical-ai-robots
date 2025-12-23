/**
 * API Client for RAG Chatbot
 * Provides methods to interact with the backend API
 */

class ApiClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  /**
   * Send a chat message to the backend
   * @param {Object} messageData - The message data to send
   * @param {string} messageData.message - The user's message
   * @param {string} messageData.mode - The chat mode ('book' or 'selection')
   * @param {string} [messageData.selectedText] - Selected text for selection mode
   * @param {string} [messageData.userId] - User ID (optional)
   * @param {string} [messageData.language] - Language preference (optional)
   * @returns {Promise<Object>} The response from the backend
   */
  async sendMessage(messageData) {
    try {
      const response = await fetch(`${this.baseURL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(messageData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Send a message specifically in book mode
   * @param {string} message - The user's message
   * @param {string} [language] - Language preference (optional)
   * @param {string} [userId] - User ID (optional)
   * @returns {Promise<Object>} The response from the backend
   */
  async sendBookModeMessage(message, language, userId) {
    const messageData = {
      message,
      mode: 'book',
    };

    if (language) messageData.language = language;
    if (userId) messageData.userId = userId;

    return this.sendMessage(messageData);
  }

  /**
   * Send a message specifically in selection mode
   * @param {string} message - The user's message
   * @param {string} selectedText - The selected text to use as context
   * @param {string} [language] - Language preference (optional)
   * @param {string} [userId] - User ID (optional)
   * @returns {Promise<Object>} The response from the backend
   */
  async sendSelectionModeMessage(message, selectedText, language, userId) {
    const messageData = {
      message,
      mode: 'selection',
      selectedText,
    };

    if (language) messageData.language = language;
    if (userId) messageData.userId = userId;

    return this.sendMessage(messageData);
  }

  /**
   * Check the health of the API
   * @returns {Promise<Object>} Health check response
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);

      if (!response.ok) {
        throw new Error(`Health check failed with status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  /**
   * Get chat history for a user (if implemented in backend)
   * @param {string} userId - The user ID
   * @returns {Promise<Array>} Array of chat history items
   */
  async getChatHistory(userId) {
    try {
      const response = await fetch(`${this.baseURL}/history/${userId}`);

      if (!response.ok) {
        if (response.status === 404) {
          return []; // Return empty array if no history exists
        }
        throw new Error(`Failed to get chat history: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting chat history:', error);
      throw error;
    }
  }
}

// Create a singleton instance
const apiClient = new ApiClient();

export default apiClient;