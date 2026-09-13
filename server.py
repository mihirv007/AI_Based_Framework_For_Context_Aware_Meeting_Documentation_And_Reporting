import os
import uuid
import logging
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markdown_pdf import MarkdownPdf, Section
from meeting_summarization import MeetingSummarizationPipeLine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Meeting Summarizer Web App")

# Ensure directories exist
UPLOAD_DIR = "uploads"
for dir_name in [UPLOAD_DIR, "static", "templates"]:
    os.makedirs(dir_name, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'wav'
        unique_filename = f"audio_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Saved audio: {file_path}")

        # Run pipeline
        pipeline = MeetingSummarizationPipeLine(whisper_model_size="base")
        report = await run_in_threadpool(pipeline.run, file_path)
        
        # Convert markdown summary to PDF
        pdf_filename = f"summary_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
        
        with open(report["summary"], "r", encoding="utf-8") as f:
            pdf = MarkdownPdf(toc_level=2)
            pdf.add_section(Section(f.read()))
            pdf.save(pdf_path)
        
        logger.info(f"Created PDF: {pdf_path}")

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename="meeting_summary.pdf"
        )

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)