import os
import gzip
import json
import re
import fitz
from warcio.archiveiterator import ArchiveIterator
from tqdm import tqdm

# Dataset 9 was bruteforced by a 3rd party. It was supplied as .warc in .gz folders and required additional scripting to clean and extract

# -------- PATH RESOLUTION --------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

WARC_ROOT = os.path.join(PROJECT_ROOT, "raw_warc")
DATASET_ROOT = os.path.join(PROJECT_ROOT, "raw_pdfs", "Dataset 9")
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "processed", "dataset9_checkpoint.json")

os.makedirs(DATASET_ROOT, exist_ok=True)

# -------- CONFIG --------
PDFS_PER_FOLDER = 1000
EFTA_PATTERN = re.compile(r"EFTA\d+")

# -------- CHECKPOINT --------
def load_checkpoint():
    if not os.path.exists(CHECKPOINT_PATH):
        return []
    with open(CHECKPOINT_PATH, "r") as f:
        return json.load(f)

def save_checkpoint(processed_files):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(processed_files, f, indent=2)

# -------- FOLDER MANAGEMENT --------
def get_current_folder_and_count():
    folders = sorted(os.listdir(DATASET_ROOT))
    if not folders:
        folder = "0001"
        os.makedirs(os.path.join(DATASET_ROOT, folder), exist_ok=True)
        return folder, 0

    folder = folders[-1]
    folder_path = os.path.join(DATASET_ROOT, folder)
    count = len(os.listdir(folder_path))
    return folder, count

# -------- CORE EXTRACTION --------
def process_warc(warc_path):
    print(f"\n=== Processing WARC: {os.path.basename(warc_path)} ===")

    folder, count = get_current_folder_and_count()

    if warc_path.endswith(".gz"):
        stream = gzip.open(warc_path, 'rb')
    else:
        stream = open(warc_path, 'rb')

    with stream:
        for record in tqdm(ArchiveIterator(stream)):
            if record.rec_type != 'response':
                continue

            content_type = record.http_headers.get_header('Content-Type')

            if not content_type or 'application/pdf' not in content_type:
                continue

            try:
                pdf_bytes = record.content_stream().read()

                # Open PDF in memory
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text("text") + "\n"
                doc.close()

                matches = EFTA_PATTERN.findall(text)
                if not matches:
                    continue

                doc_id = matches[-1]  # last occurrence = footer ID
                filename = f"{doc_id}.pdf"

                folder_path = os.path.join(DATASET_ROOT, folder)
                os.makedirs(folder_path, exist_ok=True)

                output_path = os.path.join(folder_path, filename)

                # Deduplicate
                if os.path.exists(output_path):
                    continue

                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)

                count += 1

                # Folder rollover
                if count >= PDFS_PER_FOLDER:
                    folder = f"{int(folder) + 1:04d}"
                    count = 0

            except Exception:
                continue

def main():
    processed_files = load_checkpoint()

    print("WARC ROOT:", WARC_ROOT)
    print("Files detected:", os.listdir(WARC_ROOT))

    for file in sorted(os.listdir(WARC_ROOT)):
        if not (file.endswith(".warc") or file.endswith(".warc.gz")):
            continue

        if file in processed_files:
            print(f"[SKIP] {file} already processed.")
            continue

        warc_path = os.path.join(WARC_ROOT, file)
        process_warc(warc_path)

        processed_files.append(file)
        save_checkpoint(processed_files)

    print("\nDataset 9 extraction complete.")

if __name__ == "__main__":
    main()
