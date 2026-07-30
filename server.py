"""
PricePulse API Server - FastAPI
Deploy: SG server port 8903 via Caddy
"""
import os
import time
import hashlib
import sqlite3
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from bs4 import BeautifulSoup
import uvicorn

# Config
API_KEYS = set(os.getenv("PRICEPULSE_KEYS", "").split(","))
RATE_LIMIT = {}  # api_key -> [timestamps]
CACHE = {}       # query -> (data, timestamp)
CACHE_TTL = 300  # 5 min cache

DB_PATH = "/opt/pricepulse/data.db"

# ===== Database =====
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            key TEXT PRIMARY KEY,
            email TEXT,
            tier TEXT DEFAULT 'free',
            requests INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            title TEXT, price REAL, currency TEXT,
            site TEXT, url TEXT, image TEXT,
            category TEXT, condition TEXT,
            scraped_at TEXT
        )
    """)
    conn.commit()
    return conn

# ===== Scrapers =====
async def scrape_carousell(query, limit=20):
    """Scrape Carousell SG search results"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"https://www.carousell.sg/search/{query}",
                headers={"User-Agent": "PricePulse/1.0"},
                follow_redirects=True
            )
            soup = BeautifulSoup(resp.text, 'html.parser')
            products = []
            cards = soup.select('[data-testid^="listing-card"]')[:limit]
            for card in cards:
                title_el = card.select_one('p[style*="line-clamp:2"]')
                price_el = card.select_one('p[title]')
                img_el = card.select_one('img')
                link_el = card.select_one('a')
                if title_el:
                    products.append({
                        "title": title_el.text.strip()[:100],
                        "price": float(price_el.text.strip().replace("S$","").replace(",","")) if price_el else 0,
                        "currency": "SGD",
                        "site": "carousell",
                        "url": f"https://carousell.sg{link_el['href']}" if link_el else "",
                        "image": img_el['src'] if img_el else "",
                    })
            return products
    except Exception as e:
        print(f"Carousell scrape error: {e}")
        return []

async def scrape_amazon(query, limit=20):
    """Scrape Amazon SG search results"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"https://www.amazon.sg/s?k={query}",
                headers={"User-Agent": "PricePulse/1.0"}
            )
            soup = BeautifulSoup(resp.text, 'html.parser')
            products = []
            cards = soup.select('[data-component-type="s-search-result"]')[:limit]
            for card in cards:
                title_el = card.select_one('h2 span')
                price_whole = card.select_one('.a-price-whole')
                price_fraction = card.select_one('.a-price-fraction')
                img_el = card.select_one('img.s-image')
                link_el = card.select_one('h2 a')
                if title_el:
                    price = 0
                    try:
                        price_str = (price_whole.text if price_whole else '0') + '.' + (price_fraction.text if price_fraction else '00')
                        price = float(price_str.replace(',',''))
                    except: pass
                    products.append({
                        "title": title_el.text.strip()[:150],
                        "price": price,
                        "currency": "SGD",
                        "site": "amazon_sg",
                        "url": f"https://amazon.sg{link_el['href']}" if link_el else "",
                        "image": img_el['src'] if img_el else "",
                    })
            return products
    except Exception as e:
        print(f"Amazon scrape error: {e}")
        return []

# ===== App =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="PricePulse API",
    description="Real-time price comparison for Carousell SG, Amazon SG. Search, trends, and arbitrage.",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ===== Auth =====
def check_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(401, "X-API-Key header required. Get free key: POST /api/signup")
    conn = init_db()
    row = conn.execute("SELECT key, tier, requests FROM api_keys WHERE key=?", (x_api_key,)).fetchone()
    if not row:
        raise HTTPException(403, "Invalid API key")
    # Rate limit
    now = time.time()
    limits = {"free": 100, "starter": 1000, "pro": 10000, "enterprise": 100000}
    limit = limits.get(row[1], 100)
    if x_api_key not in RATE_LIMIT:
        RATE_LIMIT[x_api_key] = []
    RATE_LIMIT[x_api_key] = [t for t in RATE_LIMIT[x_api_key] if now - t < 86400]
    if len(RATE_LIMIT[x_api_key]) >= limit:
        raise HTTPException(429, f"Rate limit exceeded ({limit}/day). Upgrade at rapidapi.com")
    RATE_LIMIT[x_api_key].append(now)
    conn.execute("UPDATE api_keys SET requests = requests + 1 WHERE key=?", (x_api_key,))
    conn.commit()
    return row

# ===== Endpoints =====
@app.post("/api/signup")
async def signup(email: str = Query(...)):
    """Get a free API key"""
    key = hashlib.sha256(f"{email}{time.time()}".encode()).hexdigest()[:32]
    conn = init_db()
    try:
        conn.execute("INSERT INTO api_keys (key, email) VALUES (?, ?)", (key, email))
        conn.commit()
        return {"api_key": key, "tier": "free", "limit": "100 requests/day"}
    except:
        raise HTTPException(400, "Email already registered")

@app.get("/search")
async def search(q: str, site: str = None, limit: int = 20, user=Header(None, alias="X-API-Key")):
    check_key(user)
    cache_key = f"search:{q}:{site}:{limit}"
    if cache_key in CACHE:
        data, ts = CACHE[cache_key]
        if time.time() - ts < CACHE_TTL:
            return data

    products = []
    if not site or site == "carousell":
        products.extend(await scrape_carousell(q, limit))
    if not site or site in ("amazon_sg", "amazon"):
        products.extend(await scrape_amazon(q, limit))

    result = {"query": q, "total": len(products), "products": products}
    CACHE[cache_key] = (result, time.time())
    return result

@app.get("/trending")
async def trending(source: str = None, limit: int = 20, user=Header(None, alias="X-API-Key")):
    check_key(user)
    # Return top searched items as trending
    queries = ["iphone", "ps5", "nike", "samsung", "macbook", "switch", "airpods", "gpu"]
    all_products = []
    for q in queries[:4]:
        products = await scrape_carousell(q, limit // 4)
        all_products.extend(products)
    return {"products": all_products[:limit], "total": len(all_products[:limit])}

@app.get("/arbitrage")
async def arbitrage(min_profit: float = 10, limit: int = 20, user=Header(None, alias="X-API-Key")):
    check_key(user)
    queries = ["iphone 15", "ps5", "airpods pro"]
    opportunities = []
    for q in queries:
        caro = await scrape_carousell(q, 10)
        amz = await scrape_amazon(q, 10)
        for c in caro[:3]:
            for a in amz[:3]:
                diff = abs(c['price'] - a['price'])
                if diff >= min_profit:
                    opportunities.append({
                        "title": c['title'][:80],
                        "carousell_price": c['price'],
                        "amazon_price": a['price'],
                        "price_diff": round(diff, 2),
                        "cheaper_on": "carousell" if c['price'] < a['price'] else "amazon_sg"
                    })
    return {"opportunities": opportunities[:limit]}

@app.get("/categories")
async def categories(source: str = None, user=Header(None, alias="X-API-Key")):
    check_key(user)
    return {"categories": [
        "Electronics", "Fashion", "Home & Living", "Toys & Games",
        "Beauty", "Sports", "Books", "Automotive"
    ]}

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/docs", include_in_schema=False)
async def custom_docs():
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/openapi.json", title="PricePulse API")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8903)
