import { useState } from 'react';

export default function useUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  };

  return { file, isDragging, setIsDragging, onDrop };
}
