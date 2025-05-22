import React, { useState, useEffect } from 'react';
import SearchBar from './SearchBar';
import SearchResults from './SearchResults';
import NowPlaying from './NowPlaying';
import './HomePage.css'; // For HomePage specific styles

function HomePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [currentMedia, setCurrentMedia] = useState(null);
  const [message, setMessage] = useState(''); // For user feedback

  const handleSearch = async (term) => {
    if (!term.trim()) {
      setSearchResults([]);
      setMessage('Please enter a search term.');
      return;
    }
    setMessage('Searching...');
    try {
      const response = await fetch(`http://localhost:3001/api/files/search?term=${encodeURIComponent(term)}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSearchResults(data);
      setMessage(data.length > 0 ? '' : 'No results found.');
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
      setMessage(`Error fetching search results: ${error.message}`);
    }
  };

  const handlePlay = async (file) => {
    setMessage(`Attempting to play ${file.name}...`);
    try {
      const response = await fetch('http://localhost:3001/api/files/play', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filePath: file.path, fileType: file.type }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }
      setCurrentMedia(file);
      setMessage(data.message || `Playing ${file.name}`);
    } catch (error) {
      console.error('Play error:', error);
      setCurrentMedia(null);
      setMessage(`Error playing file: ${error.message}`);
    }
  };

  // Optional: Debounce search
  // useEffect(() => {
  //   const timerId = setTimeout(() => {
  //     if (searchTerm) {
  //       handleSearch(searchTerm);
  //     } else {
  //       setSearchResults([]);
  //     }
  //   }, 500); // Debounce by 500ms
  //   return () => clearTimeout(timerId);
  // }, [searchTerm]);


  return (
    <div className="home-page-container">
      <header className="home-page-header">
        <h1>Sonoplasta Virtual</h1>
      </header>
      <main className="home-page-main">
        <SearchBar
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm} // Pass setSearchTerm for direct updates or handle debouncing here
          onSearch={handleSearch} // Explicit search on submit
        />
        {message && <p className="user-message">{message}</p>}
        <NowPlaying currentMedia={currentMedia} />
        <SearchResults results={searchResults} onPlay={handlePlay} />
      </main>
    </div>
  );
}

export default HomePage;
