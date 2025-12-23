import React, { useState, useEffect, useRef } from 'react';
import apiClient from '../services/api_client';
import './ChatWidget.css';

const ChatWidget = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState('book'); // 'book' or 'selection'
  const [selectedText, setSelectedText] = useState('');
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [language, setLanguage] = useState('en'); // Default to English
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Handle text selection
  useEffect(() => {
    const handleSelection = () => {
      if (isSelectionMode) {
        const selectedText = window.getSelection().toString().trim();
        if (selectedText) {
          setSelectedText(selectedText);
          setIsSelectionMode(false); // Turn off selection mode after capturing
        }
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, [isSelectionMode]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Prepare the request based on mode
      const messageData = {
        message: inputMessage,
        mode: mode,
        language: language, // Include language preference
      };

      // Add selected text if in selection mode
      if (mode === 'selection' && selectedText) {
        messageData.selectedText = selectedText;
      }

      // Call the backend API using the API client
      const data = await apiClient.sendMessage(messageData);

      // Add bot response to chat
      const botMessage = {
        id: Date.now() + 1,
        text: data.answer,
        sender: 'bot',
        sources: data.sources,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, there was an error processing your request. Please try again.',
        sender: 'bot',
        isError: true,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startTextSelection = () => {
    setIsSelectionMode(true);
    alert('Please select text on the page. The selected text will be used as context.');
  };

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <h3>Book Assistant</h3>
        <div className="chat-controls">
          <div className="chat-mode-selector">
            <button
              className={mode === 'book' ? 'active' : ''}
              onClick={() => setMode('book')}
            >
              Full Book
            </button>
            <button
              className={mode === 'selection' ? 'active' : ''}
              onClick={startTextSelection}
            >
              Selected Text
            </button>
          </div>
          <div className="language-selector">
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="en">English</option>
              <option value="ur">Urdu</option>
            </select>
          </div>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <p>Hello! I'm your book assistant. You can ask me questions about the book content.</p>
            <p>Select "Full Book" to search the entire book or "Selected Text" to ask about specific text.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
            >
              <div className="message-content">
                <p>{message.text}</p>
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <small>Sources: {message.sources.map((s, i) =>
                      <span key={i} className="source">{s}</span>
                    ).reduce((prev, curr) => [prev, ', ', curr])}</small>
                  </div>
                )}
                {message.isError && (
                  <small className="error-message">Error occurred - please try again</small>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message bot-message">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        {mode === 'selection' && selectedText && (
          <div className="selected-text-preview">
            <small>Selected text: <em>{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}</em></small>
          </div>
        )}
        <div className="input-controls">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the book..."
            disabled={isLoading}
            rows="3"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="send-button"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWidget;