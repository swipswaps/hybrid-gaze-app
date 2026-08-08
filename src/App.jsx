import React, { useEffect, useRef, useState } from 'react';

export default function App() {
  const [selectedCam, setSelectedCam] = useState(0);
  const [trackingStatus, setTrackingStatus] = useState('Initializing...');
  const [gallery, setGallery] = useState([]);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const wsUrl = `ws://${window.location.hostname}:8000/ws/track/${selectedCam}`;
    wsRef.current = new WebSocket(wsUrl);
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTrackingStatus(data.status);
      if (data.landmarks && canvasRef.current) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#00ffcc';
        data.landmarks.forEach(pt => {
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, 3, 0, 2 * Math.PI);
          ctx.fill();
        });
      }
    };
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, [selectedCam]);

  const captureFrame = async () => {
    if (!canvasRef.current) return;
    canvasRef.current.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append('file', blob, `capture_${Date.now()}.jpg`);
      try {
        const response = await fetch(`http://${window.location.hostname}:8000/api/images/process`, {
          method: 'POST',
          body: formData,
        });
        const result = await response.json();
        setGallery(prev => [...prev, result]);
      } catch (err) {
        console.error("Frame capture upload failed:", err);
      }
    }, 'image/jpeg', 0.85);
  };

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '20px', background: '#121212', color: '#fff', minHeight: '100vh' }}>
      <h2>Hybrid Sensor-Fusion Gaze & Media Interface</h2>
      <div style={{ marginBottom: '15px' }}>
        <label>Select Camera Feed: </label>
        <select value={selectedCam} onChange={(e) => setSelectedCam(Number(e.target.value))} style={{ padding: '5px', background: '#333', color: '#fff', border: '1px solid #555' }}>
          <option value={0}>Onboard Camera (0)</option>
          <option value={1}>USB Camera (1)</option>
        </select>
        <span style={{ marginLeft: '20px' }}>Status: <strong>{trackingStatus}</strong></span>
        <button onClick={captureFrame} style={{ marginLeft: '20px', padding: '6px 12px', background: '#00ffcc', color: '#000', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}>
          Capture Frame
        </button>
      </div>
      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <canvas ref={canvasRef} width={640} height={480} style={{ border: '2px solid #444', background: '#000', display: 'block' }} />
        </div>
        <div style={{ background: '#1e1e1e', padding: '15px', borderRadius: '6px', minWidth: '250px' }}>
          <h4>Captured Media Gallery</h4>
          {gallery.length === 0 ? (
            <p style={{ color: '#777', fontSize: '0.9rem' }}>No frames captured yet.</p>
          ) : (
            <ul style={{ paddingLeft: '20px', fontSize: '0.85rem' }}>
              {gallery.map((item, idx) => (
                <li key={idx} style={{ marginBottom: '8px' }}>
                  {item.filename} <span style={{ color: '#00ffcc' }}>✓</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
