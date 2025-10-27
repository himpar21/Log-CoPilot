/**
 * Sends a query to the backend API and returns the structured response.
 * @param {string} query The user's natural language query.
 * @returns {Promise<object>} A promise that resolves to the assistant's structured response.
 */
export const sendMessageToApi = async (query) => {
  try {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    // The backend should return a structured JSON object like:
    // {
    //   "summary": "Natural language answer.",
    //   "evidence": [
    //     { "type": "log", "content": "Log line details..." },
    //     { "type": "table", "headers": ["Col1", "Col2"], "rows": [["val1", "val2"]] }
    //   ]
    // }
    return await response.json();

  } catch (error) {
    console.error("Failed to send message to API:", error);
    throw error; // Re-throw to be caught by the UI component
  }
};