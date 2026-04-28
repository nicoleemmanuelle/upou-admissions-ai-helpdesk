import os
import requests
from bs4 import BeautifulSoup
from readability import Document
from slugify import slugify
from openai import OpenAI
import time

# =========================
# CONFIG
# =========================
client = OpenAI(
    api_key="sk-proj-6yNeTNO2BLXzU782avycxuYCgRQvVzsvHSXLdYKsaJb6AOM",
    base_url="https://is215-openai.upou.io/v1"  # <-- declare it here
)

OUTPUT_DIR = "knowledge_base_admissions"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# LOAD URLS FROM TXT
# =========================
def load_urls(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip().startswith("http")]


# =========================
# SCRAPE CONTENT
# =========================
def extract_content(url):
    response = requests.get(url, timeout=15)
    doc = Document(response.text)

    title = doc.title()
    html = doc.summary()

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    return title, text


# =========================
# AI FORMATTER (ADMISSIONS-FOCUSED)
# =========================
def format_admissions_md(title, raw_text, url):

    prompt = f"""
You are building a knowledge base for a university admissions chatbot.

Extract and convert the content into a structured Markdown format.

FOCUS ONLY ON ADMISSIONS-RELATED INFORMATION:
- Requirements (documents, eligibility)
- Procedures (step-by-step application process)
- Timelines (deadlines, schedules, enrollment periods)
- Fees (if mentioned)
- Program-specific requirements (if applicable)

IGNORE:
- Marketing content
- General university descriptions
- Irrelevant sections

OUTPUT FORMAT:

---
source: {url}
title: {title}
category: admissions
---

## Topic: {title}

### Overview
...

### Admission Requirements
- ...

### Application Procedure
1. ...
2. ...

### Important Dates and Timelines
- ...

### Program-Specific Notes
...

### FAQs
Q: ...
A: ...

Content:
\"\"\"
{raw_text[:12000]}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-5.4-mini",  # replace with your school model
        messages=[
            {"role": "system", "content": "You extract and structure university admissions data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# =========================
# SMART CHUNKING (BY HEADINGS)
# =========================
def chunk_by_sections(md_text):
    chunks = []
    current_chunk = ""

    for line in md_text.split("\n"):
        if line.startswith("## ") and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# =========================
# SAVE FILES
# =========================
def save_chunks(title, chunks):
    base = slugify(title)

    for i, chunk in enumerate(chunks):
        filename = f"{base}_chunk_{i+1}.md"
        path = os.path.join(OUTPUT_DIR, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(chunk)

    print(f"Saved {len(chunks)} chunks: {title}")


# =========================
# MAIN PROCESS
# =========================
def process_url(url, index, total):
    print(f"[{index}/{total}] Processing: {url}")

    title, raw_text = extract_content(url)

    print("→ Formatting admissions content...")
    md = format_admissions_md(title, raw_text, url)

    print("→ Chunking...")
    chunks = chunk_by_sections(md)

    print("→ Saving...")
    save_chunks(title, chunks)

    time.sleep(2)  # avoid rate limit


# =========================
# RUN PIPELINE
# =========================
if __name__ == "__main__":
    urls = load_urls("urls.txt")

    print(f"Loaded {len(urls)} URLs")

    for i, url in enumerate(urls, start=1):
        try:
            process_url(url, i, len(urls))
        except Exception as e:
            print(f"Error: {e}")