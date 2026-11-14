import os
import re
import math
from collections import Counter
from itertools import combinations

stopwords = {'the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'that', 'for'}

folder = "corpus"
documents = {}

for filename in os.listdir(folder):
    if filename.endswith(".txt"):
        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            documents[filename] = f.read()

doc_ids = sorted(documents.keys())
documents = {doc_id: documents[doc_id] for doc_id in doc_ids}

def preprocess(text):
    text = text.lower()
    tokens = re.findall(r'[a-z0-9]+', text)
    terms = [token for token in tokens if token not in stopwords]
    return terms

processed_docs = {}
for doc_id, text in documents.items():
    processed_docs[doc_id] = preprocess(text)

def compute_tf(terms):
    counts = Counter(terms)
    total = len(terms)
    tf = {}
    for term, count in counts.items():
        tf[term] = count / total
    return tf

tf = {}
for doc_id, terms in processed_docs.items():
    tf[doc_id] = compute_tf(terms)

N = len(processed_docs)

df = Counter()
for terms in processed_docs.values():
    unique_terms = set(terms)
    for term in unique_terms:
        df[term] += 1

idf = {}
for term, freq in df.items():
    idf[term] = math.log(N / freq)

tf_idf = {}
for doc_id, tf_doc in tf.items():
    tf_idf[doc_id] = {}
    for term, tf_value in tf_doc.items():
        tf_idf[doc_id][term] = tf_value * idf[term]

def score_query(query, tf_idf_vectors):
    query_terms = preprocess(query)
    scores = {}
    for doc_id, weights in tf_idf_vectors.items():
        score = 0
        for term in query_terms:
            score += weights.get(term, 0)
        scores[doc_id] = score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked

def cosine_similarity(vec1, vec2):
    all_terms = set(vec1.keys()) | set(vec2.keys())
    dot_product = 0
    for term in all_terms:
        dot_product += vec1.get(term, 0) * vec2.get(term, 0)
    norm1 = math.sqrt(sum(value * value for value in vec1.values()))
    norm2 = math.sqrt(sum(value * value for value in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot_product / (norm1 * norm2)

tfidf_similarities = []
for doc1, doc2 in combinations(doc_ids, 2):
    sim = cosine_similarity(tf_idf[doc1], tf_idf[doc2])
    tfidf_similarities.append((doc1, doc2, sim))

tfidf_similarities.sort(key=lambda x: x[2], reverse=True)
most_similar_tfidf = tfidf_similarities[0]

tf_similarities = []
for doc1, doc2 in combinations(doc_ids, 2):
    sim = cosine_similarity(tf[doc1], tf[doc2])
    tf_similarities.append((doc1, doc2, sim))

tf_similarities.sort(key=lambda x: x[2], reverse=True)
most_similar_tf = tf_similarities[0]

query = "artificial intelligence machine learning"
ranked_documents = score_query(query, tf_idf)

print("NUMBER OF DOCUMENTS:")
print(N)

print("\nPREPROCESSED TERMS FOR EACH DOCUMENT:")
for doc_id, terms in processed_docs.items():
    print(doc_id, "->", terms[:40])

print("\nTF EXAMPLE FROM FIRST DOCUMENT:")
first_doc = doc_ids[0]
for term, value in list(tf[first_doc].items())[:20]:
    print(term, ":", value)

print("\nIDF EXAMPLE:")
for term, value in list(idf.items())[:20]:
    print(term, ":", value)

print("\nTF-IDF EXAMPLE FROM FIRST DOCUMENT:")
for term, value in list(tf_idf[first_doc].items())[:20]:
    print(term, ":", value)

print("\nQUERY:")
print(query)

print("\nDOCUMENTS SORTED BY QUERY SCORE:")
for doc_id, score in ranked_documents:
    print(doc_id, ":", score)

print("\nMOST SIMILAR DOCUMENTS USING TF-IDF COSINE SIMILARITY:")
print(most_similar_tfidf[0], most_similar_tfidf[1], most_similar_tfidf[2])

print("\nMOST SIMILAR DOCUMENTS USING TF ONLY COSINE SIMILARITY:")
print(most_similar_tf[0], most_similar_tf[1], most_similar_tf[2])
