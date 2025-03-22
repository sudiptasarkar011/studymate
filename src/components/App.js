import React, { useState } from 'react';

function App() {
    const [jsonOutput, setJsonOutput] = useState(null);
    const [errorMessage, setErrorMessage] = useState('');

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (file && file.type === 'application/pdf') {
            setErrorMessage(''); // Clear any previous error messages
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('http://localhost:5000/upload', {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                setJsonOutput(JSON.stringify(data, null, 2)); // Format JSON output
            } catch (error) {
                setErrorMessage('Error uploading PDF: ' + error.message);
            }
        } else {
            setErrorMessage('Please upload a valid PDF file.');
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Upload PDF and Display Summary</h1>
            <input type="file" accept="application/pdf" onChange={handleFileChange} />
            {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
            {jsonOutput && (
                <div style={{ marginTop: '20px' }}>
                    <h2>Summarized JSON Output:</h2>
                    <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
                        {jsonOutput}
                    </pre>
                </div>
            )}
        </div>
    );
}

export default App; 