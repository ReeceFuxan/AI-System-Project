import React, { useState } from "react";
import axios from "axios";
import { Button, TextField } from "@mui/material";

const DeletePaper = () => {
    const [paperId, setPaperId] = useState("");

    const handleDelete = async () => {
        try {
            await axios.delete(`http://127.0.0.1:8000/delete_paper/${paperId}`);
            alert("Paper deleted successfully");
        } catch (error) {
            alert("Failed to delete paper");
        }
    };

    return (
        <div>
            <h2>Delete Paper</h2>
            <TextField label="Paper ID" value={paperId} onChange={(e) => setPaperId(e.target.value)} />
            <Button variant="contained" color="secondary" onClick={handleDelete}>
                Delete
            </Button>
        </div>
    );
};

export default DeletePaper;