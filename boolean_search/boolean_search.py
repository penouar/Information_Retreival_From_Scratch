import os
import re
from collections import defaultdict, Counter

STOPWORDS = {
    "a", "an", "the", "and", "or", "not", "is", "are", "was", "were", "in", "on", "at", "to",
    "of", "for", "with", "by", "from", "as", "it", "this", "that", "these", "those", "be",
    "been", "being", "has", "have", "had", "do", "does", "did", "but", "if", "then", "than",
    "so", "such", "into", "about", "over", "under", "after", "before", "between", "during",
    "without", "within", "can", "could", "should", "would", "may", "might", "will", "shall",
    "i", "you", "he", "she", "we", "they", "them", "their", "our", "your", "his", "her", "its"
}

def load_documents(folder="corpus"):
    documents = []
    names = []
    for filename in sorted(os.listdir(folder)):
        if filename.lower().endswith(".txt"):
            path = os.path.join(folder, filename)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read().strip()
                if text:
                    documents.append(text)
                    names.append(filename)
    if len(documents) < 500:
        raise ValueError("The corpus must contain at least 500 non-empty .txt documents.")
    return documents, names

def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]

def first_sentence(text):
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return parts[0] if parts and parts[0] else text[:120].strip()

def build_inverted_index(documents):
    index = defaultdict(dict)
    doc_term_freqs = {}
    for doc_id, text in enumerate(documents):
        tokens = tokenize(text)
        counts = Counter(tokens)
        doc_term_freqs[doc_id] = dict(counts)
        for term, freq in counts.items():
            index[term][doc_id] = freq
    return dict(index), doc_term_freqs

def build_compact_index(index):
    compact = {}
    for term, postings in index.items():
        sorted_postings = sorted(postings.items())
        gaps = []
        freqs = []
        previous_doc_id = 0
        for doc_id, freq in sorted_postings:
            gaps.append(doc_id - previous_doc_id)
            freqs.append(freq)
            previous_doc_id = doc_id
        compact[term] = {"gaps": gaps, "freqs": freqs}
    return compact

def decode_compact_posting(compact_posting):
    doc_ids = []
    current = 0
    for gap in compact_posting["gaps"]:
        current += gap
        doc_ids.append(current)
    return doc_ids

def tokenize_query(query):
    query = query.replace("(", " ( ").replace(")", " ) ")
    parts = query.split()
    tokens = []
    for part in parts:
        upper = part.upper()
        if upper in {"AND", "OR", "NOT", "(", ")"}:
            tokens.append(upper)
        else:
            tokens.append(part.lower())
    return tokens

def validate_query(tokens):
    if not tokens:
        return False
    balance = 0
    prev = None
    for token in tokens:
        if token == "(":
            balance += 1
        elif token == ")":
            balance -= 1
            if balance < 0:
                return False
        if prev is None:
            if token in {"AND", "OR", ")"}:
                return False
        else:
            if prev not in {"AND", "OR", "NOT", "("} and token not in {"AND", "OR", ")"}:
                return False
            if prev in {"AND", "OR"} and token in {"AND", "OR", ")"}:
                return False
            if prev == "NOT" and token in {"AND", "OR", "NOT", ")"}:
                return False
            if prev == "(" and token in {"AND", "OR", ")"}:
                return False
            if prev == ")" and token not in {"AND", "OR", ")"}:
                return False
        prev = token
    if balance != 0:
        return False
    if tokens[-1] in {"AND", "OR", "NOT", "("}:
        return False
    return True

def to_postfix(tokens):
    precedence = {"NOT": 3, "AND": 2, "OR": 1}
    output = []
    stack = []
    for token in tokens:
        if token not in {"AND", "OR", "NOT", "(", ")"}:
            output.append(token)
        elif token == "(":
            stack.append(token)
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and stack[-1] != "(" and precedence[stack[-1]] >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
    while stack:
        output.append(stack.pop())
    return output

def evaluate_postfix(postfix, index, all_docs):
    stack = []
    for token in postfix:
        if token == "AND":
            right = stack.pop()
            left = stack.pop()
            stack.append(left & right)
        elif token == "OR":
            right = stack.pop()
            left = stack.pop()
            stack.append(left | right)
        elif token == "NOT":
            operand = stack.pop()
            stack.append(all_docs - operand)
        else:
            stack.append(set(index.get(token, {}).keys()))
    return stack[0] if stack else set()

def boolean_search(query, index, all_docs):
    tokens = tokenize_query(query)
    if not validate_query(tokens):
        raise ValueError("Invalid Boolean query.")
    postfix = to_postfix(tokens)
    return evaluate_postfix(postfix, index, all_docs)

def extract_query_terms(tokens):
    positive_terms = []
    negative_terms = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "NOT" and i + 1 < len(tokens) and tokens[i + 1] not in {"AND", "OR", "NOT", "(", ")"}:
            negative_terms.append(tokens[i + 1])
            i += 2
        elif tokens[i] not in {"AND", "OR", "NOT", "(", ")"}:
            positive_terms.append(tokens[i])
            i += 1
        else:
            i += 1
    return positive_terms, negative_terms

def extended_boolean_search(query, index, doc_term_freqs, all_docs):
    tokens = tokenize_query(query)
    if not validate_query(tokens):
        raise ValueError("Invalid Boolean query.")
    boolean_hits = boolean_search(query, index, all_docs)
    positive_terms, negative_terms = extract_query_terms(tokens)
    ranked_results = []
    for doc_id in boolean_hits:
        freqs = doc_term_freqs[doc_id]
        max_tf = max(freqs.values()) if freqs else 1
        positive_score = 0.0
        for term in positive_terms:
            positive_score += freqs.get(term, 0) / max_tf
        if positive_terms:
            positive_score /= len(positive_terms)
        coverage = len(set(positive_terms) & set(freqs.keys())) / max(1, len(set(positive_terms)))
        negative_penalty = 0.0
        for term in negative_terms:
            negative_penalty += freqs.get(term, 0) / max_tf
        score = 0.8 * positive_score + 0.2 * coverage - 0.3 * negative_penalty
        ranked_results.append((doc_id, score))
    ranked_results.sort(key=lambda x: (-x[1], x[0]))
    return ranked_results

def index_statistics(index):
    token_count = len(index)
    posting_lengths = [len(postings) for postings in index.values()]
    average_posting_length = sum(posting_lengths) / token_count if token_count else 0
    total_entries = sum(posting_lengths)
    return token_count, average_posting_length, total_entries

def compact_index_statistics(compact_index):
    total_gap_values = sum(len(posting["gaps"]) for posting in compact_index.values())
    total_freq_values = sum(len(posting["freqs"]) for posting in compact_index.values())
    return total_gap_values, total_freq_values

def show_boolean_results(doc_ids, documents, names, limit=5):
    if not doc_ids:
        print("No matching documents found.")
        return
    for doc_id in sorted(doc_ids)[:limit]:
        print(f"Document {doc_id} ({names[doc_id]}): {first_sentence(documents[doc_id])}")

def show_ranked_results(results, documents, names, limit=5):
    if not results:
        print("No ranked results found.")
        return
    for doc_id, score in results[:limit]:
        print(f"Document {doc_id} ({names[doc_id]}) | Score = {score:.4f}: {first_sentence(documents[doc_id])}")

def compare_models(query, index, doc_term_freqs, documents, names, all_docs):
    boolean_hits = boolean_search(query, index, all_docs)
    ranked_hits = extended_boolean_search(query, index, doc_term_freqs, all_docs)
    print("\nSTANDARD BOOLEAN MODEL")
    print("Matched documents:", len(boolean_hits))
    show_boolean_results(boolean_hits, documents, names)
    print("\nEXTENDED BOOLEAN MODEL")
    print("Ranked documents:", len(ranked_hits))
    show_ranked_results(ranked_hits, documents, names)

documents, names = load_documents("corpus")
index, doc_term_freqs = build_inverted_index(documents)
compact_index = build_compact_index(index)
all_docs = set(range(len(documents)))

token_count, avg_posting_length, total_entries = index_statistics(index)
gap_count, freq_count = compact_index_statistics(compact_index)

print("INDEX STATISTICS")
print("Number of unique tokens:", token_count)
print("Average posting list length:", round(avg_posting_length, 2))
print("Total number of entries:", total_entries)

print("\nCOMPACT INDEX STATISTICS")
print("Total gap values:", gap_count)
print("Total frequency values:", freq_count)

sample_query = "(data AND search) OR retrieval"
print("\nSAMPLE QUERY")
print("Query:", sample_query)
compare_models(sample_query, index, doc_term_freqs, documents, names, all_docs)

print("\nINTERACTIVE QUERY MODE")
print("Use AND, OR, NOT and parentheses.")
print("Type exit to stop.")

while True:
    user_query = input("\nQuery: ").strip()
    if user_query.lower() == "exit":
        break
    try:
        compare_models(user_query, index, doc_term_freqs, documents, names, all_docs)
    except ValueError as e:
        print(e)
