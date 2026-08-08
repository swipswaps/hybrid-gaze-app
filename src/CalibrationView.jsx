import React, { useState } from 'react';
const calibrationPoints = [
  { x: '10%', y: '10%' }, { x: '50%', y: '10%' }, { x: '90%', y: '10%' },
  { x: '10%', y: '50%' }, { x: '50%', y: '50%' }, { x: '90%', y: '50%' },
  { x: '10%', y: '90%' }, { x: '50%', y: '90%' }, { x: '90%', y: '90%' }
];
export default function CalibrationView({ onComplete }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [samples, setSamples] = useState([]);
  const handlePointClick = (pt) => {
    const updated = [...samples, { target: pt, timestamp: Date.now() }];
    setSamples(updated);
    if (currentIndex + 1 < calibrationPoints.length) setCurrentIndex(currentIndex + 1);
    else onComplete(updated);
  };
  const currentPt = calibrationPoints[currentIndex];
  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'absolute', left: currentPt.x, top: currentPt.y, transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
        <button onClick={() => handlePointClick(currentPt)} style={{ width: '30px', height: '30px', borderRadius: '50%', background: '#00ffcc', border: '3px solid #fff', cursor: 'pointer', boxShadow: '0 0 15px #00ffcc' }} />
        <div style={{ color: '#fff', fontSize: '0.8rem', marginTop: '8px', fontFamily: 'monospace' }}>
          Calibration Point {currentIndex + 1} / {calibrationPoints.length}
        </div>
      </div>
    </div>
  );
}
