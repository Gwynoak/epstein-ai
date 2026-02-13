import os
import json
import fitz
import re
from tqdm import tqdm

# -------- PATH RESOLUTION --------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

DISCARDED_PATH = os.path.join(PROJECT_ROOT, "processed", "discarded.jsonl")
DOCUMENTS_PATH = os.path.join(PROJECT_ROOT, "processed", "documents.jsonl")
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "processed", "recovery_checkpoint.json")
RAW_ROOT = os.path.join(PROJECT_ROOT, "raw_pdfs")

# -------- CONFIG --------
MIN_REAL_WORDS = 15
MIN_ALPHA_RATIO = 0.30

WORD_PATTERN = re.compile(r"[A-Za-z]{3,}")

def load_checkpoint():
    if not os.path.exists(CHECKPOINT_PATH):
        return 0
    with open(CHECKPOINT_PATH, "r") as f:
        return json.load(f).get("line_index", 0)

def save_checkpoint(index):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump({"line_index": index}, f)

def compute_metrics(text):
    total_chars = len(text)
    if total_chars == 0:
        return 0, 0

    alpha_chars = sum(c.isalpha() for c in text)
    alpha_ratio = alpha_chars / total_chars

    words = WORD_PATTERN.findall(text)
    real_word_count = len(words)

    return real_word_count, alpha_ratio

def main():
    start_index = load_checkpoint()
    print("Resuming from discarded line:", start_index)

    recovered = 0
    total_processed = 0

    with open(DISCARDED_PATH, "r", encoding="utf-8") as discard_file, \
         open(DOCUMENTS_PATH, "a", encoding="utf-8") as doc_file:

        for idx, line in enumerate(tqdm(discard_file)):
            if idx < start_index:
                continue

            record = json.loads(line)
            source_path = record["source_path"]
            full_path = os.path.join(RAW_ROOT, source_path)

            try:
                doc = fitz.open(full_path)
                text = ""
                for page in doc:
                    text += page.get_text("text") + "\n"
                doc.close()

                text = text.strip()

                real_word_count, alpha_ratio = compute_metrics(text)

                if real_word_count >= MIN_REAL_WORDS and alpha_ratio >= MIN_ALPHA_RATIO:
                    recovered_record = {
                        "doc_id": record["doc_id"],
                        "dataset": record["dataset"],
                        "folder": record["folder"],
                        "filename": record["filename"],
                        "source_path": record["source_path"],
                        "char_count": len(text),
                        "word_count": len(text.split()),
                        "has_text": True,
                        "text": text
                    }

                    doc_file.write(json.dumps(recovered_record) + "\n")
                    recovered += 1

                total_processed += 1

                if total_processed % 500 == 0:
                    save_checkpoint(idx)

            except Exception:
                continue

    save_checkpoint(total_processed)

    print("\n====================================")
    print("Recovery complete.")
    print("Recovered documents:", recovered)
    print("====================================")

if __name__ == "__main__":
    main()
