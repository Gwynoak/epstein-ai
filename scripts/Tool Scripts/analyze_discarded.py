import json
import os
import fitz
from tqdm import tqdm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

DISCARDED_PATH = os.path.join(PROJECT_ROOT, "processed", "discarded.jsonl")
RAW_ROOT = os.path.join(PROJECT_ROOT, "raw_pdfs")

length_buckets = {
    "<10 words": 0,
    "10-30 words": 0,
    "30-100 words": 0,
    "100-300 words": 0,
    "300+ words": 0
}

total = 0

with open(DISCARDED_PATH, "r", encoding="utf-8") as f:
    for line in tqdm(f):
        record = json.loads(line)
        source_path = record["source_path"]

        full_path = os.path.join(RAW_ROOT, source_path)

        try:
            doc = fitz.open(full_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()

            words = text.split()
            wc = len(words)

            if wc < 10:
                length_buckets["<10 words"] += 1
            elif wc < 30:
                length_buckets["10-30 words"] += 1
            elif wc < 100:
                length_buckets["30-100 words"] += 1
            elif wc < 300:
                length_buckets["100-300 words"] += 1
            else:
                length_buckets["300+ words"] += 1

            total += 1

        except:
            continue

print("\nTotal analyzed:", total)
for k, v in length_buckets.items():
    print(k, ":", v)
