"""S3 knowledge base retriever.

Retrieves and ranks documents from S3 by relevance to the user query.
Documents are scored by how many meaningful query terms they contain,
and only the highest-scoring documents are returned as context.
"""

import os
import logging
from typing import List, Tuple

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

_STOP_WORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "not", "with", "this", "that", "are",
    "was", "be", "as", "by", "from", "how", "what", "when", "where",
    "who", "which", "do", "does", "did", "i", "my", "me", "can", "you",
    "your", "we", "our", "they", "their", "have", "has", "had", "will",
    "would", "could", "should", "about", "there", "than", "so", "if",
}


def _list_bucket_objects(s3_client, bucket: str):
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents") or []:
            yield obj


def _meaningful_terms(query: str) -> List[str]:
    terms = [t.strip().lower() for t in query.split() if t.strip()]
    filtered = [t for t in terms if t not in _STOP_WORDS and len(t) > 2]
    # fall back to all terms if filtering removed everything
    return filtered if filtered else terms


def _score(text_lower: str, terms: List[str]) -> int:
    return sum(1 for term in terms if term in text_lower)


def get_context(query: str, max_chars: int = 12000, top_k: int = 5) -> str:
    bucket = os.getenv("S3_BUCKET", "upou-admissions-kb-1")
    s3 = boto3.client("s3")

    if not query:
        return ""

    terms = _meaningful_terms(query)
    if not terms:
        return ""

    logger.info("Retrieval query terms: %s", terms)

    scored: List[Tuple[int, str]] = []
    for obj in _list_bucket_objects(s3, bucket):
        key = obj.get("Key", "")
        try:
            resp = s3.get_object(Bucket=bucket, Key=key)
            body = resp["Body"].read().decode("utf-8")
        except Exception:
            logger.exception("Failed to read %s", key)
            continue

        score = _score(body.lower(), terms)
        if score > 0:
            scored.append((score, body))

    if not scored:
        return ""

    # sort highest score first, take top_k documents
    scored.sort(key=lambda x: x[0], reverse=True)
    top_docs = [body for _, body in scored[:top_k]]

    logger.info("Retrieved %d relevant documents (top score: %d)", len(top_docs), scored[0][0])

    context = "\n---\n".join(top_docs)
    if len(context) > max_chars:
        context = context[:max_chars]
        last_newline = context.rfind("\n")
        if last_newline > 0:
            context = context[:last_newline]

    return context