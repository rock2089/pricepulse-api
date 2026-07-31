#!/usr/bin/env python3
"""
Reddit Auto Promoter - GitHub Actions
Daily post to r/SideProject, r/SaaS, r/DeepSeek promoting API Shop
"""
import os, json, time, random
from urllib.request import Request, urlopen
from urllib.parse import urlencode

# ====== CONFIG ======
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USER = os.environ.get("REDDIT_USER", "")
REDDIT_PASS = os.environ.get("REDDIT_PASS", "")

SUBREDDITS = ["SideProject", "SaaS", "DeepSeek", "Python", "webdev"]

POSTS = [
    {
        "title": "I built a Stock & Crypto Price API - free tier available 🚀",
        "text": """Hey everyone!

I built **PricePulse API** - a simple REST API for real-time stock and crypto prices.

**Features:**
- 10,000+ stocks & 500+ crypto pairs
- Real-time WebSocket streaming
- REST endpoints with JSON responses
- Free tier: 100 requests/day
- No API key needed for basic endpoints

**Live Demo:** https://shop.pricepulseapi.site/pricepulse/docs

**GitHub:** https://github.com/rock2089/pricepulse-api

Would love feedback from the community! What features would make this useful for your projects?

Edit: Thanks for all the kind words! Adding more endpoints this week."""
    },
    {
        "title": "I scraped 10 Amazon categories and matched them with 1688 prices - here's what I found 💡",
        "text": """Been running a **cross-border arbitrage scanner** using Python + GitHub Actions.

Every 6 hours it scans Amazon bestsellers and matches them with 1688 wholesale prices.

**Top finds this week:**
- Silicone measuring cups: $12.99 Amazon → ¥6.50 1688 = **900%+ margin**
- Phone cases: $9.99 → ¥2.80 = **500%+**
- LED strips: $15.99 → ¥8.00 = **300%+**

All automated with GitHub Actions (free tier). Code is open source.

Would anyone be interested in a tutorial on how to build this? 

Repo: https://github.com/rock2089/pricepulse-api"""
    },
    {
        "title": "Turned my side project into a passive income source - 3 months in",
        "text": """Built a simple API product, set up autopilot with GitHub Actions, and it's been running itself for months.

**Stack:**
- FastAPI (Python)
- Caddy reverse proxy
- Cloudflare Tunnel
- GitHub Actions for monitoring + promotion
- $5/month VPS

**What I learned:**
1. Ship first, polish later
2. Free tier → paid conversions are real
3. Automation is worth 10x the effort
4. Reddit feedback > any market research

Happy to answer questions about the setup!

https://shop.pricepulseapi.site"""
    },
]

def get_reddit_token():
    """Get Reddit OAuth token"""
    if not CLIENT_ID or not CLIENT_SECRET:
        return None
    
    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth.encode()
    import base64
    auth_b64 = base64.b64encode(auth_bytes).decode()
    
    data = urlencode({
        "grant_type": "password",
        "username": REDDIT_USER,
        "password": REDDIT_PASS,
    }).encode()
    
    req = Request("https://www.reddit.com/api/v1/access_token", data=data, headers={
        "Authorization": f"Basic {auth_b64}",
        "User-Agent": "PricePulseBot/1.0",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()).get("access_token")
    except Exception as e:
        print(f"  Token error: {e}")
        return None

def post_to_reddit(subreddit: str, title: str, text: str, token: str) -> bool:
    """Submit a post to Reddit"""
    data = urlencode({
        "sr": subreddit,
        "title": title,
        "text": text,
        "kind": "self",
        "api_type": "json",
    }).encode()
    
    req = Request("https://oauth.reddit.com/api/submit", data=data, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": "PricePulseBot/1.0",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    
    try:
        with urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read())
            if "json" in result and "errors" in result["json"]:
                errors = result["json"]["errors"]
                if errors:
                    print(f"  ❌ Error: {errors}")
                    return False
                print(f"  ✅ Posted! URL: {result['json']['data']['url']}")
                return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    return False

def main():
    print("=" * 60)
    print(f"📢 Reddit Auto Promoter - {time.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    token = get_reddit_token()
    if not token:
        print("\n⚠️  REDDIT API 未配置")
        print("需要设置 GitHub Secrets:")
        print("  REDDIT_CLIENT_ID")
        print("  REDDIT_CLIENT_SECRET")
        print("  REDDIT_USER")
        print("  REDDIT_PASS")
        print("\n去 https://www.reddit.com/prefs/apps 创建App获取")
        return
    
    # Pick a random post template
    post = random.choice(POSTS)
    
    # Pick a random subreddit
    sub = random.choice(SUBREDDITS)
    
    print(f"\n🎯 目标: r/{sub}")
    print(f"📝 标题: {post['title'][:80]}")
    
    # Post!
    success = post_to_reddit(sub, post["title"], post["text"], token)
    
    # Wait and try one more
    if success:
        time.sleep(30)
        sub2 = random.choice([s for s in SUBREDDITS if s != sub])
        post2 = random.choice([p for p in POSTS if p != post])
        print(f"\n🎯 第二发: r/{sub2}")
        post_to_reddit(sub2, post2["title"], post2["text"], token)
    
    # Summary
    with open("reddit_log.txt", "w") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M UTC')} | r/{sub} | {'OK' if success else 'FAIL'}\n")
    
    print(f"\n📊 日志已保存")

if __name__ == "__main__":
    main()
