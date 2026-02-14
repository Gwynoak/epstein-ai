import os
import json
import re
from multiprocessing import Pool, cpu_count

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

INPUT_PATH = os.path.join(PROJECT_ROOT, "processed", "documents.jsonl")
CLEAN_PATH = os.path.join(PROJECT_ROOT, "processed", "documents_clean.jsonl")
SCRUBBED_PATH = os.path.join(PROJECT_ROOT, "processed", "documents_scrubbed_out.jsonl")

WORD_PATTERN = re.compile(r"[A-Za-z]{3,}")
DIGIT_PATTERN = re.compile(r"\d+")

MAX_WORKERS = int(cpu_count() * 0.7)


def compute_keep_flag(record):
    text = record.get("text", "")

    total_chars = len(text)
    if total_chars == 0:
        return False

    alpha_chars = sum(c.isalpha() for c in text)
    alpha_ratio = alpha_chars / total_chars

    real_words = WORD_PATTERN.findall(text)
    real_word_count = len(real_words)

    digit_tokens = len(DIGIT_PATTERN.findall(text))

    if real_word_count < 5 and digit_tokens < 3 and alpha_ratio < 0.2:
        return False

    return True


def main():
    print("Loading documents into memory...")

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        documents = [json.loads(line) for line in f]

    print(f"Total documents loaded: {len(documents)}")
    print(f"Using {MAX_WORKERS} workers")

    with Pool(MAX_WORKERS) as pool:
        keep_flags = pool.map(compute_keep_flag, documents)

    kept = []
    removed = []

    for record, keep in zip(documents, keep_flags):
        if keep:
            kept.append(record)
        else:
            removed.append(record)

    print("Writing clean documents...")
    with open(CLEAN_PATH, "w", encoding="utf-8") as f:
        for record in kept:
            f.write(json.dumps(record) + "\n")

    print("Writing scrubbed documents...")
    with open(SCRUBBED_PATH, "w", encoding="utf-8") as f:
        for record in removed:
            f.write(json.dumps(record) + "\n")

    print("\n====================================")
    print("Scrub complete.")
    print("Kept:", len(kept))
    print("Removed:", len(removed))
    print("====================================")


if __name__ == "__main__":
    main()
