import os
import json
import fitz
from tqdm import tqdm
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_ROOT = os.path.join(PROJECT_ROOT, "raw_pdfs")
PROCESSED_ROOT = os.path.join(PROJECT_ROOT, "processed")

DOCS_PATH = os.path.join(PROCESSED_ROOT, "documents.jsonl")
DISCARDED_PATH = os.path.join(PROCESSED_ROOT, "discarded.jsonl")
CHECKPOINT_PATH = os.path.join(PROCESSED_ROOT, "checkpoints.json")
MIN_TEXT_LENGTH = 300
MAX_WORKERS = 16


def ensure_directories():
    os.makedirs(PROCESSED_ROOT, exist_ok=True)
    if not os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "w") as f:
            json.dump({}, f)


def load_checkpoints():
    with open(CHECKPOINT_PATH, "r") as f:
        return json.load(f)


def save_checkpoints(checkpoints):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(checkpoints, f, indent=2)


def normalize_text(text):
    text = text.replace("\x00", "")
    text = " ".join(text.split())
    return text.strip()


def process_pdf(args):
    dataset_name, dataset_id, folder_name, pdf_file, folder_path = args
    pdf_path = os.path.join(folder_path, pdf_file)

    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()

        text = normalize_text(text)

        doc_id = f"dataset{dataset_id}_{folder_name}_{pdf_file.replace('.pdf','')}"

        record = {
            "doc_id": doc_id,
            "dataset": dataset_id,
            "folder": folder_name,
            "filename": pdf_file,
            "source_path": os.path.join(dataset_name, folder_name, pdf_file),
            "char_count": len(text),
            "word_count": len(text.split()),
            "has_text": len(text) >= MIN_TEXT_LENGTH,
            "ingested_at": datetime.utcnow().isoformat()
        }

        if len(text) < MIN_TEXT_LENGTH:
            record["reason"] = "no_extractable_text"
            return ("discard", record)

        record["text"] = text
        return ("valid", record)

    except Exception as e:
        return ("error", {
            "dataset": dataset_id,
            "folder": folder_name,
            "filename": pdf_file,
            "error": str(e)
        })


def process():
    ensure_directories()
    checkpoints = load_checkpoints()

    total_processed = 0
    total_discarded = 0

    for dataset_name in sorted(os.listdir(RAW_ROOT)):
        dataset_path = os.path.join(RAW_ROOT, dataset_name)

        if not os.path.isdir(dataset_path):
            continue

        dataset_id = dataset_name.replace("Dataset ", "").strip()

        print(f"\n=== Processing {dataset_name} ===")

        if dataset_name not in checkpoints:
            checkpoints[dataset_name] = []

        for folder_name in sorted(os.listdir(dataset_path)):
            folder_path = os.path.join(dataset_path, folder_name)

            if not os.path.isdir(folder_path):
                continue

            if folder_name in checkpoints[dataset_name]:
                print(f"[SKIP] {dataset_name}/{folder_name} already processed.")
                continue

            print(f"\n--- Folder {folder_name} ---")

            pdf_files = [
                f for f in os.listdir(folder_path)
                if f.lower().endswith(".pdf")
            ]

            tasks = [
                (dataset_name, dataset_id, folder_name, pdf_file, folder_path)
                for pdf_file in pdf_files
            ]

            with open(DOCS_PATH, "a", encoding="utf-8") as docs_file, \
                 open(DISCARDED_PATH, "a", encoding="utf-8") as discard_file, \
                 ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:

                futures = [executor.submit(process_pdf, task) for task in tasks]

                for future in tqdm(as_completed(futures), total=len(futures)):
                    result_type, record = future.result()

                    if result_type == "valid":
                        docs_file.write(json.dumps(record) + "\n")
                        total_processed += 1
                    elif result_type == "discard":
                        discard_file.write(json.dumps(record) + "\n")
                        total_discarded += 1
                    else:
                        print(f"[ERROR] {record}")

            checkpoints[dataset_name].append(folder_name)
            save_checkpoints(checkpoints)

            print(f"[DONE] Folder {folder_name} processed.")

    print("\n====================================")
    print(f"Total processed documents: {total_processed}")
    print(f"Total discarded documents: {total_discarded}")
    print("Ingestion complete.")
    print("====================================")


if __name__ == "__main__":
    process()
