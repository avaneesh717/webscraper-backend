# 🐍 FastAPI Backend – Web Scraper API

This is the backend service for a full stack web scraping application. It exposes a `/scrape` endpoint which takes a URL as input and returns structured data (section-wise text content) from that page.

Deployed on **Render** and ready to communicate with the frontend React app hosted on Vercel.

---

## 🚀 Features

- 🌐 Accepts any URL and scrapes its readable content (headings, paragraphs, lists).
- 🧠 Organizes data into sections based on `h1`, `h2`, `h3` tags and their respective content (`p`, `li`).
- 🔄 CORS enabled for smooth cross-origin communication.
- 🧪 Accessible Swagger documentation via `/docs` (if needed).
- 🪶 Lightweight and ideal for dynamic content extraction.

---

## 🛠️ Tech Stack

- **FastAPI** – async Python web framework.
- **BeautifulSoup** – for HTML parsing.
- **Requests** – for making HTTP requests.
- **Uvicorn** – ASGI server (via Render).
- **Render** – for deployment.

---

## 🌐 API Endpoint

### `GET /scrape`

**Query Parameter**:
- `url` (string): The full URL of the web page you want to scrape.
