import React from 'react';
import { Link } from 'react-router-dom';
import './SideMenu.css';

function SideMenu() {
  return (
    <div className="side-menu">
      <h2>Menu</h2>
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/youtube">YouTube</Link></li>
        <li><Link to="/upload">Upload</Link></li>
        <li><Link to="/doxologia">Doxologia</Link></li>
        <li><Link to="/youtube-download">Download YouTube</Link></li>
        <li><Link to="/playlists">Playlists</Link></li>
      </ul>
    </div>
  );
}

export default SideMenu;
