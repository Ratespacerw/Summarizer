// src/App.jsx
import React, { useState } from 'react';
import './App.css'; 

function App() {
  const [inputText, setInputText] = useState(""); 
  const [summary, setSummary] = useState("");
  const [keywords, setKeywords] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault(); 

    setError(null);
    setSummary("");
    setKeywords([]);
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/summarizer/process/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error_detail || `Server responded with status: ${response.status}`);
      }

      const data = await response.json(); 
      setSummary(data.summary);
      setKeywords(data.keywords);

    } catch (err) {
      console.error("API call failed:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AI Content Summarizer</h1>
        <p>Enter text below to get a summary and keywords.</p>
      </header>

      <main className="app-main">
        <form className="summarizer-form" onSubmit={handleSubmit}>
          <textarea
            value={inputText}
            onChange={(event) => setInputText(event.target.value)}
            placeholder="Paste your long article or text here..."
            className="text-input"
            disabled={isLoading}
          />
          <button type="submit" className="submit-button" disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Process Text'}
          </button>
        </form>

        <div className="results-container">
          {isLoading && <p>Loading summary...</p>}
          
          {error && <p className="error-message">Error: {error}</p>}
          
          {summary && !isLoading && (
            <div className="summary-section">
              <h2>Summary:</h2>
              <p>{summary}</p>
            </div>
          )}

          {keywords.length > 0 && !isLoading && (
            <div className="keywords-section">
              <h2>Keywords:</h2>
              <div className="keywords-list">
                {keywords.map((keyword, index) => (
                  <span key={index} className="keyword-tag">{keyword}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
      
      <footer className="app-footer">
        {/* --- MODIFIED LINE --- */}
        <p>Built with Django & React by Ansal Chaubey</p>
      </footer>
    </div>
  );
}

export default App;