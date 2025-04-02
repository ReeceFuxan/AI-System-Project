import React, { useEffect, useState } from "react";
import axios from "axios";
import { Button, List, ListItem, ListItemText } from "@mui/material";

const PaperList = () => {
    const [papers, setPapers] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchPapers();
    }, []);

    const fetchPapers = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:8000/list_papers");
            setPapers(response.data.papers);
        } catch (error) {
            setError("Failed to load papers.");
        }
    };

    return (
        <div>
            <h2>Uploaded Papers</h2>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <List>
                {papers.map((paper) => (
                    <ListItem key={paper.id}>
                        <ListItemText primary={paper.title} secondary={paper.author} />
                    </ListItem>
                ))}
            </List>
        </div>
    );
};

export default PaperList;