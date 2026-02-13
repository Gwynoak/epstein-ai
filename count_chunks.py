count = 0
with open("processed/chunks.jsonl", "r", encoding="utf-8") as f:
    for _ in f:
        count += 1
print(count)