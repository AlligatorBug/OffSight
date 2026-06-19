import React from 'react';

export default function StatCards({ detected = 0, tracked = 0, identified = 0, numberOnly = 0 }) {
  return (
    <div className="statstrip">
      <div className="stat">
        <div className="num">{detected}</div>
        <div className="lbl">Detected</div>
      </div>
      <div className="stat">
        <div className="num green">{tracked}</div>
        <div className="lbl">Tracked</div>
      </div>
      <div className="stat">
        <div className="num green">{identified}</div>
        <div className="lbl">Identified</div>
      </div>
      <div className="stat">
        <div className="num amber">{numberOnly}</div>
        <div className="lbl">Number only</div>
      </div>
    </div>
  );
}
