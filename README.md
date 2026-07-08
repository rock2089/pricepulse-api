# PricePulse — Southeast Asian E-Commerce Price Monitoring API

[![PyPI version](https://img.shields.io/pypi/v/pricepulse)](https://pypi.org/project/pricepulse/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://pypi.org/project/pricepulse/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Free 100 req/day](https://img.shields.io/badge/free-100%20req%2Fday-brightgreen)](https://incl-coupons-question-pair.trycloudflare.com)

**Real-time product price data from Carousell SG, Amazon SG, and Vinted.**  
Free tier: 100 requests/day — no credit card required.

```bash
pip install pricepulse
```

```python
import pricepulse
client = pricepulse.Client(api_key="your_key")
results = client.search("ps5", site="carousell")
```

## Features

- 🔍 **Search** — Find products by keyword across platforms
- 📈 **Trending** — See what's popular right now
- 💰 **Arbitrage** — Discover cross-platform price differences
- 🏷️ **Categories** — Browse structured categories
- 📊 **Compare** — Compare prices across Carousell, Amazon SG, Vinted

## Quick Start

### 1. Get your free API key

```bash
curl -X POST https://incl-coupons-question-pair.trycloudflare.com/api/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com"}'
```

### 2. Make your first request

```bash
curl "https://incl-coupons-question-pair.trycloudflare.com/search?q=laptop" \
  -H "X-API-Key: your_api_key"
```

### 3. Or use the Python client

```python
from pricepulse import Client

api = Client(api_key="your_api_key")
products = api.search("iphone", site="carousell")
for p in products[:5]:
    print(f"{p['title']} — ${p['price']}")
```

## Pricing

| Tier | Price | Requests/day | Best for |
|------|-------|-------------|----------|
| Free | $0 | 100 | Try it out |
| Starter | $10/month | 1,000 | Hobby projects |
| Pro | $50/month | 10,000 | Production apps |

## API Reference

Full API docs at [`/docs`](https://incl-coupons-question-pair.trycloudflare.com/docs) (Swagger UI).

## Data Sources

- **Carousell SG** — Singapore's largest peer-to-peer marketplace
- **Amazon SG** — Amazon Singapore
- **Vinted** — Second-hand fashion marketplace

## Use Cases

- Price tracking and alerts
- E-commerce research and analysis
- Cross-platform arbitrage detection
- Market trend analysis
- Developer demos and prototypes

## Why PricePulse?

- **Free to start** — 100 requests/day, no credit card
- **No complex setup** — Single REST API, instant results
- **Southeast Asia focused** — Covers the rapidly growing SEA market
- **Open source** — Python SDK on PyPI, full source on GitHub
- **PayPal payments** — Secure, instant upgrades

## Links

- 📖 [API Documentation](https://incl-coupons-question-pair.trycloudflare.com/docs)
- 🐍 [PyPI Package](https://pypi.org/project/pricepulse/)
- 🐙 [GitHub Repository](https://github.com/rock2089/pricepulse-api)
- 📦 [Dataset (5,755 products)](https://incl-coupons-question-pair.trycloudflare.com/dataset)

## License

MIT


---

## Buy the Dataset

Need the raw data? Grab **10,800 products** (Carousell SG + Vinted EU) as CSV + JSON.

**$3.99 / 19 yuan** - Instant download after payment.

[Buy Dataset &rarr;](https://pricepulseapi.site/buy-data-pack)
