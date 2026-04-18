import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import csv
import re

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

# --- CONFIG ---
INPUT_FILE = "url_addtl.txt"        # Text File for the list of URL generated from Link Scraping
OUTPUT_MD = "rag_output_addtl.md"   # MD File output after the execution
OUTPUT_CSV = "rag_output_addtl.csv" # MD File output after the execution

MAX_DEPTH = 1
DELAY = 1

# --- KEYWORDS SET TO CAPTURE ADMISSION-RELATED INFO ---
KEYWORDS = [
    "admission", "admissions",
    "apply", "application",
    "Admission Requirement",
    "Admission Policies", "Admission Requirements"
]

headers = {"User-Agent": "Mozilla/5.0"}

visited = set()
chunks_data = []

# --- EMBEDDINGS (LOCAL, NO API KEY) ---
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

text_splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile"
)

# --- LOAD URLS ---
def load_urls(file):
    with open(file, "r") as f:
        return [line.strip() for line in f if line.strip()]

# --- CLEAN HTML ---
def extract_text(soup):
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.extract()

    text = soup.get_text(separator="\n", strip=True)
    return "\n".join([line.strip() for line in text.splitlines() if line.strip()])

# --- TITLE ---
def extract_title(soup):
    return soup.title.string.strip() if soup.title else "No Title"

# --- FILTER: ADMISSION CONTENT ONLY ---
def filter_admission_content(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    filtered = [
        s for s in sentences
        if any(k in s.lower() for k in KEYWORDS)
    ]
    return "\n".join(filtered)

# --- CHECK PAGE RELEVANCE ---
def is_admission_page(url, title, text):
    combined = (url + " " + title + " " + text).lower()
    return any(k in combined for k in KEYWORDS)

# --- CRAWLER ---
def crawl(url, depth, base_domain):
    if url in visited or depth > MAX_DEPTH:
        return

    print(f"Crawling: {url}")
    visited.add(url)

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        title = extract_title(soup)
        clean_text = extract_text(soup)

        # Skip non-admission pages early
        if not is_admission_page(url, title, clean_text):
            return

        # KEEP ONLY ADMISSION CONTENT
        filtered_text = filter_admission_content(clean_text)

        # Skip empty results
        if len(filtered_text.strip()) < 50:
            return

        # --- SEMANTIC CHUNKING ---
        docs = text_splitter.create_documents([filtered_text])

        for i, doc in enumerate(docs):
            chunks_data.append({
                "id": len(chunks_data),
                "url": url,
                "title": title,
                "chunk_index": i,
                "content": doc.page_content
            })

        # --- FOLLOW LINKS ---
        if depth < MAX_DEPTH:
            for a in soup.find_all("a", href=True):
                next_url = urljoin(url, a["href"])
                if urlparse(next_url).netloc == base_domain:
                    crawl(next_url, depth + 1, base_domain)

        time.sleep(DELAY)

    except Exception as e:
        print(f"Error: {e}")

# --- EXPORT MARKDOWN ---
def export_markdown(file):
    with open(file, "w", encoding="utf-8") as f:
        for item in chunks_data:
            f.write(f"## {item['title']}\n")
            f.write(f"**Source:** {item['url']}\n")
            f.write(f"**Chunk {item['chunk_index']}**\n\n")
            f.write(item["content"] + "\n\n---\n\n")

# --- EXPORT CSV ---
def export_csv(file):
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "title", "url", "chunk_index", "content"]
        )
        writer.writeheader()
        writer.writerows(chunks_data)

# --- MAIN ---
if __name__ == "__main__":
    urls = load_urls(INPUT_FILE)

    for url in urls:
        domain = urlparse(url).netloc
        crawl(url, 0, domain)

    print(f"\nTotal admission chunks: {len(chunks_data)}")

    export_markdown(OUTPUT_MD)
    export_csv(OUTPUT_CSV)

    print("\nDone. Admission-only dataset ready.")
