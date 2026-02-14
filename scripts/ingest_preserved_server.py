import os
import json
import fitz
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# -------- PATHS --------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_ROOT = os.path.join(PROJECT_ROOT, "raw_pdfs")
OUTPUT_ROOT = os.path.join(PROJECT_ROOT, "processed_jsonl")

os.makedirs(OUTPUT_ROOT, exist_ok=True)

MAX_WORKERS = int(cpu_count() * 0.7)

# -------- NORMALIZATION --------
def mild_normalize(text):
    text = text.replace("\x00", "")
    return text.strip()

# -------- SINGLE PDF PROCESS --------
def process_pdf(args):
    dataset_name, folder_name, pdf_filename = args

    pdf_path = os.path.join(RAW_ROOT, dataset_name, folder_name, pdf_filename)

    try:
        doc = fitz.open(pdf_path)

        pages = []
        for i, page in enumerate(doc):
            page_text = page.get_text("text")
            page_text = mild_normalize(page_text)
            pages.append(f"---PAGE {i+1:03d}---\n{page_text}")

        doc.close()

        full_text = "\n\n".join(pages)

        if len(full_text.strip()) < 5:
            return None

        record = {
            "doc_id": pdf_filename.replace(".pdf", ""),
            "dataset": dataset_name.replace("Dataset ", "").strip(),
            "folder": folder_name,
            "filename": pdf_filename,
            "source_path": os.path.join(dataset_name, folder_name, pdf_filename),
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
            "text": full_text
        }

        output_dir = os.path.join(OUTPUT_ROOT, dataset_name, folder_name)
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, pdf_filename.replace(".pdf", ".jsonl"))

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(record))

        return True

    except Exception:
        return None

# -------- MAIN --------
def main():
    tasks = []

    for dataset_name in sorted(os.listdir(RAW_ROOT)):
        dataset_path = os.path.join(RAW_ROOT, dataset_name)
        if not os.path.isdir(dataset_path):
            continue

        for folder_name in sorted(os.listdir(dataset_path)):
            folder_path = os.path.join(dataset_path, folder_name)
            if not os.path.isdir(folder_path):
                continue

            for pdf_filename in os.listdir(folder_path):
                if pdf_filename.lower().endswith(".pdf"):
                    tasks.append((dataset_name, folder_name, pdf_filename))

    print(f"Total PDFs detected: {len(tasks)}")
    print(f"Using {MAX_WORKERS} workers")

    with Pool(MAX_WORKERS) as pool:
        list(tqdm(pool.imap_unordered(process_pdf, tasks), total=len(tasks)))

    print("Ingestion complete.")

if __name__ == "__main__":
    main()
