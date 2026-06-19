import React from 'react';

const TYPE_LABEL = {
  named: 'Identified',
  numonly: 'Number only',
  idonly: 'Tracked',
};

const TYPE_ORDER = { named: 0, numonly: 1, idonly: 2 };

export default function PlayerPanel({ players = [] }) {
  const sorted = [...players].sort((a, b) => TYPE_ORDER[a.type] - TYPE_ORDER[b.type]);
  const identifiedCount = players.filter((p) => p.type === 'named').length;

  return (
    <aside className="roster-side">
      <div className="side-head">
        <h2>Roster</h2>
        <span className="count">
          {identifiedCount} / {players.length}
        </span>
      </div>
      <div className="roster-list">
        {sorted.map((p) => (
          <div className={`player-row ${p.type}`} key={p.trackerId}>
            <div className="jersey">{p.label.startsWith('#') ? p.label.slice(1) : p.trackerId}</div>
            <div className="meta">
              <div className={`pname2 ${p.type !== 'named' ? 'unknown' : ''}`}>
                {p.type === 'named' ? p.label : p.type === 'numonly' ? `Unmatched ${p.label}` : 'Re-ID pending'}
              </div>
              <div className="sub">
                {TYPE_LABEL[p.type]} · ID {p.trackerId}
              </div>
            </div>
          </div>
        ))}
        {sorted.length === 0 && <div className="roster-empty">Waiting for first detections…</div>}
      </div>
    </aside>
  );
}