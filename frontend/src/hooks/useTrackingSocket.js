import { useCallback, useRef, useState } from 'react';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

/**
 * Drives the OffSight processing socket end-to-end. The protocol, matching
 * backend/websocket.py exactly:
 *
 *   open
 *   →  send meta JSON                       (e.g. { squad: [...] })
 *   ←  {"status":"received", message: "...waiting for video..."}
 *   →  send video bytes (ArrayBuffer)
 *   ←  {"status":"received", message: "...initialising pipeline..."}
 *   ←  {"status":"processing", message: "...starting processing..."}
 *   ←  {"status":"processing", frame, total, detections: [...]}   × N
 *   ←  {"status":"done"}
 *   ←  binary: annotated video bytes
 */
export default function useTrackingSocket() {
  const wsRef = useRef(null);
  const videoSentRef = useRef(false);
  const doneRef = useRef(false);

  const [status, setStatus] = useState('idle'); // idle | connecting | sending | processing | done | error
  const [message, setMessage] = useState('');
  const [frame, setFrame] = useState(0);
  const [total, setTotal] = useState(0);
  const [detections, setDetections] = useState([]);
  const [resultUrl, setResultUrl] = useState(null);
  const [error, setError] = useState(null);

  const start = useCallback((meta, videoFile) => {
    setStatus('connecting');
    setError(null);
    setResultUrl(null);
    setFrame(0);
    setTotal(0);
    setDetections([]);
    videoSentRef.current = false;
    doneRef.current = false;

    const ws = new WebSocket(WS_URL);
    ws.binaryType = 'arraybuffer';
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('sending');
      ws.send(JSON.stringify(meta));
    };

    ws.onmessage = (event) => {
      // Binary frame = the final annotated video, always sent after "done"
      if (typeof event.data !== 'string') {
        const blob = new Blob([event.data], { type: 'video/mp4' });
        setResultUrl(URL.createObjectURL(blob));
        return;
      }

      const payload = JSON.parse(event.data);

      if (payload.message) setMessage(payload.message);

      if (payload.status === 'received' && !videoSentRef.current) {
        // First "received" ack is for the metadata — now send the video bytes.
        videoSentRef.current = true;
        videoFile
          .arrayBuffer()
          .then((buf) => ws.send(buf))
          .catch((err) => {
            setStatus('error');
            setError(err.message);
          });
        return;
      }

      if (payload.status === 'processing') {
        setStatus('processing');
        if (typeof payload.frame === 'number') setFrame(payload.frame);
        if (typeof payload.total === 'number') setTotal(payload.total);
        if (payload.detections) setDetections(payload.detections);
        return;
      }

      if (payload.status === 'done') {
        setStatus('done');
        doneRef.current = true;
        setMessage('Processing complete — receiving annotated video…');
      }
    };

    ws.onerror = () => {
      setStatus('error');
      setError('Connection error — check that the backend is running.');
    };

    ws.onclose = (event) => {
      wsRef.current = null;
      if (!doneRef.current) {
        setStatus('error');
        setError(
          event.code === 1009
            ? 'Video too large for the WebSocket connection — increase --ws-max-size on the backend.'
            : `Connection closed unexpectedly (code ${event.code}).`
        );
      }
    };
  }, []);

  const stop = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  return { status, message, frame, total, detections, resultUrl, error, start, stop };
}