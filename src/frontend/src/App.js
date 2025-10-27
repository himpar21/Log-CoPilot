import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import { sendMessageToApi } from './api/chatService';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      content: {
        summary: "Welcome to the Log Analysis Assistant! I'm ready to help you analyze your logs. Try asking a question like 'Which service showed max latency yesterday?'",
        evidence: []
      }
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (query) => {
    if (!query.trim()) return;

    // Add user message to the chat
    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: { summary: query }
    };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      // Send query to backend and get response
      const assistantResponse = await sendMessageToApi(query);
      
      const assistantMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        content: assistantResponse
      };
      setMessages(prevMessages => [...prevMessages, assistantMessage]);

    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        content: {
          summary: "Sorry, I encountered an error. Please check the backend connection or try again.",
          evidence: [{ type: 'error', content: error.message }]
        }
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />
      <ChatWindow messages={messages} isLoading={isLoading} />
      <InputBar onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}

export default App; 