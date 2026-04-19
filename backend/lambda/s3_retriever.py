import os
import csv
import io
import re
import boto3

csv.field_size_limit(1_000_000)

s3 = boto3.client("s3")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "upou-admissions-kb")

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "because", "but", "and", "or", "if", "while", "what", "which",
    "who", "whom", "this", "that", "these", "those", "i", "me", "my",
    "myself", "we", "our", "you", "your", "he", "him", "his", "she", "her",
    "it", "its", "they", "them", "their", "about", "up", "am",
}

def get_context(query):
    """Retrieve relevant chunks from CSV knowledge base files in S3."""
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME)
    # Strip punctuation and remove stop words
    raw_words = re.findall(r'[a-zA-Z0-9]+', query.lower())
    query_words = set(w for w in raw_words if w not in STOP_WORDS and len(w) > 1)
    print(f"Query words after cleanup: {query_words}")
    scored_chunks = []

    for obj in objects.get("Contents", []):
        key = obj["Key"]
        if not key.endswith(".csv"):
            continue

        file = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        content = file["Body"].read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))

        for row in reader:
            chunk_text = row.get("content", "")
            title = row.get("title", "")
            url = row.get("url", "")
            chunk_lower = chunk_text.lower()
            # Also match against title
            combined = title.lower() + " " + chunk_lower

            # Score: prioritize distinct query words matched, then frequency
            distinct_matches = 0
            total_freq = 0
            for word in query_words:
                pattern = r'\b' + re.escape(word) + r'\b'
                count = len(re.findall(pattern, combined))
                if count > 0:
                    distinct_matches += 1
                    total_freq += count
            if distinct_matches > 0:
                # Primary sort by distinct words matched, secondary by frequency
                score = distinct_matches * 1000 + total_freq
                header = f"[Source: {title}]({url})\n" if title else ""
                scored_chunks.append((score, header + chunk_text))

    # Sort by relevance
    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    # Take top chunks up to token budget
    context = ""
    for _, chunk in scored_chunks:
        if len(context) + len(chunk) > 8000:
            break
        context += chunk + "\n\n"

    return context