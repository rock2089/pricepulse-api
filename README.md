<div align="center">
  <h1>PricePulse API</h1>
  <p><strong>Real-time price data for Southeast Asian & European e-commerce</strong></p>
  <p>
    <a href="https://incl-coupons-question-pair.trycloudflare.com">
      <img src="https://img.shields.io/badge/live-demo-brightgreen?style=flat-square" alt="Live Demo"/>
    </a>
    <a href="https://incl-coupons-question-pair.trycloudflare.com/pricing">
      <img src="https://img.shields.io/badge/pricing-free%20tier-blue?style=flat-square" alt="Pricing"/>
    </a>
    <img src="https://img.shields.io/badge/products-5755-orange?style=flat-square" alt="Products"/>
    <img src="https://img.shields.io/badge/sites-3-brightgreen?style=flat-square" alt="Sites"/>
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/>
  </p>
</div>

---

Search and compare product prices across **Carousell Singapore**, **Amazon SG**, and **Vinted Europe** in real-time. 5,755+ products indexed with daily updates.

## Supported Markets

| Marketplace | Region | Products |
|-------------|--------|:--------:|
| Carousell SG | 🇸🇬 Singapore | 2,692 |
| Amazon SG | 🇸🇬 Singapore | — |
| Vinted | 🇪🇺 Europe | 3,061 |

## ✨ Features

- **Multi-marketplace search** — Query all supported marketplaces
- **Trending products** — See what's hot right now
- **Price history** — Track price changes over time
- **Arbitrage detection** — Find cross-marketplace opportunities
- **Category browsing** — Explore products by category
- **REST API** — Clean JSON responses, easy to integrate

## 🚀 Quick Start

```bash
# 1. Get your free API key
curl -X POST https://incl-coupons-question-pair.trycloudflare.com/api/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com"}'

# 2. Search for products
curl "https://incl-coupons-question-pair.trycloudflare.com/search?q=iphone&site=carousell" \
  -H "X-API-Key: ***"

# 3. Check trending items
curl "https://incl-coupons-question-pair.trycloudflare.com/trending" \
  -H "X-API-Key: ***"
```

## 💰 Pricing

| Plan | Queries / Day | Price |
|------|:-------------:|:-----:|
| **Free** | 100 | **$0** |
| **Starter** | 1,000 | **$10/mo** |
| **Pro** | 10,000 | **$50/mo** |

> Get started free at [incl-coupons-question-pair.trycloudflare.com](https://incl-coupons-question-pair.trycloudflare.com)

## 🔧 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /search?q=<keyword>&site=<site>` | Search products |
| `GET /trending` | Trending products |
| `GET /categories` | Browse categories |
| `GET /arbitrage` | Cross-marketplace price differences |
| `GET /health` | API health check |

## 🛠 Tech Stack

- **Backend:** Python FastAPI
- **Data:** Automated scrapers (daily updates)
- **Hosting:** Singapore VPS
- **Proxy:** Cloudflare Tunnel

## 📝 License

MIT — see [LICENSE](LICENSE) for details.
