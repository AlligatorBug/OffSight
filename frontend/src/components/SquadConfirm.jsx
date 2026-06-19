import React from 'react';

function Column({ title, accent, players, onEditName }) {
  return (
    <div className="squad-col">
      <div className={`squad-head ${accent}`}>
        <h3>{title}</h3>
        {accent && <span className="tag">{accent === 'home' ? 'Home' : 'Away'}</span>}
      </div>
      {players.map((p, idx) => (
        <div className="roster-row" key={`${p.number}-${idx}`}>
          <div className="num">{p.number}</div>
          <input
            className="pname-input"
            value={p.name}
            onChange={(e) => onEditName(p, e.target.value)}
          />
        </div>
      ))}
      {players.length === 0 && <div className="roster-row empty">No players</div>}
    </div>
  );
}

export default function SquadConfirm({ fixture, squad, source, syncedAt, onChange, onBack, onConfirm }) {
  const home = squad.filter((p) => p.side === 'home');
  const away = squad.filter((p) => p.side === 'away');
  const grouped = home.length > 0 || away.length > 0;
  const ungrouped = squad.filter((p) => !p.side);

  const handleEdit = (player, newName) => {
    const next = squad.map((p) => (p === player ? { ...p, name: newName } : p));
    onChange(next);
  };

  const syncedLabel =
    source === 'api' && syncedAt
      ? `synced ${Math.max(1, Math.round((Date.now() - new Date(syncedAt)) / 60000))} min ago`
      : 'from manual upload';

  return (
    <section className="screen active">
      <div className="eyebrow">Squad source</div>
      <h2 className="title">Confirm starting lineups</h2>
      <p className="subtitle">
        Review before processing starts — edit any row if a late change isn&rsquo;t reflected yet.
      </p>

      <div className="source-bar">
        <span className="ok">●</span>
        {fixture
          ? `Fixture #${fixture.fixtureId} · ${fixture.homeTeam} vs ${fixture.awayTeam}`
          : 'Manual squad upload'}
        {' · '}
        {syncedLabel}
      </div>

      {grouped ? (
        <div className="squads">
          <Column title={fixture?.homeTeam || 'Home'} accent="home" players={home} onEditName={handleEdit} />
          <Column title={fixture?.awayTeam || 'Away'} accent="away" players={away} onEditName={handleEdit} />
        </div>
      ) : (
        <div className="squads single">
          <Column title="Squad" accent="" players={ungrouped} onEditName={handleEdit} />
        </div>
      )}

      <div className="step-actions">
        <button className="text-btn" onClick={onBack}>
          ← Back to search
        </button>
        <button className="primary-btn" onClick={onConfirm} disabled={squad.length === 0}>
          Confirm &amp; continue ▸
        </button>
      </div>
    </section>
  );
}