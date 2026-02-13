import os
import json
from tqdm import tqdm

# Resolve project root dynamically
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DOCS_PATH = os.path.join(PROJECT_ROOT, "processed", "documents.jsonl")
CHUNKS_PATH = os.path.join(PROJECT_ROOT, "processed", "chunks.jsonl")

MAX_CHUNK_WORDS = 1200
TARGET_CHUNK_WORDS = 1000


def split_into_paragraphs(text):
    # Assume paragraphs separated by double newline originally
    # Since ingestion collapsed whitespace, we approximate using sentence breaks
    # We treat periods followed by space as potential breakpoints
    return text.split(". ")


def chunk_text(doc_record):
    text = doc_record["text"]
    words = text.split()

    if len(words) <= MAX_CHUNK_WORDS:
        return [{
            "chunk_index": 0,
            "text": text,
            "word_count": len(words)
        }]

    # For large docs, chunk based on word windows
    chunks = []
    current_chunk = []
    current_word_count = 0
    chunk_index = 0

    for word in words:
        current_chunk.append(word)
        current_word_count += 1

        if current_word_count >= TARGET_CHUNK_WORDS:
            chunk_text = " ".join(current_chunk).strip()
            chunks.append({
                "chunk_index": chunk_index,
                "text": chunk_text,
                "word_count": current_word_count
            })
            chunk_index += 1
            current_chunk = []
            current_word_count = 0

    # Handle remainder
    if current_chunk:
        chunk_text = " ".join(current_chunk).strip()
        chunks.append({
            "chunk_index": chunk_index,
            "text": chunk_text,
            "word_count": current_word_count
        })

    return chunks


def process():
    total_docs = 0
    total_chunks = 0
    large_docs = 0

    with open(DOCS_PATH, "r", encoding="utf-8") as docs_file, \
         open(CHUNKS_PATH, "w", encoding="utf-8") as chunks_file:

        for line in tqdm(docs_file):
            doc = json.loads(line)

            total_docs += 1

            doc_chunks = chunk_text(doc)

            if len(doc_chunks) > 1:
                large_docs += 1

            for chunk in doc_chunks:
                chunk_record = {
                    "chunk_id": f"{doc['doc_id']}_{chunk['chunk_index']}",
                    "doc_id": doc["doc_id"],
                    "dataset": doc["dataset"],
                    "folder": doc["folder"],
                    "filename": doc["filename"],
                    "chunk_index": chunk["chunk_index"],
                    "word_count": chunk["word_count"],
                    "text": chunk["text"]
                }

                chunks_file.write(json.dumps(chunk_record) + "\n")
                total_chunks += 1

    print("\n====================================")
    print(f"Total documents processed: {total_docs}")
    print(f"Total chunks created: {total_chunks}")
    print(f"Documents requiring splitting: {large_docs}")
    print("Chunking complete.")
    print("====================================")


if __name__ == "__main__":
    process()
