const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const pdfParse = require('pdf-parse');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(cors());
app.use(express.static(path.join(__dirname, 'public'))); // Serve frontend files

// Helper function to generate summaries (mock implementation)
function generateSummary(text) {
    // Split the text into sections (mock logic for demonstration)
    const sections = text.split('\n').filter(line => line.trim().length > 0 && line.includes(':'));
    return sections.map(section => {
        const [topic, ...summaryParts] = section.split(':');
        return {
            topic: topic.trim(),
            summary: summaryParts.join(':').trim() || `Summary of ${topic.trim()}`
        };
    });
}

app.post('/analyze-pdf', upload.single('file'), async (req, res) => {
    const file = req.file;

    if (!file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    try {
        // Read and parse the uploaded PDF
        const dataBuffer = fs.readFileSync(file.path);
        const pdfData = await pdfParse(dataBuffer);

        // Generate summaries based on the extracted text
        const summaries = generateSummary(pdfData.text);

        // Format the response
        const response = [
            {
                fileName: file.originalname,
                topics: summaries
            }
        ];

        // Send the response
        res.json(response);
    } catch (error) {
        console.error('Error processing PDF:', error);
        res.status(500).json({ error: 'Failed to process PDF' });
    } finally {
        // Clean up the uploaded file
        fs.unlinkSync(file.path);
    }
});

const PORT = 5001;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});