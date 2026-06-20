# PricePulse API

[![Status](https://img.shields.io/badge/status-active-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

Real-time product price data from **Carousell Singapore** and **Amazon SG**. Search products by keyword, track price trends, and find arbitrage opportunities between marketplaces.

## Quick Start

```bash
# Get your free API key
curl -X POST https://incl-coupons-question-pair.trycloudflare.com/api/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com"}'

# Search for products
curl "https://incl-coupons-question-pair.trycloudflare.com/search?q=iphone&site=carousell" \
  -H "X-API-Key: YOUR_API_KEY"
```

## Pricing

| Plan | Queries/day | Price |
|------|------------|-------|
| Free | 100 | $0 |
| Starter | 1,000 | $10/month |
| Pro | 10,000 | $50/month |

## Features

- Search products across Carousell SG and Amazon SG
- Trending products endpoint
- Price history tracking
- Arbitrage detection between marketplaces
- REST API with JSON responses

## Docs

Full API documentation at [incl-coupons-question-pair.trycloudflare.com](https://incl-coupons-question-pair.trycloudflare.com)
Pricing at [incl-coupons-question-pair.trycloudflare.com/pricing](https://incl-coupons-question-pair.trycloudflare.com/pricing)
