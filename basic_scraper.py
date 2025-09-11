# basic_cuny_scraper.py
import re, time, json, hashlib, urllib.parse, urllib.robotparser as rp
import requests
from bs4 import BeautifulSoup

WHITELIST = (
    r".*\.cuny\.edu$",
    r".*\.baruch\.cuny\.edu$",
    r".*\.hunter\.cuny\.edu$",
    r".*\.citytech\.cuny\.edu$",
    r".*\.ccny\.cuny\.edu$",
)

HEADERS = {
    "User-Agent": "CUNYAdmissionsBot/0.1 (+https://example.org/contact)"
}
TIMEOUT = 15
SLEEP_BETWEEN = 1.0  # seconds (be polite)

def allowed_by_robots(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rparser = rp.RobotFileParser()
    try:
        rparser.set_url(robots_url)
        rparser.read()
        return rparser.can_fetch(HEADERS["User-Agent"], url)
    except Exception:
        # If robots fails to load, default to disallow to be safe
        return False

def whitelisted(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(re.fullmatch(pat, host) for pat in WHITELIST)

def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    # basic content-type guard
    if "text/html" not in resp.headers.get("Content-Type", ""):
        raise ValueError("Not an HTML page")
    return resp.text

def extract(html: str, base_url: str):
    soup = BeautifulSoup(html, "html.parser")
    # Title
    title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    # Remove script/style/nav/footer for cleaner text
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    # Get visible text
    text = " ".join(s.strip() for s in soup.stripped_strings)
    # Keep on-site links you might crawl later
    links = []
    for a in soup.find_all("a", href=True):
        href = urllib.parse.urljoin(base_url, a["href"])
        if href.startswith("mailto:") or href.startswith("tel:"):
            continue
        if whitelisted(href):
            links.append(href)
    # Deduplicate links
    links = sorted(set(links))
    return title, text, links

def snapshot_record(url: str, title: str, text: str, links: list):
    h = hashlib.sha256((url + text[:2000]).encode("utf-8")).hexdigest()[:12]
    return {
        "url": url,
        "title": title,
        "content_sha": h,
        "content_preview": text[:1200],
        "links_whitelisted": links,
    }

def scrape_one(url: str):
    if not whitelisted(url):
        raise ValueError("URL not in CUNY whitelist.")
    if not allowed_by_robots(url):
        raise PermissionError("Blocked by robots.txt")

    html = fetch(url)
    title, text, links = extract(html, url)
    return snapshot_record(url, title, text, links)

if __name__ == "__main__":
    print("🚀 Starting CUNY scraper...")
    
    # Try a couple of admissions-related pages (replace or add more safely)
    test_urls = [
        "https://www.cuny.edu/admissions/undergraduate/",
        "https://www.cuny.edu/admissions/graduate-studies/",
        "https://hunter.cuny.edu/admissions/undergraduate/first-year-applicants/"
    ]

    results = []
    for u in test_urls:
        try:
            print(f"🔍 Scraping: {u}")
            rec = scrape_one(u)
            results.append(rec)
            print(f"✅ Successfully scraped: {rec['title'][:50]}...")
            time.sleep(SLEEP_BETWEEN)
        except Exception as e:
            print(f"❌ Skipped {u}: {e}")

    out_path = "cuny_scrape_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(results)} records to {out_path}")
    print("🎉 Scraping complete!")
