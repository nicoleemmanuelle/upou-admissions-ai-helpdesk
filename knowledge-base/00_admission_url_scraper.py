import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# --- CONFIG ---
START_URL = "https://registrar.upou.edu.ph/"        # Base URL to start Scraping
KEYWORDS = ["admission", "admissions", "apply"]     # Keywords
MAX_PAGES = 100
DELAY = 1

visited = set()
found_pages = []

headers = {
    "User-Agent": "Mozilla/5.0"
}

def is_same_domain(url, base_domain):
    return urlparse(url).netloc in ["", base_domain]

def is_admission_related(text):
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

def extract_links(soup, current_url, base_domain):
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(current_url, a["href"])
        if is_same_domain(href, base_domain):
            links.append((href, a.get_text(strip=True)))
    return links

def crawl(url, base_domain):
    if url in visited or len(visited) >= MAX_PAGES:
        return

    print(f"Scanning: {url}")
    visited.add(url)

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        links = extract_links(soup, url, base_domain)

        for link_url, link_text in links:
            combined_text = f"{link_url} {link_text}"

            if is_admission_related(combined_text):
                if link_url not in found_pages:
                    print(f"  ➜ Found admission page: {link_url}")
                    found_pages.append(link_url)

            # Continue crawling deeper
            if link_url not in visited:
                crawl(link_url, base_domain)

        time.sleep(DELAY)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    base_domain = urlparse(START_URL).netloc
    crawl(START_URL, base_domain)

    print("\n=== Admission-related Pages Found ===")
    for page in found_pages:
        print(page)

    # Optional: save to file
    with open("url_main.txt", "w") as f:
        for page in found_pages:
            f.write(page + "\n")
