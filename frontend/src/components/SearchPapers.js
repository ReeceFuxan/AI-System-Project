import React, { useState } from "react";
import axios from "axios";
import { TextField, Button } from "@mui/material";

const SearchPapers = () => {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);

    const handleSearch = async () => {
        if (!query) return;
        try {
            const response = await axios.get(`http://127.0.0.1:8000/search_papers?query=${query}`);
            setResults(response.data.results);
        } catch (error) {
            console.error("Search failed", error);
        }
    };

    return (
        <div>
            <h2>Search Papers</h2>
            <TextField label="Search" value={query} onChange={(e) => setQuery(e.target.value)} />
            <Button variant="contained" onClick={handleSearch}>Search</Button>
            <ul>
                {results.map((paper) => (
                    <li key={paper.ID}>{paper.Title} by {paper.Author}</li>
                ))}
            </ul>
        </div>
    );
};

export default SearchPapers;