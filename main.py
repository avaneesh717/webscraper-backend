from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_favicon(soup, base_url):
    icon_link = soup.find("link", rel=lambda x: x and 'icon' in x.lower())
    if icon_link and icon_link.get("href"):
        return urljoin(base_url, icon_link.get("href"))
    return urljoin(base_url, "/favicon.ico")

@app.get("/scrape")
async def scrape(url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Metadata
    metadata = {
        "title": soup.title.string if soup.title else urlparse(url).netloc,
        "description": "",
        "favicon": get_favicon(soup, url),
        "url": url
    }
    
    desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    if desc_tag:
        metadata["description"] = desc_tag.get("content", "")

    # Cleanup
    for tag in soup(["script", "style", "nav", "footer", "form", "svg"]):
        tag.decompose()

    # Sections
    sections = []
    seen_text = set()
    current_section = {"heading": "Overview", "content": []}

    tags_to_track = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'blockquote']
    for tag in soup.find_all(tags_to_track):
        text = tag.get_text(strip=True)
        if not text or len(text) < 3 or text in seen_text:
            continue
        seen_text.add(text)

        if tag.name.startswith('h'):
            if current_section["content"]:
                sections.append(current_section)
            current_section = {"heading": text, "content": []}
        else:
            current_section["content"].append(text)

    if current_section["content"]:
        sections.append(current_section)

    # Images
    images = []
    seen_imgs = set()
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        
        abs_url = urljoin(url, src)
        if abs_url in seen_imgs or not abs_url.startswith("http"):
            continue
        
        seen_imgs.add(abs_url)
        images.append({
            "src": abs_url,
            "alt": img.get("alt", "Scraped Image")
        })

    return {
        "metadata": metadata,
        "sections": sections,
        "images": images[:20]  # Limit to top 20 images
    }
