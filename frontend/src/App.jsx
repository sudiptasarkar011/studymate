import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/analyze-pdf/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setAnalysis(response.data);
    } catch (error) {
      console.error("Error analyzing PDF:", error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-4">PDF Topic Analyzer</h1>
      <input type="file" onChange={handleFileChange} className="mb-4 p-2 border rounded-lg" />
      <button onClick={handleUpload} className="px-4 py-2 bg-blue-500 text-white rounded-lg">
        {loading ? "Analyzing..." : "Upload & Analyze"}
      </button>

      {analysis && (
        <div className="mt-6 p-4 bg-white shadow-lg rounded-lg w-3/4">
          <h2 className="text-xl font-semibold">Analysis Results</h2>
          <p><strong>Title:</strong> {analysis.title}</p>
          
          <h3 className="font-semibold mt-2">Topics (TF-IDF)</h3>
          <ul className="list-disc pl-6">
            {analysis.topics_tfidf.map((topic, index) => (
              <li key={index}>{topic.topic} ({(topic.relevance_score * 100).toFixed(2)}%)</li>
            ))}
          </ul>

          <h3 className="font-semibold mt-2">Topics (BERT)</h3>
          <ul className="list-disc pl-6">
            {analysis.topics_bert.map((topic, index) => (
              <li key={index}>{topic.topic} ({(topic.relevance_score * 100).toFixed(2)}%)</li>
            ))}
          </ul>

          <h3 className="font-semibold mt-2">Summary</h3>
          <p className="p-2 border rounded-md bg-gray-100">{analysis.summary}</p>
        </div>
      )}
    </div>
  );
}

export default App;
