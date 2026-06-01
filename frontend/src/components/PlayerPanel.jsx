import React from 'react';

export default function PlayerPanel({ players = [] }) {
  return (
    <aside className="player-panel">
      <h2>Players</h2>
      <ul>
        {players.map((p) => (
          <li key={p.id}>{p.name} — #{p.jersey}</li>
        ))}
      </ul>
    </aside>
  );
}
