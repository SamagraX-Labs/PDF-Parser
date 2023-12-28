from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Header, HTTPException, Depends
from celery import Celery
from tempfile import NamedTemporaryFile
import os
from src.marker_english.convert_single import main as convert_single_english
from src.marker_hindi.convert_single import main as convert_single_hindi

app = FastAPI()

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

def process_pdf(filename: str, language: str, file: UploadFile=File(...)):
    try:
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write(file.file.read())

        if language == 'en':
            convert_single_english()  
            print(f'Processing {filename} in English')
        elif language == 'hi':
            print(f'Processing {filename} in Hindi')

    finally:
        file.file.close()
        os.remove(temp_filename)

async def get_language_header(language: str = Header(default=None)):
    if language is None:
        raise HTTPException(status_code=400, detail="Language header is required")
    return language

@app.post("/process-pdf")
async def process_pdf(background_tasks: BackgroundTasks, language: str = Depends(get_language_header), file: UploadFile=File(...)):
    background_tasks.add_task(process_pdf, file.filename, language)
    return {"message": "PDF processing started"}
