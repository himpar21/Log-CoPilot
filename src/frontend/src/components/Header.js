import React from 'react';

function Header() {
  return (
    <header className="app-header">
      <h1>Log Analysis Copilot</h1>
      <div className="status-indicator"></div>
      <span>Local LLM Active</span>
    </header>
  );
}

export default Header;