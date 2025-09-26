from fastapi import FastAPI, HTTPException
from app.schemas import ScrapeRequest

app = FastAPI()

@app.post("/scrape")
# La funzione scrape_page può essere awaitable, 
# può essere sospesa senza bloccare tutto il server
async def scrape_page(req: ScrapeRequest):
    return {"message": f"Ricevuto URL {req}"}