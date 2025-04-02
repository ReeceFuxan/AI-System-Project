import React, { useState } from "react";
import axios from "axios";
import { Button, TextField } from "@mui/material";

const UploadPaper = () => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            setMessage("Please select a file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("http://127.0.0.1:8000/upload_paper", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setMessage(`Upload successful: ${response.data.filename}`);
        } catch (error) {
            setMessage("Upload failed. Try again.");
        }
    };

    return (
        <div>
            <h2>Upload Paper</h2>
            <input type="file" onChange={handleFileChange} />
            <Button variant="contained" color="primary" onClick={handleUpload}>
                Upload
            </Button>
            <p>{message}</p>
        </div>
    );
};

export default UploadPaper;