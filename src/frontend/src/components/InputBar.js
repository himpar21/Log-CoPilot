import React, { useState } from 'react';

function InputBar({ onSendMessage, isLoading }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSendMessage(query);
      setQuery('');
    }
  };

  return (
    <form className="input-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask about your logs..."
        disabled={isLoading}
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Thinking...' : 'Send'}
      </button>
    </form>
  );
}

export default InputBar;