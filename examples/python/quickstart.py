"""PricePulse API - Python usage example"""
import requests

API_BASE = "https://incl-coupons-question-pair.trycloudflare.com"
API_KEY = "your-api-key-here"

headers = {"X-API-Key": API_KEY}

# Search Carousell SG
resp = requests.get(f"{API_BASE}/search", params={"q": "iphone 15", "site": "carousell"}, headers=headers)
for p in resp.json().get("products", [])[:3]:
    print(f"  {p['title']} - ${p['price']} ({p['site']})")

# Trending
trending = requests.get(f"{API_BASE}/trending", headers=headers).json()
print(f"Trending: {len(trending.get('products', []))} items")

# Arbitrage opportunities
arb = requests.get(f"{API_BASE}/arbitrage", headers=headers).json()
for a in arb.get("opportunities", [])[:3]:
    print(f"  Arbitrage: {a['title']} - save ${a['price_diff']}")
