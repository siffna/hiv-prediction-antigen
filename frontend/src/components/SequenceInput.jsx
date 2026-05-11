import React, { useState } from 'react';

function SequenceInput({ onPredict }) {
  const [sequence, setSequence] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePredict = () => {
    if (!sequence.trim()) {
      alert('Please paste a sequence');
      return;
    }

    setLoading(true);
    
    try {
      onPredict({ sequence: sequence.trim() });
    } catch (err) {
      alert('Error: ' + err.message);
      setLoading(false);
    }
  };

  return (
    <div className="input-section">
      <h2>🧬 Paste HIV Protein Sequence</h2>
      
      <textarea 
        value={sequence}
        onChange={(e) => setSequence(e.target.value)}
        placeholder="Paste HIV protein sequence in FASTA format or raw amino acids (e.g., MGARASLR...)"
        rows={8}
        disabled={loading}
      />

      <div className="info-box">
        <p><strong>Note:</strong> Paste any HIV strain/group. We'll fetch related sequences from NCBI and predict an optimal antigen.</p>
      </div>

      <button 
        className="predict-btn" 
        onClick={handlePredict}
        disabled={loading}
      >
        {loading ? '🔄 Analyzing (30-60 seconds)...' : '🚀 Predict Universal Antigen'}
      </button>
    </div>
  );
}

export default SequenceInput;