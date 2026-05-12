import React, { useState } from 'react';
import SequenceInput from './components/SequenceInput';
import AntigenResults from './components/AntigenResults';
import AntigenMetrics from './components/AntigenMetrics';
import './App.css';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async (input) => {
    setLoading(true);
    setError(null);
    setResults(null);
    
    console.log("Sending to backend:", input);
    
    try {
      const response = await fetch('https://hiv-prediction-antigen.onrender.com', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input)
      });
      
      console.log("Response status:", response.status);
      
      const data = await response.json();
      
      console.log("Response data:", data);
      
      if (response.ok) {
        setResults(data);
      } else {
        setError(data.error || 'Prediction failed');
      }
    } catch (err) {
      console.error("Fetch error:", err);
      setError('Backend connection error. Make sure Flask is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>HIV Antigen Prediction Tool</h1>
        <p>Evolutionary analysis for vaccine target discovery</p>
        <p className="subtitle">Paste HIV sequence → Predicts antigen → Generates mRNA</p>
      </header>

      <main className="app-main">
        <SequenceInput onPredict={handlePredict} />
        
        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Analyzing your HIV sequence against NCBI database...</p>
            <p className="loading-detail">This may take 30-60 seconds</p>
          </div>
        )}
        
        {error && <div className="error">{error}</div>}
        
        {results && (
          <>
            <AntigenResults results={results} />
            <AntigenMetrics results={results} />
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Using NCBI BLAST, evolutionary analysis, and heuristic scoring for vaccine design</p>
      </footer>
    </div>
  );
}

export default App;