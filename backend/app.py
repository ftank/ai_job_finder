from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from resume_analyzer import ResumeAnalyzer
import os
import shutil
from typing import Dict, Any

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize ResumeAnalyzer
analyzer = ResumeAnalyzer()

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze a resume PDF file
    
    Args:
        file (UploadFile): The uploaded PDF file
        
    Returns:
        dict: Analysis results
    """
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save the uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the resume
        results = analyzer.process_resume(file_path)
        
        # Clean up the uploaded file
        os.remove(file_path)
        
        return results
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 