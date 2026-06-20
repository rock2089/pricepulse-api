---
title: "Building PricePulse: A Real-time Price API for Southeast Asian E-commerce"
published: false
description: "How I built a price comparison API scraping Carousell SG and Amazon SG"
tags: api, python, webdev, opensource
---

## The Problem

If you're building anything e-commerce related for Southeast Asia, you quickly realize one thing: **there's no unified price data API**. 

Amazon has a Product Advertising API, but it's limited. Carousell has no public API at all. Lazada and Shopee? Even more locked down.

Yet the demand is real - developers building price comparison tools, dropshipping apps, market research platforms all need this data.

## The Solution: PricePulse

PricePulse is a REST API that provides real-time product price data from **Carousell Singapore** and **Amazon SG** through a simple JSON API.

### Architecture

```
User → Cloudflare Tunnel → Nginx → FastAPI (Python)
                                        ↓
                            ┌─── Carousell Scraper ───┐
                            │   Amazon SG Scraper     │
                            └────────────────────────┘
                                        ↓
                                    SQLite DB
                                    (2600+ products)
```

### Tech Stack

- **Python FastAPI** for the REST layer
- **Nginx** as reverse proxy + static file serving
- **Cloudflare Tunnel** for China accessibility
- **SQLite** for product data storage
- **Singapore VPS** (Alibaba Cloud) for hosting

### Key Features

1. **Multi-marketplace search** - Query both platforms with one API call
2. **Price history tracking** - See how prices change over time
3. **Arbitrage detection** - Find products cheaper on one marketplace vs the other
4. **Trending products** - What's hot right now
5. **Category browsing** - Explore by category

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /search?q=<keyword>&site=<carousell|amazon>` | Search products |
| `GET /trending` | Trending products |
| `GET /arbitrage` | Cross-marketplace price differences |
| `GET /categories` | Browse categories |
| `GET /health` | API health check |

### Sample Response

```json
{
  "products": [
    {
      "title": "iPhone 15 Pro Max 256GB",
      "price": 1888.0,
      "currency": "SGD",
      "site": "carousell",
      "seller": "techshop_sg"
    }
  ],
  "total": 42
}
```

### Challenges

**Data freshness** - Running scrapers on a schedule to keep data current
**Anti-bot measures** - E-commerce sites don't like scrapers
**China accessibility** - The server is in Singapore but our target users include China-based developers. Solved with Cloudflare Tunnel.

### Pricing

- **Free**: 100 queries/day (no credit card)
- **Starter**: $10/month (1,000 queries/day)
- **Pro**: $50/month (10,000 queries/day)

### What's Next

- Add Lazada Indonesia and Thailand
- Price alerts via webhook
- Historical data export
- SDK for Python, Node.js, Go

## Try It

- **Live demo**: [incl-coupons-question-pair.trycloudflare.com](https://incl-coupons-question-pair.trycloudflare.com)
- **Pricing**: [Pricing page](https://incl-coupons-question-pair.trycloudflare.com/pricing)
- **GitHub**: [github.com/rock2089/pricepulse-api](https://github.com/rock2089/pricepulse-api)
