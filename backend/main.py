from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF for PDF text extraction
import os
import requests
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend's URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# Function to generate summaries using Ollama
def generate_summary_with_ollama(text, model="llama2"):
    url = "http://localhost:11434/api/generate"  # Ollama's local API endpoint
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": f"Summarize the following text into sections with topics and summaries:\n\n{text}"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        raise Exception("Failed to connect to Ollama API. Ensure it is running on localhost:11434.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ollama API error: {e}")

# API Endpoint to upload PDF and analyze topics
@app.post("/analyze-pdf/")
async def analyze_pdf(file: UploadFile = File(...)):
    # The 'file' parameter matches the key in the frontend's FormData
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    # Save uploaded PDF
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Extract text from the PDF
    text = extract_text_from_pdf(file_path)

    # Generate summary using Ollama
    try:
        ollama_summary = generate_summary_with_ollama(text)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    # Format the response in the desired JSON structure
    response = [
        {
            "fileName": file.filename,
            "topics": [
                {
                    "topic": section.split(":")[0].strip(),
                    "summary": section.split(":")[1].strip() if ":" in section else section.strip()
                }
                for section in ollama_summary.split("\n") if section.strip()
            ]
        }
    ]

    return JSONResponse(content=response)

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)



