import React from 'react';
import './NowPlaying.css';

function NowPlaying({ currentMedia }) {
  if (!currentMedia) {
    return (
      <div className="now-playing-container placeholder">
        <p>No media selected. Search and press play!</p>
      </div>
    );
  }

  return (
    <div className="now-playing-container">
      <h3>Now Playing</h3>
      <p className="now-playing-info">
        <span className="now-playing-name">{currentMedia.name}</span>
        <span className="now-playing-type">({currentMedia.type})</span>
      </p>
    </div>
  );
}

export default NowPlaying;
