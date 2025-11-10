import React from 'react';

const Navbar = ({ onMenuClick }) => {
  return (
    <header className="navbar">
      <button className="menu-btn" onClick={onMenuClick} aria-label="Toggle sidebar">☰</button>
      <h1 className="app-title">Document Manager</h1>
      <nav className="nav-links">
        <a href="#" onClick={(e) => e.preventDefault()}>Docs</a>
        <a href="#" onClick={(e) => e.preventDefault()}>Help</a>
        <a href="#" onClick={(e) => e.preventDefault()}>About</a>
      </nav>
    </header>
  );
};

export default Navbar;