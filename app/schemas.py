from pydantic import BaseModel, HttpUrl

# Validiamo l'url di input per lo scraping
class ScrapeRequest(BaseModel):
    url: HttpUrl