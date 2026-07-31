#!/usr/bin/env python3
"""
跨境套利扫描 - Amazon热销 vs 1688进价
GitHub Actions运行，爬Amazon→匹配1688→算利润
"""
import json, time, re, sys
from urllib.request import Request, urlopen
from urllib.parse import quote
from html.parser import HTMLParser

# ====== 热销品类 ======
CATEGORIES = [
    ("silicone measuring cups", "硅胶量杯"),
    ("phone case iphone", "手机壳"),
    ("led strip lights", "LED灯带"),
    ("bluetooth earbuds", "蓝牙耳机"),
    ("fidget toys", "解压玩具"),
    ("car phone holder", "车载手机支架"),
    ("mini usb fan", "USB小风扇"),
    ("pet toys", "宠物玩具"),
    ("kitchen gadgets", "厨房小工具"),
    ("desk organizer", "桌面收纳"),
]

def amazon_search(keyword: str) -> list:
    """爬Amazon搜索结果"""
    url = f"https://www.amazon.com/s?k={quote(keyword)}"
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
    })
    try:
        with urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  Amazon爬取失败 ({keyword}): {e}")
        return []
    
    products = []
    # 提取价格和标题
    prices = re.findall(r'\$(\d+\.?\d*)', html)
    titles = re.findall(r'<span[^>]*class="a-size-base-plus a-color-base a-text-normal"[^>]*>(.*?)</span>', html)
    ratings = re.findall(r'<span[^>]*class="a-icon-alt"[^>]*>([\d.]+) out of', html)
    reviews = re.findall(r'<span[^>]*class="a-size-base s-underline-text"[^>]*>([\d,]+)</span>', html)
    
    for i in range(min(len(titles), 10)):
        title = re.sub(r'<[^>]+>', '', titles[i]).strip()
        price = float(prices[i]) if i < len(prices) else 0
        rating = float(ratings[i]) if i < len(ratings) else 0
        review_count = reviews[i].replace(',', '') if i < len(reviews) else '0'
        
        if price > 0:
            products.append({
                "title": title[:80],
                "price_usd": price,
                "rating": rating,
                "reviews": int(review_count) if review_count.isdigit() else 0,
            })
    return products

def alibaba_search(keyword_cn: str) -> list:
    """爬1688搜索（简单版）"""
    url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={quote(keyword_cn)}"
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    try:
        with urlopen(req, timeout=20) as resp:
            html = resp.read().decode("gbk", errors="ignore")
    except:
        try:
            with urlopen(req, timeout=20) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"  1688爬取失败 ({keyword_cn}): {e}")
            return []
    
    products = []
    # 提取价格
    prices = re.findall(r'(\d+\.?\d*)元', html)
    titles_cn = re.findall(r'class="title"[^>]*title="([^"]+)"', html)
    
    for i in range(min(len(titles_cn), 5)):
        price_cny = float(prices[i]) if i < len(prices) else 0
        if price_cny > 0 and price_cny < 1000:
            products.append({
                "title_cn": titles_cn[i][:60] if i < len(titles_cn) else "N/A",
                "price_cny": price_cny,
            })
    return products

def main():
    print("=" * 70)
    print(f"🛒 跨境套利扫描 - {time.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 70)
    
    results = []
    
    for kw_en, kw_cn in CATEGORIES:
        print(f"\n🔍 {kw_en} / {kw_cn}")
        
        # Amazon
        amazon_products = amazon_search(kw_en)
        best_amazon = amazon_products[0] if amazon_products else None
        
        if best_amazon:
            print(f"  🇺🇸 Amazon: ${best_amazon['price_usd']:.2f} - {best_amazon['title'][:60]}")
        
        # 1688
        alibaba_products = alibaba_search(kw_cn)
        best_alibaba = alibaba_products[0] if alibaba_products else None
        
        if best_alibaba:
            print(f"  🇨🇳 1688: ¥{best_alibaba['price_cny']:.2f} - {best_alibaba['title_cn'][:60]}")
        
        # 算利润
        if best_amazon and best_alibaba and best_amazon['price_usd'] > 0 and best_alibaba['price_cny'] > 0:
            cost_cny = best_alibaba['price_cny']
            sell_cny = best_amazon['price_usd'] * 7.2  # USD→CNY
            profit = sell_cny - cost_cny
            margin = (profit / sell_cny * 100) if sell_cny > 0 else 0
            
            stars = "⭐" * min(5, int(margin / 100)) if margin > 100 else ("🟢" if margin > 50 else "🟡")
            
            results.append({
                "keyword_en": kw_en,
                "keyword_cn": kw_cn,
                "amazon_title": best_amazon['title'],
                "amazon_price": best_amazon['price_usd'],
                "amazon_rating": best_amazon['rating'],
                "amazon_reviews": best_amazon['reviews'],
                "alibaba_title": best_alibaba['title_cn'],
                "alibaba_price": best_alibaba['price_cny'],
                "profit_cny": round(profit, 2),
                "margin_pct": round(margin, 1),
            })
            
            print(f"  💰 利润: ¥{profit:.0f} | 利润率: {margin:.0f}% {stars}")
        
        time.sleep(2)  # 礼貌爬取
    
    # 排序输出
    results.sort(key=lambda x: -x['margin_pct'])
    
    print(f"\n{'='*70}")
    print("🏆 套利排行榜")
    print(f"{'='*70}")
    print(f"{'品类':<20} {'Amazon':>8} {'1688':>8} {'利润':>8} {'利润率':>8}")
    print("-" * 55)
    
    top_deals = []
    for r in results:
        marker = "🔥" if r['margin_pct'] > 200 else ("💰" if r['margin_pct'] > 100 else "📦")
        line = f"{marker} {r['keyword_cn']:<16} ${r['amazon_price']:>7.2f} ¥{r['alibaba_price']:>7.2f} ¥{r['profit_cny']:>7.0f} {r['margin_pct']:>7.0f}%"
        print(line)
        
        if r['margin_pct'] > 100:
            top_deals.append(r)
    
    # 保存报告
    report = {
        "time": time.strftime('%Y-%m-%d %H:%M UTC'),
        "results": results,
        "top_deals": top_deals,
    }
    with open("arbitrage_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 报告已保存: arbitrage_report.json")
    print(f"🔥 高利润品类: {len(top_deals)} 个")
    
    # Markdown报告
    md = f"""# 🛒 跨境套利扫描报告
**{time.strftime('%Y-%m-%d %H:%M UTC')}**

## 🏆 套利排行榜

| 品类 | Amazon | 1688 | 利润(¥) | 利润率 |
|------|--------|------|---------|--------|
"""
    for r in results:
        md += f"| {r['keyword_cn']} | ${r['amazon_price']:.2f} | ¥{r['alibaba_price']:.2f} | ¥{r['profit_cny']:.0f} | {r['margin_pct']:.0f}% |\n"
    
    md += f"\n## 🔥 高利润品类 ({len(top_deals)}个)\n\n"
    for r in top_deals:
        md += f"- **{r['keyword_cn']}**: Amazon ${r['amazon_price']:.2f} → 1688 ¥{r['alibaba_price']:.2f} = **利润 ¥{r['profit_cny']:.0f} ({r['margin_pct']:.0f}%)**\n"
    
    with open("arbitrage_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    
    print(f"📝 Markdown报告: arbitrage_report.md")

if __name__ == "__main__":
    main()
