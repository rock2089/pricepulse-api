#!/usr/bin/env python3
"""
Freelancer Auto Bid - Runs on GitHub Actions
Searches projects, filters matches, generates proposals
"""
import os, json, time, sys
from urllib.request import Request, urlopen
from urllib.parse import quote

# ====== CONFIG ======
FL_EMAIL = os.environ.get("FL_EMAIL", "")
FL_PASSWORD = os.environ.get("FL_PASSWORD", "")
FL_COOKIE = os.environ.get("FL_COOKIE", "")  # Netscape format cookie string

KEYWORDS = [
    "python scraping", "web automation", "data extraction",
    "price tracker", "telegram bot", "discord bot",
    "excel data", "python script", "scraper", "data mining"
]

FILTER = {
    "currency": "USD",
    "budget_min": 10,
    "budget_max": 200,
    "max_bids": 20,
    "max_hours": 48,
}

BID_TEMPLATES = {
    "scraping": "I have a ready-made web scraping solution — can deliver in 24h. Python (BeautifulSoup/Selenium), clean CSV output. Fixed price ${price}.",
    "automation": "I'll build a Python automation script for this. Fast delivery, clean code. Fixed price ${price}.",
    "bot": "I can build this bot using my existing PricePulse API framework — Telegram/Discord alerts, 24h delivery. Fixed price ${price}.",
    "data": "I'll process this data with Python/pandas — clean, formatted output. Fixed price ${price}.",
    "default": "I can complete this efficiently using Python. Fast delivery, quality work. Fixed price ${price}.",
}

def search_projects(query: str, limit: int = 30) -> list:
    """Search Freelancer API"""
    url = f"https://www.freelancer.com/api/projects/0.1/projects/active/?limit={limit}&query={quote(query)}&job_type=hourly,fixed"
    req = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    })
    try:
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            return data.get("result", {}).get("projects", [])
    except Exception as e:
        print(f"  Search error ({query}): {e}")
        return []

def classify_project(title: str, desc: str, skills: str) -> str:
    """Classify project type for template selection"""
    text = (title + " " + desc + " " + skills).lower()
    if any(k in text for k in ["scrap", "crawl", "extract", "beautifulsoup", "selenium"]):
        return "scraping"
    if any(k in text for k in ["bot", "telegram", "discord", "alert", "notify"]):
        return "bot"
    if any(k in text for k in ["automation", "script", "workflow"]):
        return "automation"
    if any(k in text for k in ["data", "excel", "csv", "pandas", "analysis"]):
        return "data"
    return "default"

def match_score(title: str, desc: str, skills: str) -> int:
    """Calculate relevance score"""
    text = (title + " " + desc + " " + skills).lower()
    score = 0
    for kw, pts in {
        "scrap": 15, "beautifulsoup": 15, "selenium": 15, "scrapy": 15,
        "web scraping": 15, "data extraction": 12, "data mining": 12,
        "python": 10, "pandas": 12, "automation": 9, "bot": 10,
        "crawl": 8, "excel": 8, "price": 10, "tracker": 10,
        "telegram": 8, "discord": 8,
    }.items():
        if kw in text:
            score += pts
    if score == 0 and "python" not in text and "scrap" not in text and "automation" not in text:
        return 0
    return score

def main():
    print("=" * 70)
    print(f"FREELANCER AUTO BID - {time.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 70)
    
    # Collect projects
    all_projects = {}
    seen = set()
    for kw in KEYWORDS:
        for p in search_projects(kw):
            pid = p.get("id")
            if pid not in seen:
                seen.add(pid)
                all_projects[pid] = p
        time.sleep(0.5)
    
    print(f"\nScanned: {len(all_projects)} unique projects across {len(KEYWORDS)} keywords\n")
    
    # Filter
    now = int(time.time())
    filtered = []
    
    for pid, p in all_projects.items():
        if p.get("currency", {}).get("code") != FILTER["currency"]:
            continue
        
        b = p.get("budget", {})
        lo, hi = b.get("minimum", 0) or 0, b.get("maximum", 0) or 0
        
        if hi and hi > FILTER["budget_max"]:
            continue
        if not lo and not hi:
            continue
        if hi and hi < FILTER["budget_min"]:
            continue
        
        if p.get("bid_stats", {}).get("bid_count", 0) > FILTER["max_bids"]:
            continue
        if p.get("submitdate", 0) < now - FILTER["max_hours"] * 3600:
            continue
        
        upgrades = p.get("upgrades", {})
        if upgrades.get("sealed") or upgrades.get("featured"):
            continue
        
        title = p.get("title", "")
        desc = p.get("preview_description", "") or ""
        skills = " ".join([s.get("name", "") for s in (p.get("jobs") or [])])
        
        score = match_score(title, desc, skills)
        p["_score"] = score
        p["_bids"] = p.get("bid_stats", {}).get("bid_count", 0)
        p["_lo"] = lo
        p["_hi"] = hi
        p["_hours"] = (now - p.get("submitdate", 0)) / 3600
        filtered.append(p)
    
    filtered.sort(key=lambda p: (-p["_score"], p["_bids"]))
    
    # Output results
    report_lines = []
    good_count = 0
    
    for p in filtered[:15]:
        if p["_score"] <= 0:
            continue
        
        good_count += 1
        pid = p.get("id")
        title = p.get("title", "N/A")
        seo = p.get("seo_url", "")
        lo, hi = p["_lo"], p["_hi"]
        bid_count = p["_bids"]
        hours = p["_hours"]
        ptype = p.get("type", "fixed")
        desc = (p.get("preview_description", "") or "")[:200]
        skills_list = [s.get("name", "") for s in (p.get("jobs") or [])]
        skills_str = " ".join(skills_list)
        
        # Determine bid price
        if hi and hi <= 50:
            bid_price = max(10, lo if lo else int(hi * 0.5))
        elif hi:
            bid_price = max(10, int(hi * 0.4))
        else:
            bid_price = lo if lo else 15
        
        ptype_label = "Type" if ptype == "hourly" else "Proj"
        budget_str = f"${lo}-{hi}" if lo != hi else f"${lo or hi}"
        
        # Classify and pick template
        pclass = classify_project(title, desc, skills_str)
        template = BID_TEMPLATES.get(pclass, BID_TEMPLATES["default"])
        proposal = template.replace("${price}", str(bid_price))
        
        url = f"https://www.freelancer.com/projects/{seo}"
        
        block = f"""
{'─'*60}
[{good_count}] ID:{pid} | {budget_str} {ptype_label} | {bid_count} bids | {hours:.1f}h | Score:{p['_score']}
  Title: {title[:100]}
  Skills: {', '.join(skills_list[:5])}
  URL: {url}
  Desc: {desc[:150]}
  >> Bid: ${bid_price}
  >> Proposal: {proposal}
"""
        print(block)
        report_lines.append(block)
    
    # Summary
    summary = f"""
{'='*70}
SUMMARY
{'='*70}
Projects worth bidding: {good_count}
Total bid cost: ${good_count * 0.59:.2f} ({good_count} x $0.59)
"""
    print(summary)
    report_lines.append(summary)
    
    if good_count == 0:
        print("No matching projects in this round.")
    
    # Save report
    with open("bid_report.txt", "w", encoding="utf-8") as f:
        f.write("".join(report_lines))
    
    print(f"Report saved to bid_report.txt")
    
    # If we have cookie, try to bid
    if FL_COOKIE and good_count > 0:
        print("\n⚠️  Cookie provided but auto-bidding via cookie not yet implemented.")
        print("    For now: review report above and manually bid on best matches.")

if __name__ == "__main__":
    main()
