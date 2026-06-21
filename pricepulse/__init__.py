"""PricePulse API Client"""
import requests

BASE_URL = "https://incl-coupons-question-pair.trycloudflare.com"


class PricePulse:
    """Client for the PricePulse API - real-time price monitoring."""

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["X-API-Key"] = api_key

    def _get(self, path, params=None):
        resp = requests.get(f"{BASE_URL}{path}", params=params, headers=self.headers, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def search(self, query, source=None, limit=20):
        """Search products across marketplaces."""
        params = {"q": query, "limit": limit}
        if source:
            params["source"] = source
        return self._get("/search", params)

    def trending(self, source=None, limit=20):
        """Get trending products."""
        params = {"limit": limit}
        if source:
            params["source"] = source
        return self._get("/trending", params)

    def arbitrage(self, min_profit=10, limit=20):
        """Find cross-platform arbitrage opportunities."""
        return self._get("/arbitrage", {"min_profit": min_profit, "limit": limit})

    def categories(self, source=None):
        """Browse product categories."""
        params = {}
        if source:
            params["source"] = source
        return self._get("/categories", params)

    def health(self):
        """Check API health."""
        return self._get("/health")
