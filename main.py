from fastapi import FastAPI, BackgroundTasks
from celery import Celery
from app.tasks.process_pdf import process_pdfs_in_directory

app = FastAPI()

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.get("/process-pdfs-in-directory/{directory_path}")
async def process_pdfs(directory_path: str, background_tasks: BackgroundTasks):
    task = process_pdfs_in_directory.delay(directory_path)  # Use the new function

    response = {"status": "Processing PDFs in the directory", "task_id": task.id}
    
    background_tasks.add_task(process_pdfs_in_directory, directory_path)  # Use the new function

    return response