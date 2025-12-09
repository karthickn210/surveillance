import React, { useEffect, useRef, useState } from 'react';

const VideoStream = ({ id, active }) => {
    const canvasRef = useRef(null);
    const [status, setStatus] = useState('Connecting...');

    useEffect(() => {
        if (!active) return;

        const ws = new WebSocket(`ws://localhost:8000/ws/stream/${id}`);

        ws.onopen = () => {
            setStatus('Live');
        };

        ws.onmessage = (event) => {
            const blob = new Blob([event.data], { type: 'image/jpeg' });
            const url = URL.createObjectURL(blob);
            const img = new Image();
            img.onload = () => {
                const canvas = canvasRef.current;
                if (canvas) {
                    const ctx = canvas.getContext('2d');
                    // Draw image to canvas
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                }
                URL.revokeObjectURL(url);
            };
            img.src = url;
        };

        ws.onerror = () => setStatus('Error');
        ws.onclose = () => setStatus('Disconnected');

        return () => {
            ws.close();
        };
    }, [id, active]);

    return (
        <div className="relative bg-black rounded-lg overflow-hidden aspect-video border border-gray-800 group">
            {/* Overlay Header */}
            <div className="absolute top-0 left-0 right-0 p-2 bg-gradient-to-b from-black/70 to-transparent z-10 flex justify-between items-center">
                <span className="text-sm font-mono text-white/90">CAM {id + 1}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${status === 'Live' ? 'bg-red-600 animate-pulse' : 'bg-gray-600'}`}>
                    {status}
                </span>
            </div>

            <canvas ref={canvasRef} className="w-full h-full object-contain" />

            {/* Placeholder when no stream */}
            {status !== 'Live' && (
                <div className="absolute inset-0 flex items-center justify-center text-gray-600">
                    <svg className="w-12 h-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                </div>
            )}
        </div>
    );
};

const VideoGrid = () => {
    // Simulating 4 cameras, but only enabling the first one for this demo as per backend config
    const cameras = [0, 1, 2, 3];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {cameras.map((camId) => (
                <VideoStream key={camId} id={camId} active={camId === 0} />
            ))}
        </div>
    );
};

export default VideoGrid;
