from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scrape")
async def scrape(url: str):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return {"sections": []}

    soup = BeautifulSoup(r.text, "html.parser")
    sections = []
    seen = set()
    current_section = {"heading": "Introduction", "content": []}

    # This goes in order: h1/h2/h3 start a new section, p/li get added as content
    for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
        text = tag.get_text(strip=True)
        if not text or text in seen:
            continue
        seen.add(text)

        if tag.name in ['h1', 'h2', 'h3']:
            if current_section["content"]:
                sections.append(current_section)
            current_section = {"heading": text, "content": []}
        else:
            current_section["content"].append(text)

    if current_section["content"]:
        sections.append(current_section)

    return {"sections": sections}
