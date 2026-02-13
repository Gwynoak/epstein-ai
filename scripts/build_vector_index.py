import os
import json
import numpy as np
import faiss
import torch
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(filename="embedding.log", level=logging.INFO)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CHUNKS_PATH = os.path.join(PROJECT_ROOT, "processed", "chunks.jsonl")
INDEX_PATH = os.path.join(PROJECT_ROOT, "processed", "faiss.index")
META_PATH = os.path.join(PROJECT_ROOT, "processed", "chunk_metadata.jsonl")
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "processed", "embedding_checkpoint.json")

MODEL_NAME = "BAAI/bge-large-en-v1.5"
BATCH_SIZE = 64
SAVE_INTERVAL = 5000  # save FAISS every N chunks

print("Index path:", INDEX_PATH)
print("Checkpoint path:", CHECKPOINT_PATH)


def load_checkpoint():
    if not os.path.exists(CHECKPOINT_PATH):
        return 0
    with open(CHECKPOINT_PATH, "r") as f:
        return json.load(f).get("last_index", 0)


def save_checkpoint(index_position):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump({"last_index": index_position}, f)


def main():
    print("Loading embedding model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(MODEL_NAME, device=device)
    print(f"Using device: {device}")

    print("Loading or creating FAISS index...")

    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        print("Existing index loaded.")
    else:
        dummy = model.encode(["test"], convert_to_numpy=True)
        dimension = dummy.shape[1]
        index = faiss.IndexFlatIP(dimension)
        print("New index created.")

    start_position = load_checkpoint()
    print(f"Resuming from chunk #{start_position}")

    batch_texts = []
    batch_meta = []
    current_position = 0
    total_added = 0

    with open(CHUNKS_PATH, "r", encoding="utf-8") as chunk_file, \
         open(META_PATH, "a", encoding="utf-8") as meta_file:

        for line in tqdm(chunk_file):
            if current_position < start_position:
                current_position += 1
                continue

            record = json.loads(line)

            batch_texts.append(record["text"])
            batch_meta.append({
                "chunk_id": record["chunk_id"],
                "doc_id": record["doc_id"],
                "dataset": record["dataset"],
                "folder": record["folder"],
                "filename": record["filename"]
            })

            if len(batch_texts) >= BATCH_SIZE:
                embeddings = model.encode(
                    batch_texts,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )

                index.add(embeddings)

                for meta in batch_meta:
                    meta_file.write(json.dumps(meta) + "\n")

                total_added += len(batch_texts)
                current_position += len(batch_texts)

                batch_texts = []
                batch_meta = []

                if total_added % SAVE_INTERVAL == 0:
                    print("Saving intermediate index...")
                    faiss.write_index(index, INDEX_PATH)
                    save_checkpoint(current_position)

        # Final flush
        if batch_texts:
            embeddings = model.encode(
                batch_texts,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            index.add(embeddings)

            for meta in batch_meta:
                meta_file.write(json.dumps(meta) + "\n")

            current_position += len(batch_texts)

    print("Saving final index...")
    faiss.write_index(index, INDEX_PATH)
    save_checkpoint(current_position)

    print("Embedding complete.")


if __name__ == "__main__":
    main()
