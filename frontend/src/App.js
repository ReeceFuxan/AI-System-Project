import React, { useState, useEffect } from "react";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; // Update if using a different backend URL

function App() {
    const [papers, setPapers] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState([]);
    const [file, setFile] = useState(null);

    const uploadPaper = async () => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload_paper`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log("Upload Response:", response.data);
    } catch (error) {
      console.error("Error uploading paper:", error);
    }
  };

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
        const scholarResponse = await axios.get(`${API_BASE_URL}/search_google_scholar`, {
            params: { query: searchQuery },
        });
        const similarityResponse = await axios.get(`${API_BASE_URL}/query_similarity`, {
            params: { query: searchQuery },
        });

        const similarityMap = {};
        similarityResponse.data.results.forEach(item => {
            similarityMap[item.title.toLowerCase()] = item.similarity_score;
        });

        const enrichedResults = scholarResponse.data.map(paper => ({
            ...paper,
            similarity_score: similarityMap[paper.title.toLowerCase()] || 0,
        }));

        setSearchResults(enrichedResults);
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
            <h2>Search Results from Google Scholar</h2>
            <ul>
                {searchResults.map((paper, index) => (
                     <li key={index}>
                         <strong>{paper.title}</strong> <br />
                         <a href={paper.link} target="_blank" rel="noopener noreferrer">
                             {paper.link}
                         </a> <br />
                         <p>Published: {paper.year}</p>
                         <em>Similarity Score:</em> {paper.similarity_score.toFixed(3)}
                    </li>
                ))}
            </ul>

            {/* Upload Paper */}
             <div>
                 <h3>Upload Paper</h3>
                 <input
                    type="file"
                    onChange={(e) => setFile(e.target.files[0])}
                 />
                 <button onClick={uploadPaper}>Upload</button>
             </div>

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