import React, { useState } from 'react';

function AntigenScore({ region, index }) {
  const [showMRNA, setShowMRNA] = useState(false);

  const conservationPercent = (region.conservation_score * 100).toFixed(1);

  return (
    <div className="antigen-card">
      <div className="card-header">
        <h4>Antigen Region {index}</h4>
        <div className={`conservation-badge ${conservationPercent > 70 ? 'high' : conservationPercent > 50 ? 'medium' : 'low'}`}>
          {conservationPercent}% Conserved
        </div>
      </div>

      <div className="card-content">
        <p><strong>Position:</strong> {region.start} - {region.end}</p>
        
        <div className="sequence-box">
          <p><strong>Amino Acid Sequence:</strong></p>
          <code>{region.sequence}</code>
        </div>

        <button 
          className="toggle-mrna"
          onClick={() => setShowMRNA(!showMRNA)}
        >
          {showMRNA ? '▼ Hide mRNA' : '▶ Show mRNA'}
        </button>

        {showMRNA && (
          <div className="mrna-box">
            <p><strong>Optimized mRNA Sequence:</strong></p>
            <code>{region.mrna}</code>
            <p className="mrna-note">⚠️ This mRNA can be synthesized and formulated into vaccines</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default AntigenScore;