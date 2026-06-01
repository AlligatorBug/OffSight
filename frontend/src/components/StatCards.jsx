import React from 'react';

export default function StatCards({ stats = {} }) {
  return (
    <div className="stat-cards">
      <div className="card">Detected: {stats.detected ?? 0}</div>
      <div className="card">Tracked: {stats.tracked ?? 0}</div>
      <div className="card">Identified: {stats.identified ?? 0}</div>
    </div>
  );
}
