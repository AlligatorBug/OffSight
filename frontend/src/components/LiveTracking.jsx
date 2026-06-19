import React, { useEffect, useState } from 'react';
import StatCards from './StatCards';
import PlayerPanel from './PlayerPanel';
import VideoPlayer from './VideoPlayer';
import { classifyLabel } from '../utils/classify';

export default function LiveTracking({
  matchLabel,
  videoFile,
  videoDims,
  status,
  message,
  frame,
  total,
  detections,
  roster,
  resultUrl,
  error,
}) {
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    if (!videoFile) return undefined;
    const url = URL.createObjectURL(videoFile);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [videoFile]);

  const named = roster.filter((p) => p.type === 'named').length;
  const numOnly = roster.filter((p) => p.type === 'numonly').length;
  const tracked = roster.length;

  const pct = total > 0 ? Math.round((frame / total) * 100) : 0;
  const aspect = videoDims ? `${videoDims.width} / ${videoDims.height}` : '16 / 9';

  return (
    <section className="screen active wide">
      <div className="eyebrow">Processing</div>
      <h2 className="title">Tracking in progress</h2>
      <p className="subtitle">
        {matchLabel}
        {videoFile ? ` · ${videoFile.name}` : ''}
      </p>

      <div className="tracking-grid">
        <div className="tracking-main">
          <StatCards detected={detections.length} tracked={tracked} identified={named} numberOnly={numOnly} />

          {error && <div className="error-banner">{error}</div>}

          <div className="pitch-wrap" style={{ aspectRatio: aspect }}>
            {previewUrl && <video className="pitch-video" src={previewUrl} muted autoPlay loop playsInline />}

            <div className="frame-tag">
              <span className="rec" />
              FRAME {String(frame).padStart(4, '0')} / {String(total).padStart(4, '0')}
            </div>

            {videoDims &&
              detections.map((d) => {
                const [x1, y1, x2, y2] = d.bbox;
                const left = (x1 / videoDims.width) * 100;
                const top = (y1 / videoDims.height) * 100;
                const width = ((x2 - x1) / videoDims.width) * 100;
                const height = ((y2 - y1) / videoDims.height) * 100;
                const type = classifyLabel(d.label);

                return (
                  <div
                    key={d.tracker_id}
                    className={`bbox ${type}`}
                    style={{ left: `${left}%`, top: `${top}%`, width: `${width}%`, height: `${height}%` }}
                  >
                    <span className="tag">{d.label}</span>
                  </div>
                );
              })}
          </div>

          <div className="progress-row">
            <span>{status === 'done' ? 'DONE' : 'PROCESSING'}</span>
            <div className="progress-track">
              <i className="progress-fill" style={{ width: `${pct}%` }} />
            </div>
            <span>
              {frame} / {total || '—'}
            </span>
          </div>

          {message && <p className="status-message">{message}</p>}

          {resultUrl && (
            <div className="result-block">
              <div className="section-label">Annotated output</div>
              <VideoPlayer src={resultUrl} />
              <a className="primary-btn" href={resultUrl} download="offsight_annotated.mp4">
                Download video ▸
              </a>
            </div>
          )}
        </div>

        <PlayerPanel players={roster} />
      </div>
    </section>
  );
}