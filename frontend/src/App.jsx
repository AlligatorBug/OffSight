import React from 'react';
import Navbar from './components/Navbar';
import UploadZone from './components/UploadZone';
import VideoPlayer from './components/VideoPlayer';
import PlayerPanel from './components/PlayerPanel';
import StatCards from './components/StatCards';

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main>
        <UploadZone />
        <VideoPlayer />
        <StatCards />
      </main>
      <PlayerPanel />
    </div>
  );
}
