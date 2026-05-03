from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.concurrency import run_in_threadpool
from markdown_pdf import MarkdownPdf, Section
from meeting_summarization import MeetingSummarizationPipeLine
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(title="Meeting Summarizer Audio Recording Service")

# Create directories if they do not exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Renders the beautiful audio recording and uploading UI.
    """
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Endpoint to handle an uploaded audio file from the frontend.
    The file can come from a direct file upload or the MediaRecorder API.
    """
    try:
        # Generate a unique filename using uuid
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'wav'
        unique_filename = f"audio_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            # Read and save in chunks
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Successfully saved audio file to {file_path}")

        # Run the summarization pipeline
        pipeline = MeetingSummarizationPipeLine(whisper_model_size="base")
        report = await run_in_threadpool(pipeline.run, file_path)
        
        summary_txt_path = report["summary"]

        # Convert the generated markdown summary to a PDF file
        pdf_filename = f"summary_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path_full = os.path.join(UPLOAD_DIR, pdf_filename)
        
        with open(summary_txt_path, "r", encoding="utf-8") as f:
            summary_content = f.read()
            
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(summary_content))
        pdf.save(pdf_path_full)
        
        logger.info(f"Successfully created PDF summary at {pdf_path_full}")

        # Return the generated PDF to the browser as an attachment
        return FileResponse(
            path=pdf_path_full,
            media_type="application/pdf",
            filename="meeting_summary.pdf"
        )

    except Exception as e:
        logger.error(f"Error handling file upload: {str(e)}")
        return {"status": "error", "message": f"Failed to upload audio: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Optional start via python script execution
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
