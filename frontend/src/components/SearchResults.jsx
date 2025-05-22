import React from 'react';
import './SearchResults.css';

// Basic icons - consider using a library like react-icons for better icons
const FileIcon = ({ type }) => {
  let iconText = '📄'; // Default icon
  if (type === 'video') iconText = '🎬';
  else if (type === 'audio') iconText = '🎵';
  else if (type === 'presentation') iconText = '📊';
  else if (type === 'image') iconText = '🖼️';
  return <span className="file-icon">{iconText}</span>;
};

function SearchResults({ results, onPlay }) {
  if (!results.length) {
    return <p>No results found.</p>;
  }

  return (
    <div className="search-results-container">
      <h3>Search Results</h3>
      <ul className="results-list">
        {results.map((file, index) => (
          <li key={index} className="result-item">
            <FileIcon type={file.type} />
            <span className="file-name">{file.name}</span>
            <span className="file-type-label">({file.type})</span>
            <button onClick={() => onPlay(file)} className="play-button">
              Play
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SearchResults;
