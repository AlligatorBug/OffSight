import { useEffect, useRef, useState } from 'react';

export default function useWebSocket(url) {
  const ws = useRef(null);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    ws.current = new WebSocket(url);
    ws.current.onmessage = (e) => setMessages((prev) => [...prev, e.data]);
    return () => ws.current?.close();
  }, [url]);

  const send = (data) => ws.current?.send(data);

  return { messages, send };
}
