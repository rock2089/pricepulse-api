# PricePulse API 🛍️💸

**Real-time cross-platform price comparison API for Singapore marketplaces.**

Compare prices across Carousell SG and Amazon SG instantly. Find arbitrage opportunities, track trending products, and build price-aware applications.

[![API Status](https://img.shields.io/badge/API-Live-brightgreen)](https://shop.pricepulseapi.site/pricepulse/docs)
[![Free Tier](https://img.shields.io/badge/Free-100%20req%2Fday-blue)](https://shop.pricepulseapi.site/pricepulse/docs)

## 🚀 Quick Start

```bash
# Get your free API key
curl -X POST "https://shop.pricepulseapi.site/pricepulse/api/signup?email=you@example.com"

# Search products
curl -H "X-API-Key: YOUR_KEY" \
  "https://shop.pricepulseapi.site/pricepulse/search?q=ps5&site=carousell"

# Find arbitrage (Carousell vs Amazon)
curl -H "X-API-Key: YOUR_KEY" \
  "https://shop.pricepulseapi.site/pricepulse/arbitrage?min_profit=10"
```

## 📡 Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/signup` | Get free API key (100 req/day) |
| `GET /search` | Search products by keyword |
| `GET /trending` | Hot products across platforms |
| `GET /arbitrage` | Cross-platform price gaps |
| `GET /categories` | Product categories |
| `GET /health` | API status |

**Interactive Docs:** [Swagger UI](https://shop.pricepulseapi.site/pricepulse/docs)

## 💰 Pricing

| Tier | Requests/Day | Price |
|------|-------------|-------|
| Free | 100 | $0 |
| Starter | 1,000 | $10/mo |
| Pro | 10,000 | $50/mo |
| Enterprise | Unlimited | Contact |

## 🏗️ Self-Host

```bash
pip install fastapi httpx beautifulsoup4 uvicorn
python server.py  # Runs on port 8903
```

## 🔌 Use Cases

- **Dropshippers** — Find underpriced items on Carousell, flip on Amazon
- **Price Trackers** — Monitor price changes over time
- **Market Research** — Analyze SG marketplace trends
- **Bots** — Build Telegram/Discord deal alert bots

## 📊 Data Sources

- Carousell Singapore
- Amazon Singapore

---

Built with FastAPI • Deployed on Tencent Cloud Lighthouse + Cloudflare Tunnel
