import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function AntigenMetrics({ results }) {
  if (!results) return null;

  const coverageData = [
    { name: 'Subtype A', value: (results.coverage.by_subtype.A * 100).toFixed(1) },
    { name: 'Subtype B', value: (results.coverage.by_subtype.B * 100).toFixed(1) },
    { name: 'Subtype C', value: (results.coverage.by_subtype.C * 100).toFixed(1) },
    { name: 'Subtype D', value: (results.coverage.by_subtype.D * 100).toFixed(1) },
  ];

  return (
    <div className="metrics-section">
      <h2>📊 Coverage & Confidence Analysis</h2>

      {/* Overall Coverage */}
      <div className="metric-card">
        <h3>Overall Coverage</h3>
        <div className="coverage-percentage">
          {(results.coverage.overall * 100).toFixed(1)}%
        </div>
        <p>Works against {results.coverage.exact_matches} out of {results.coverage.total_sequences_analyzed} analyzed HIV sequences</p>
      </div>

      {/* Coverage by Subtype */}
      <div className="metric-card">
        <h3>Coverage by HIV Subtype</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={coverageData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis label={{ value: 'Coverage (%)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Bar dataKey="value" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Confidence Score */}
      <div className="metric-card">
        <h3>Confidence Score</h3>
        <div className="confidence-circle">
          <svg viewBox="0 0 100 100" width="150" height="150">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#e0e0e0" strokeWidth="8" />
            <circle 
              cx="50" 
              cy="50" 
              r="45" 
              fill="none" 
              stroke="#667eea" 
              strokeWidth="8"
              strokeDasharray={`${results.confidence_score * 283} 283`}
            />
            <text x="50" y="55" textAnchor="middle" fontSize="24" fontWeight="bold" fill="#667eea">
              {(results.confidence_score * 100).toFixed(0)}%
            </text>
          </svg>
        </div>
        <p>Model confidence that this antigen will work</p>
      </div>

      {/* Mutation Resistance */}
      <div className="metric-card">
        <h3>Mutation Resistance</h3>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${results.mutation_resistance * 100}%` }}
          ></div>
        </div>
        <p>{(results.mutation_resistance * 100).toFixed(1)}% resistant to likely mutations</p>
      </div>

      {/* Detailed Metrics */}
      <div className="metric-card">
        <h3>Antigen Scores</h3>
        <table className="metrics-table">
          <tbody>
            <tr>
              <td><strong>Conservation Score:</strong></td>
              <td>{(results.metrics.conservation * 100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td><strong>Diversity Score:</strong></td>
              <td>{(results.metrics.diversity * 100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td><strong>Epitope Potential:</strong></td>
              <td>{(results.metrics.epitope_potential * 100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td><strong>Overall Score:</strong></td>
              <td>{(results.metrics.overall_score * 100).toFixed(1)}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AntigenMetrics;