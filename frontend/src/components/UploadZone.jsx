import React from 'react';
import useUpload from '../hooks/useUpload';

export default function UploadZone() {
  const { onDrop, isDragging } = useUpload();

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''}`}
      onDrop={onDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      <p>Drag & drop a football clip here, or click to select</p>
    </div>
  );
}
