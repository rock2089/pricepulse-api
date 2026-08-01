#!/usr/bin/env python3
"""
Freelancer Auto Bid v2 - Login, Search, Bid, Check Messages
"""
import os, json, time, sys, ssl, re
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor, HTTPSHandler
from urllib.parse import quote
from http.cookiejar import CookieJar
import urllib.error

ssl._create_default_https_context = ssl._create_unverified_context

FL_EMAIL = os.environ.get("FL_EMAIL", "")
FL_PASSWORD = os.environ.get("FL_PASSWORD", "")
MAX_BID_COST = 10  # Max total bid cost ($0.59 each)

if not FL_EMAIL or not FL_PASSWORD:
    print("ERROR: Missing FL_EMAIL/FL_PASSWORD in env")
    sys.exit(1)

class FreelancerAPI:
    def __init__(self):
        self.cj = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cj), HTTPSHandler())
        
    def _req(self, url, data=None, method='GET', extra_headers=None):
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        
        req = Request(url, data=data, headers=headers, method=method)
        try:
            resp = self.opener.open(req, timeout=20)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            return {"status": "error", "code": e.code, "message": body[:300]}
        except Exception as e:
            return {"status": "error", "message": str(e)[:200]}
    
    def login(self):
        print("🔑 Logging in...")
        result = self._req(
            "https://www.freelancer.com/api/users/0.1/login",
            data=json.dumps({"user": FL_EMAIL, "password": FL_PASSWORD}).encode(),
            method='POST'
        )
        if result.get("status") == "error":
            print(f"  ❌ Login failed: {result.get('message','?')}")
            return False
        username = result.get("result", {}).get("username", "?")
        print(f"  ✅ Logged in as {username}")
        return True
    
    def check_messages(self):
        print("\n📨 Checking messages...")
        result = self._req(
            "https://www.freelancer.com/api/messaging/0.1/threads/?limit=10&unread=true&context_types[]=project"
        )
        threads = result.get("result", {}).get("threads", [])
        print(f"  Unread: {len(threads)}")
        for t in threads[:5]:
            ctx = t.get("context", {})
            pid = ctx.get("project_id", "?")
            title = ctx.get("title", "N/A")[:80]
            print(f"  📩 Thread #{t['id']} | Project #{pid} | {title}")
            # Get message content
            detail = self._req(
                f"https://www.freelancer.com/api/messaging/0.1/threads/{t['id']}/messages/?limit=2"
            )
            msgs = detail.get("result", {}).get("messages", [])
            for m in msgs:
                user = m.get("from_user", {}).get("username", "?")
                text = (m.get("message_preview") or m.get("message", ""))[:200]
                print(f"      {user}: {text}")
        return threads
    
    def bid(self, project_id, amount, period, description):
        result = self._req(
            "https://www.freelancer.com/api/projects/0.1/bid/",
            data=json.dumps({
                "project_id": project_id,
                "amount": amount,
                "period": period,
                "description": description,
                "currency_id": 1,
            }).encode(),
            method='POST'
        )
        return result

def main():
    print("=" * 60)
    print(f"FREELANCER AUTO BID v2 - {time.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    api = FreelancerAPI()
    
    # 1. Login
    if not api.login():
        sys.exit(1)
    
    # 2. Check messages
    api.check_messages()
    
    # 3. Search for projects
    print("\n🔍 Searching projects...")
    keywords = ["python", "scraping", "automation", "data entry", "virtual assistant", "bot", "web scraping"]
    seen = set()
    candidates = []
    
    for kw in keywords:
        result = api._req(
            f"https://www.freelancer.com/api/projects/0.1/projects/active/?limit=10&query={quote(kw)}"
        )
        projects = result.get("result", {}).get("projects", [])
        for p in projects:
            pid = p.get("id")
            if pid not in seen:
                seen.add(pid)
                budget = p.get("budget", {})
                bids = p.get("bid_stats", {}).get("bid_count", 99)
                title = p.get("title", "")
                desc = (p.get("preview_description", "") or "")[:200]
                
                min_b = budget.get("minimum", 0) or 0
                max_b = budget.get("maximum", 0) or 0
                
                # Filter: budget $2-200, max 15 bids
                if (min_b >= 2 or max_b >= 2) and bids <= 15:
                    score = 0
                    text = (title + desc).lower()
                    for kw2 in ["scrap", "python", "automation", "bot", "data", "extract", "crawl", 
                               "script", "excel", "price", "telegram", "discord", "virtual assistant"]:
                        if kw2 in text:
                            score += 10
                    
                    candidates.append({
                        "id": pid,
                        "title": title,
                        "budget": f"${min_b}-{max_b}" if min_b != max_b else f"${min_b}",
                        "min_b": min_b,
                        "max_b": max_b,
                        "bids": bids,
                        "score": score,
                        "desc": desc[:100],
                        "url": f"https://www.freelancer.com/projects/{p.get('seo_url','')}"
                    })
        time.sleep(0.5)
    
    # Sort by score desc, bids asc
    candidates.sort(key=lambda c: (-c["score"], c["bids"]))
    
    print(f"\n📊 Found {len(candidates)} candidates:")
    for c in candidates[:10]:
        print(f"  #{c['id']} | {c['budget']} | {c['bids']} bids | Score:{c['score']} | {c['title'][:70]}")
    
    # 4. Place bids on top candidates
    print(f"\n💰 Placing bids (max ${MAX_BID_COST}):")
    bid_count = 0
    total_cost = 0
    
    for c in candidates[:8]:
        if total_cost + 0.59 > MAX_BID_COST:
            break
        
        # Determine bid amount
        if c["max_b"] and c["max_b"] <= 50:
            amount = max(10, c["max_b"] - 5)
        elif c["max_b"]:
            amount = int(c["max_b"] * 0.6)
        else:
            amount = c["min_b"] if c["min_b"] else 15
        
        desc = f"""I can complete this project efficiently. I have relevant experience with {c['title'][:30]}.
Quality work, fast delivery. Let's discuss the details.

Fixed price: ${amount}
Delivery: 3-5 days"""

        result = api.bid(c["id"], amount, 5, desc)
        if result.get("status") == "error":
            msg = result.get("message", "")
            if "balance" in msg.lower() or "minimum" in msg.lower():
                print(f"  ❌ #{c['id']}: Balance issue - {msg[:100]}")
                continue
            elif "verified" in msg.lower():
                print(f"  ❌ #{c['id']}: Verification needed - {msg[:100]}")
                continue
            else:
                print(f"  ❌ #{c['id']}: {msg[:100]}")
        else:
            bid_id = result.get("result", {}).get("id", "?")
            print(f"  ✅ #{c['id']}: Bid placed! Amount=${amount}, Bid ID={bid_id}")
            bid_count += 1
            total_cost += 0.59
        
        time.sleep(1)
    
    # 5. Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {bid_count} bids placed, total cost ${total_cost:.2f}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
