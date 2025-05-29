import React, { useState } from 'react';
import axios from 'axios';
import './ResumeAnalyzer.css';

const ResumeAnalyzer = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [analysis, setAnalysis] = useState(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.type === 'application/pdf') {
            setFile(selectedFile);
            setError(null);
        } else {
            setError('Please select a valid PDF file');
            setFile(null);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file first');
            return;
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/analyze', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.data.error) {
                setError(response.data.error);
            } else {
                setAnalysis(response.data);
            }
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred while analyzing the resume');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="resume-analyzer">     
            <form onSubmit={handleSubmit} className="upload-form">
                <div className="file-input-container">
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="file-input"
                    />
                    <button 
                        type="submit" 
                        disabled={!file || loading}
                        className="analyze-button"
                    >
                        {loading ? 'Analyzing...' : 'Analyze Resume'}
                    </button>
                </div>
            </form>

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            {analysis && !error && (
                <div className="analysis-results">
                    <h2>Analysis Results</h2>
                    
                    <section className="result-section">
                        <h3>Skills</h3>
                        <ul>
                            {analysis.skills.map((skill, index) => (
                                <li key={index}>{skill}</li>
                            ))}
                        </ul>
                    </section>

                    <section className="result-section">
                        <h3>Experience Summary</h3>
                        <p>{analysis.experience_summary}</p>
                    </section>

                    <section className="result-section">
                        <h3>Education</h3>
                        <ul>
                            {analysis.education.map((edu, index) => (
                                <li key={index}>{edu}</li>
                            ))}
                        </ul>
                    </section>

                    <section className="result-section">
                        <h3>Strengths</h3>
                        <ul>
                            {analysis.strengths.map((strength, index) => (
                                <li key={index}>{strength}</li>
                            ))}
                        </ul>
                    </section>

                    <section className="result-section">
                        <h3>Areas for Improvement</h3>
                        <ul>
                            {analysis.areas_for_improvement.map((area, index) => (
                                <li key={index}>{area}</li>
                            ))}
                        </ul>
                    </section>

                    <section className="result-section">
                        <h3>Career Level</h3>
                        <p>{analysis.career_level}</p>
                    </section>

                    <section className="result-section">
                        <h3>Recommendations</h3>
                        <ul>
                            {analysis.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                            ))}
                        </ul>
                    </section>
                </div>
            )}
        </div>
    );
};

export default ResumeAnalyzer; 