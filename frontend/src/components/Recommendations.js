import React, { useState } from "react";
import axios from "axios";
import { TextField, Button } from "@mui/material";

const Recommendations = () => {
    const [paperId, setPaperId] = useState("");
    const [recommendations, setRecommendations] = useState([]);

    const fetchRecommendations = async () => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/recommend_papers?paper_id=${paperId}`);
            setRecommendations(response.data.recommendations);
        } catch (error) {
            console.error("Failed to fetch recommendations", error);
        }
    };

    return (
        <div>
            <h2>Recommendations</h2>
            <TextField label="Paper ID" value={paperId} onChange={(e) => setPaperId(e.target.value)} />
            <Button variant="contained" onClick={fetchRecommendations}>Get Recommendations</Button>
            <ul>
                {recommendations.map((paper) => (
                    <li key={paper.paper_id}>{paper.title} - Similarity: {paper.similarity_score}</li>
                ))}
            </ul>
        </div>
    );
};

export default Recommendations;