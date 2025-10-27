import React from 'react';

// Component to render a table from evidence data
const EvidenceTable = ({ data }) => (
  <div className="evidence-table-container">
    <table>
      <thead>
        <tr>
          {data.headers.map((header, index) => <th key={index}>{header}</th>)}
        </tr>
      </thead>
      <tbody>
        {data.rows.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {row.map((cell, cellIndex) => <td key={cellIndex}>{cell}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// Component to render a log entry
const EvidenceLog = ({ content }) => (
  <pre className="evidence-log">
    <code>{content}</code>
  </pre>
);

function Message({ message }) {
  const { sender, content } = message;
  const messageClass = sender === 'user' ? 'user-message' : 'assistant-message';

  return (
    <div className={`message ${messageClass}`}>
      <div className="message-content">
        <p>{content.summary}</p>
        {content.evidence && content.evidence.length > 0 && (
          <div className="evidence-section">
            <h4>Evidence:</h4>
            {content.evidence.map((item, index) => {
              switch (item.type) {
                case 'log':
                  return <EvidenceLog key={index} content={item.content} />;
                case 'table':
                  return <EvidenceTable key={index} data={item} />;
                case 'error':
                   return <pre key={index} className="evidence-error"><code>{item.content}</code></pre>;
                default:
                  return null;
              }
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default Message;