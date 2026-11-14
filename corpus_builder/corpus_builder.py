import os
import re

os.makedirs("corpus", exist_ok=True)

with open("big_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

text = re.sub(r"\s+", " ", text)

sentences = re.split(r'(?<=[.!?])\s+', text)

doc_size = 33
doc_id = 0

for i in range(0, len(sentences), doc_size):
    chunk = sentences[i:i+doc_size]

    if len(chunk) < doc_size:
        continue

    doc_text = " ".join(chunk)

    with open(f"corpus/doc{doc_id}.txt", "w", encoding="utf-8") as f:
        f.write(doc_text)

    doc_id += 1

print(f"Created {doc_id} documents.")
