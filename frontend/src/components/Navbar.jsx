import React from 'react';

export default function Navbar({ connected }) {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="mark" />
        <h1>Off<span>Sight</span></h1>
      </div>
      <div className="status-pill">
        <span className="dot" style={{ background: connected ? 'var(--green)' : 'var(--slate)' }} />
        {connected ? 'PIPELINE LIVE' : 'IDLE'}
      </div>
    </header>
  );
}