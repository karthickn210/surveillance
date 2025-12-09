import React, { useEffect, useState } from 'react';

const AlertFeed = () => {
    const [alerts, setAlerts] = useState([]);
    const [selectedAlert, setSelectedAlert] = useState(null);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/alerts');
                const data = await res.json();
                setAlerts(data);
            } catch (err) {
                console.error("Failed to fetch alerts", err);
            }
        };

        // Poll every 1 second
        const interval = setInterval(fetchAlerts, 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <>
            <div className="flex-1 overflow-y-auto space-y-2 text-sm text-gray-400 p-2">
                {alerts.length === 0 && <div className="text-center italic">No active threats detected.</div>}

                {alerts.map((alert, idx) => (
                    <div
                        key={idx}
                        onClick={() => alert.image && setSelectedAlert(alert)}
                        className={`p-3 rounded border-l-4 cursor-pointer hover:bg-gray-700 transition-colors
               ${alert.type === 'weapon' ? 'bg-red-900/40 border-red-500 text-red-200' :
                                alert.type === 'target' ? 'bg-green-900/40 border-green-500 text-green-200' :
                                    'bg-yellow-900/40 border-yellow-500 text-yellow-200'}
             `}
                    >
                        <div className="flex justify-between items-start">
                            <span className="font-bold uppercase text-xs">{alert.type} ALERT</span>
                            <span className="text-xs opacity-60">
                                {new Date(alert.timestamp * 1000).toLocaleTimeString()}
                            </span>
                        </div>
                        <p className="mt-1 font-medium">{alert.message}</p>
                        {alert.image && <p className="text-xs mt-1 underline opacity-75">Click to view snapshot</p>}
                    </div>
                ))}
            </div>

            {/* Modal */}
            {selectedAlert && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4" onClick={() => setSelectedAlert(null)}>
                    <div className="bg-gray-800 p-4 rounded-xl max-w-2xl w-full shadow-2xl border border-gray-700" onClick={e => e.stopPropagation()}>
                        <div className="flex justify-between items-center mb-4 border-b border-gray-700 pb-2">
                            <h3 className="text-xl font-bold text-white uppercase">{selectedAlert.type} SNAPSHOT</h3>
                            <button onClick={() => setSelectedAlert(null)} className="text-gray-400 hover:text-white">Close</button>
                        </div>
                        <div className="rounded overflow-hidden bg-black aspect-video flex items-center justify-center">
                            <img
                                src={`http://localhost:8000${selectedAlert.image}`}
                                alt="Alert Evidence"
                                className="max-h-[60vh] object-contain"
                            />
                        </div>
                        <div className="mt-4 text-gray-300">
                            <p><span className="font-bold">Detected:</span> {selectedAlert.message}</p>
                            <p><span className="font-bold">Time:</span> {new Date(selectedAlert.timestamp * 1000).toLocaleString()}</p>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default AlertFeed;
