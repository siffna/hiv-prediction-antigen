import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import AntigenScore from './AntigenScore';

function ResultsVisualization({ results }) {
  if (!results || !results.antigen_regions) {
    return <div>No results to display</div>;
  }

  // Prepare data for chart
  const chartData = results.antigen_regions.map((region, idx) => ({
    name: `Region ${idx + 1}`,
    conservation: (region.conservation_score * 100).toFixed(1),
  }));

  return (
    <div className="results-section">
      <h2>Step 2: Predicted Antigen Regions</h2>

      {/* Conservation Score Chart */}
      <div className="chart-container">
        <h3>Conservation Scores</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis label={{ value: 'Conservation (%)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Bar dataKey="conservation" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Results */}
      <div className="antigen-list">
        <h3>Recommended Antigen Sequences</h3>
        {results.antigen_regions.map((region, idx) => (
          <AntigenScore key={idx} region={region} index={idx + 1} />
        ))}
      </div>

      {/* Summary Stats */}
      <div className="summary-stats">
        <h3>Summary</h3>
        <p>Total sequence length: <strong>{results.sequence_length}</strong> amino acids</p>
        <p>Antigen regions identified: <strong>{results.antigen_regions.length}</strong></p>
        <p>Average conservation: <strong>{(results.scores.reduce((a, b) => a + b, 0) / results.scores.length * 100).toFixed(1)}%</strong></p>
      </div>
    </div>
  );
}

export default ResultsVisualization;