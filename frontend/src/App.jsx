import React from 'react';
import VideoGrid from './components/VideoGrid';
import TargetUploader from './components/TargetUploader';

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">
      <header className="bg-gray-800 p-4 border-b border-gray-700 flex justify-between items-center shadow-lg">
        <h1 className="text-2xl font-bold tracking-wider text-red-500 flex items-center gap-2">
          <span className="w-3 h-3 bg-red-600 rounded-full animate-pulse"></span>
          SURVEILLANCE AI
        </h1>
        <div className="text-sm text-gray-400">System Status: ONLINE</div>
      </header>

      <main className="p-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Video Feed Area */}
        <div className="lg:col-span-3 space-y-4">
          <div className="bg-gray-800 rounded-xl p-4 shadow-xl border border-gray-700">
            <h2 className="text-lg font-semibold mb-3 text-gray-300">Live Feeds</h2>
            <VideoGrid />
          </div>
        </div>

        {/* Sidebar Controls */}
        <div className="lg:col-span-1 space-y-6">

          {/* Target Upload Section */}
          <div className="bg-gray-800 rounded-xl p-4 shadow-xl border border-gray-700">
            <h2 className="text-lg font-semibold mb-3 text-gray-300">Target Tracking</h2>
            <TargetUploader />
          </div>

          {/* Alerts Feed (Placeholder) */}
          <div className="bg-gray-800 rounded-xl p-4 shadow-xl border border-gray-700 h-96 overflow-hidden flex flex-col">
            <h2 className="text-lg font-semibold mb-3 text-gray-300">Live Alerts</h2>
            <div className="flex-1 overflow-y-auto space-y-2 text-sm text-gray-400">
              <div className="p-2 bg-gray-700/50 rounded border-l-2 border-green-500">
                System initialized.
              </div>
              {/* Dynamic alerts would go here */}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
