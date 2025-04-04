import React, { useState, useEffect } from "react";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; // Update if using a different backend URL

function App() {
    const [papers, setPapers] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState([]);

    // Fetch list of papers on component mount
    useEffect(() => {
        fetchPapers();
    }, []);

    const fetchPapers = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/list_papers`);
            setPapers(response.data.papers);
        } catch (error) {
            console.error("Error fetching papers:", error);
        }
    };

    const searchPapers = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/search_papers`, {
                params: { query: searchQuery },
            });
            setSearchResults(response.data.results);
        } catch (error) {
            console.error("Error searching papers:", error);
        }
    };

    return (
        <div>
            <h1>AI-Powered Research Paper Recommendation</h1>

            {/* Search Bar */}
            <input
                type="text"
                placeholder="Search papers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button onClick={searchPapers}>Search</button>

            {/* Search Results */}
            <h2>Search Results</h2>
            <ul>
                {searchResults.map((paper) => (
                    <li key={paper.ID}>
                        <strong>{paper.Title}</strong> by {paper.Author}
                    </li>
                ))}
            </ul>

            {/* List of Papers */}
            <h2>All Papers</h2>
            <ul>
                {papers.map((paper) => (
                    <li key={paper.id}>
                        <strong>{paper.title}</strong> by {paper.author}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default App;