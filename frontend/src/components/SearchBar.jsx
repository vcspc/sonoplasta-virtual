import React from 'react';
import './SearchBar.css';

function SearchBar({ searchTerm, setSearchTerm, onSearch }) {
  const handleInputChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSearch(searchTerm);
  };

  return (
    <form onSubmit={handleSubmit} className="search-bar-container">
      <input
        type="text"
        placeholder="Search for media..."
        value={searchTerm}
        onChange={handleInputChange}
        className="search-input"
      />
      <button type="submit" className="search-button">Search</button>
    </form>
  );
}

export default SearchBar;
