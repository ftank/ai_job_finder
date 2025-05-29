import React from 'react';
import ResumeAnalyzer from './components/ResumeAnalyzer';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Resume Analyzer</h1>
      </header>
      <div className="container">
        <ResumeAnalyzer />
      </div>
    </div>
  );
}

export default App; 