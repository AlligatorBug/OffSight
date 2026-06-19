import React from 'react';

const STEPS = [
  { n: 1, label: 'Find match' },
  { n: 2, label: 'Confirm squad' },
  { n: 3, label: 'Upload footage' },
  { n: 4, label: 'Live tracking' },
];

export default function Stepper({ currentStep }) {
  return (
    <nav className="stepper">
      {STEPS.map((s) => (
        <div
          key={s.n}
          className={`step ${s.n === currentStep ? 'active' : ''} ${s.n < currentStep ? 'done' : ''}`}
        >
          <div className="circle">{s.n < currentStep ? '✓' : s.n}</div>
          <div className="label">{s.label}</div>
          {s.n !== STEPS.length && <div className="step-line" />}
        </div>
      ))}
    </nav>
  );
}