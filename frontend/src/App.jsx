import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './components/HomePage';
import YouTubePage from './components/YouTubePage';
import UploadPage from './components/UploadPage';
import DoxologiaPage from './components/DoxologiaPage';
import YouTubeDownloadPage from './components/YouTubeDownloadPage';
import PlaylistsPage from './components/PlaylistsPage';

// Import global styles and component-specific styles
import './index.css'; // Global styles
// SideMenu.css and Layout.css are imported directly in their respective components.

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="youtube" element={<YouTubePage />} />
          <Route path="upload" element={<UploadPage />} />
          <Route path="doxologia" element={<DoxologiaPage />} />
          <Route path="youtube-download" element={<YouTubeDownloadPage />} />
          <Route path="playlists" element={<PlaylistsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
