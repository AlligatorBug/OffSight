import React, { useRef, useState } from 'react';

export default function UploadZone({ linkedLabel, onFileChosen, onBack, onStart, canStart }) {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const validateAndSet = (file) => {
    if (!file) return;
    if (!file.type.startsWith('video/')) {
      setError('Please choose a video file (MP4, MOV, or MKV).');
      return;
    }
    setError(null);
    setFileName(file.name);
    onFileChosen(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    validateAndSet(e.dataTransfer.files[0]);
  };

  return (
    <section className="screen active">
      <div className="eyebrow">Match footage</div>
      <h2 className="title">Upload the clip</h2>
      <p className="subtitle">
        Drop your match footage in. Detection, tracking, OCR, and identification start as soon as it&rsquo;s
        received.
      </p>

      <div
        className={`dropzone ${isDragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onClick={() => inputRef.current?.click()}
      >
        <div className="icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00E5A0" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>
        <div className="ttl">{fileName || 'Drag & drop your clip here'}</div>
        <div className="hint">{fileName ? 'Click to choose a different file' : 'or click below to browse your files'}</div>
        <button
          className="browse-btn"
          onClick={(e) => {
            e.stopPropagation();
            inputRef.current?.click();
          }}
        >
          Choose file
        </button>
        <div className="fmt">MP4 · MOV · MKV</div>
        <input
          ref={inputRef}
          type="file"
          accept="video/mp4,video/quicktime,video/x-matroska"
          style={{ display: 'none' }}
          onChange={(e) => validateAndSet(e.target.files[0])}
        />
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="linked-pill">
        <span className="dot2" />
        Lineup linked: {linkedLabel}
      </div>

      <div className="step-actions">
        <button className="text-btn" onClick={onBack}>
          ← Back to squad
        </button>
        <button className="primary-btn" onClick={onStart} disabled={!canStart}>
          Start processing ▸
        </button>
      </div>
    </section>
  );
}
