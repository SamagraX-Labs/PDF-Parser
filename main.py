from fastapi import FastAPI, BackgroundTasks
from celery import Celery
from app.tasks.process_pdf import main as process_pdf

app = FastAPI()

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.get("/process-pdfs-in-directory")
async def process_pdfs_in_directory(background_tasks: BackgroundTasks):
    task = process_pdf.delay()

    response = {"status": "Processing PDFs in the directory", "task_id": task.id}
    background_tasks.add_task(process_pdf())
    return response
