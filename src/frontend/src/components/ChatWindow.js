import React, { useRef, useEffect } from 'react';
import Message from './Message';

function ChatWindow({ messages, isLoading }) {
  const chatEndRef = useRef(null);

  // Auto-scroll to the latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="chat-window">
      {messages.map(msg => (
        <Message key={msg.id} message={msg} />
      ))}
      {isLoading && (
        <div className="message assistant-message">
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}
      <div ref={chatEndRef} />
    </div>
  );
}

export default ChatWindow;