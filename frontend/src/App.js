import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import JobSearchApp from './components/JobSearchApp';
import LinkedInCallback from './components/LinkedInCallback';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<JobSearchApp />} />
          <Route path="/callback" element={<LinkedInCallback />} />
          <Route path="/test" element={<div>Test Route Working</div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 