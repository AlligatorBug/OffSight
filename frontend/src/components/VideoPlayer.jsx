import React from 'react';

export default function VideoPlayer({ src }) {
  if (!src) return null;
  return (
    <div className="video-player">
      <video src={src} controls autoPlay muted />
    </div>
  );
}
