import React, { useState } from 'react';

function AntigenResults({ results }) {
  const [showMRNA, setShowMRNA] = useState(false);

  if (!results) return null;

  return (
    <div className="results-section">
      <h2>🎯 Predicted Universal Antigen</h2>

      {/* Predicted Antigen Card */}
      <div className="antigen-card">
        <h3>Recommended Antigen Sequence</h3>
        <p className="position-info">
          Position {results.antigen_position.start} - {results.antigen_position.end} of user sequence
        </p>
        
        <div className="sequence-display">
          <code>{results.predicted_antigen}</code>
        </div>

        <p className="sequence-info">
          <strong>Length:</strong> {results.predicted_antigen.length} amino acids
        </p>

        {/* mRNA Toggle */}
        <button 
          className="toggle-button"
          onClick={() => setShowMRNA(!showMRNA)}
        >
          {showMRNA ? '▼ Hide mRNA' : '▶ Show mRNA'}
        </button>

        {showMRNA && (
          <div className="mrna-display">
            <h4>Optimized mRNA Sequence</h4>
            <code>{results.mrna}</code>
            <p className="mrna-note">
              ✅ This mRNA can be synthesized and formulated into vaccines. 
              Codons optimized for human expression.
            </p>
          </div>
        )}
      </div>

      {/* Analysis Summary */}
      <div className="analysis-summary">
        <h3>Analysis Summary</h3>
        <ul>
          <li>
            <strong>Analyzed:</strong> {results.related_sequences_count} related HIV sequences from NCBI
          </li>
          <li>
            <strong>Method:</strong> Evolutionary-weighted conservation + AI prediction
          </li>
          <li>
            <strong>User Sequence:</strong> {results.user_sequence_length} amino acids
          </li>
          <li>
            <strong>Coverage:</strong> Works against {(results.coverage.overall * 100).toFixed(1)}% of known strains
          </li>
        </ul>
      </div>
    </div>
  );
}

export default AntigenResults;