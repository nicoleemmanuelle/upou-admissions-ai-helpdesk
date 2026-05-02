## Knowledge Base 

This module handles the **collection, processing, and transformation of UPOU admissions data** into structured formats used by the AI helpdesk system.

The  consists of three main stages:

1. Web scraping of admissions-related pages
2. OCR extraction from documents using AWS Textract
3. AI-based formatting and chunking for RAG

---

## 📂 Directory Structure

```
knowledge-base/
├── 00_admission_url_scraper.py   # Crawls and collects admission-related URLs
├── 03_aws_textractv2.py         # Extracts text from documents using AWS Textract
├── 03_kb_generationv2.py        # Converts content into structured Markdown using OpenAI
├── urls.txt                     # List of admission URLs to process
├── for_textract/                # Raw PDFs/images for OCR
└── output_for_s3/               # Final processed knowledge base files
```

---

## 🕸️ Step 1: URL Scraping

**File:** `00_admission_url_scraper.py`

This script crawls the UPOU registrar website and identifies admission-related pages.

### Features

* Recursive crawling within the same domain
* Filters links using keywords (`admission`, `apply`, etc.)
* Avoids duplicate visits
* Outputs discovered URLs to a file

### Output

* List of relevant URLs saved for further processing

---

## 📄 Step 2: Document Processing (AWS Textract)

**File:** `03_aws_textractv2.py`

This script extracts text from uploaded PDFs/images stored in S3 using AWS Textract.

### Features

* Reads files from S3 (`for_textract/` folder)
* Performs OCR using `analyze_document`
* Extracts structured text from forms and tables

### Outputs

Generated in `output_for_s3/`:

* `.md` → readable knowledge base format
* `.json` → structured raw output
* `.csv` → aggregated dataset

---

## 🤖 Step 3: AI Knowledge Base Generation

**File:** `03_kb_generationv2.py`

This script processes scraped web content and converts it into structured, admissions-focused Markdown using OpenAI.

### Features

* Cleans HTML using BeautifulSoup + Readability
* Uses LLM to extract:

  * Requirements
  * Procedures
  * Timelines
  * FAQs
* Filters out irrelevant content (e.g., marketing text)
* Chunks content into smaller sections for better retrieval

### Output

* Structured Markdown files (`*_chunk_*.md`) ready for RAG

---

## ⚙️  Flow

```text
URLs → Scraper → Raw HTML
           ↓
      OpenAI Formatter → Structured Markdown → Chunked Files
           ↓
    Textract (PDF/Image) → Text Extraction → MD / JSON / CSV
           ↓
      output_for_s3 → Uploaded to S3 → Used by Lambda (RAG)
```

---

## 🚀 How to Run

### 1. Scrape URLs

```bash
python 00_admission_url_scraper.py
```

### 2. Process documents with Textract

```bash
python 03_aws_textractv2.py
```

### 3. Generate structured knowledge base

```bash
python 03_kb_generationv2.py
```

---

## 📌 Notes

* Ensure AWS credentials are configured before running Textract
* Update `BUCKET_NAME` and AWS keys in the Textract script
* The OpenAI API key must be set in `03_kb_generationv2.py`
* Output files are automatically uploaded to S3 during Terraform deployment

---

## 🧠 Purpose

This ensures that:

* The AI model only responds using **verified admissions data**
* Content is structured and optimized for **retrieval-augmented generation (RAG)**
* Both **web content and scanned documents** are included in the knowledge base
