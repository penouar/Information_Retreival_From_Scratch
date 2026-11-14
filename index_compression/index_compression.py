import random
import string
import time
from bisect import bisect_left

VOCAB_SIZE = 1000
DOC_COUNT = 10000
PAIR_COUNT = 1_000_000
WORD_MIN_LEN = 3
WORD_MAX_LEN = 10
random.seed(42)

def generate_unique_words(n, min_len=3, max_len=10):
    words = set()
    letters = string.ascii_lowercase
    while len(words) < n:
        length = random.randint(min_len, max_len)
        word = ''.join(random.choice(letters) for _ in range(length))
        words.add(word)
    return list(words)

def generate_counts(total_pairs, vocab_size, max_per_word):
    weights = [random.random() + 0.1 for _ in range(vocab_size)]
    total_weight = sum(weights)
    counts = [max(1, int(total_pairs * w / total_weight)) for w in weights]
    diff = total_pairs - sum(counts)
    while diff > 0:
        i = random.randrange(vocab_size)
        if counts[i] < max_per_word:
            counts[i] += 1
            diff -= 1
    while diff < 0:
        i = random.randrange(vocab_size)
        if counts[i] > 1:
            counts[i] -= 1
            diff += 1
    return counts

def build_inverted_index(words, counts, doc_count):
    index = {}
    for word, count in zip(words, counts):
        docs = sorted(random.sample(range(1, doc_count + 1), count))
        index[word] = docs
    return index

def to_gaps(doc_ids):
    if not doc_ids:
        return []
    gaps = [doc_ids[0]]
    for i in range(1, len(doc_ids)):
        gaps.append(doc_ids[i] - doc_ids[i - 1])
    return gaps

def from_gaps(gaps):
    if not gaps:
        return []
    doc_ids = [gaps[0]]
    for i in range(1, len(gaps)):
        doc_ids.append(doc_ids[-1] + gaps[i])
    return doc_ids

def unary_encode_number(n):
    return '0' * (n - 1) + '1'

def unary_decode_stream(bits):
    numbers = []
    zeros = 0
    for b in bits:
        if b == '0':
            zeros += 1
        else:
            numbers.append(zeros + 1)
            zeros = 0
    return numbers

def gamma_encode_number(n):
    binary = bin(n)[2:]
    length_part = unary_encode_number(len(binary))
    offset = binary[1:]
    return length_part + offset

def gamma_decode_stream(bits):
    numbers = []
    i = 0
    while i < len(bits):
        zeros = 0
        while i < len(bits) and bits[i] == '0':
            zeros += 1
            i += 1
        if i >= len(bits):
            break
        i += 1
        length = zeros + 1
        if length == 1:
            numbers.append(1)
        else:
            offset = bits[i:i + length - 1]
            i += length - 1
            numbers.append(int('1' + offset, 2))
    return numbers

def fibonacci_numbers_up_to(n):
    fibs = [1, 2]
    while fibs[-1] <= n:
        fibs.append(fibs[-1] + fibs[-2])
    if fibs[-1] > n:
        fibs.pop()
    return fibs

def fibonacci_encode_number(n):
    fibs = fibonacci_numbers_up_to(n)
    bits = [0] * len(fibs)
    remaining = n
    for i in range(len(fibs) - 1, -1, -1):
        if fibs[i] <= remaining:
            bits[i] = 1
            remaining -= fibs[i]
    return ''.join(str(bit) for bit in bits) + '1'

def fibonacci_decode_token(token_bits):
    fibs = [1, 2]
    while len(fibs) < len(token_bits):
        fibs.append(fibs[-1] + fibs[-2])
    value = 0
    for bit, fib in zip(token_bits, fibs):
        if bit == '1':
            value += fib
    return value

def fibonacci_decode_stream(bits):
    numbers = []
    current = ''
    for b in bits:
        current += b
        if len(current) >= 2 and current[-2:] == '11':
            token = current[:-1]
            numbers.append(fibonacci_decode_token(token))
            current = ''
    return numbers

def encode_list(numbers, encode_number):
    return ''.join(encode_number(n) for n in numbers)

def binary_search(sorted_list, target):
    pos = bisect_left(sorted_list, target)
    return pos < len(sorted_list) and sorted_list[pos] == target

def textual_gap_size(gaps):
    return len(' '.join(map(str, gaps)))

def prepare_variants(index):
    gap_lists = {word: to_gaps(doc_ids) for word, doc_ids in index.items()}
    unary_encoded = {word: encode_list(gaps, unary_encode_number) for word, gaps in gap_lists.items()}
    gamma_encoded = {word: encode_list(gaps, gamma_encode_number) for word, gaps in gap_lists.items()}
    fibonacci_encoded = {word: encode_list(gaps, fibonacci_encode_number) for word, gaps in gap_lists.items()}
    return gap_lists, unary_encoded, gamma_encoded, fibonacci_encoded

def total_size_text(gap_lists):
    return sum(textual_gap_size(gaps) for gaps in gap_lists.values())

def total_size_bits(encoded_lists):
    return sum(len(bits) for bits in encoded_lists.values())

def search_plain(index, target_doc):
    found = 0
    for doc_ids in index.values():
        if binary_search(doc_ids, target_doc):
            found += 1
    return found

def search_compressed(encoded_lists, decode_stream, target_doc):
    found = 0
    for bits in encoded_lists.values():
        gaps = decode_stream(bits)
        doc_ids = from_gaps(gaps)
        if binary_search(doc_ids, target_doc):
            found += 1
    return found

def time_function(func, repeats=3):
    best = float('inf')
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = func()
        elapsed = time.perf_counter() - start
        best = min(best, elapsed)
    return result, best

words = generate_unique_words(VOCAB_SIZE, WORD_MIN_LEN, WORD_MAX_LEN)
counts = generate_counts(PAIR_COUNT, VOCAB_SIZE, DOC_COUNT)
index = build_inverted_index(words, counts, DOC_COUNT)
gap_lists, unary_encoded, gamma_encoded, fibonacci_encoded = prepare_variants(index)

sample_numbers = [1, 2, 3, 4, 5, 10]
print("SAMPLE ENCODING TEST")
for n in sample_numbers:
    u = unary_encode_number(n)
    g = gamma_encode_number(n)
    f = fibonacci_encode_number(n)
    print(f"{n}: unary={u}, gamma={g}, fibonacci={f}")

print("\nSAMPLE DECODING TEST")
sample_stream_unary = ''.join(unary_encode_number(n) for n in sample_numbers)
sample_stream_gamma = ''.join(gamma_encode_number(n) for n in sample_numbers)
sample_stream_fibonacci = ''.join(fibonacci_encode_number(n) for n in sample_numbers)
print("Unary decoded:", unary_decode_stream(sample_stream_unary))
print("Gamma decoded:", gamma_decode_stream(sample_stream_gamma))
print("Fibonacci decoded:", fibonacci_decode_stream(sample_stream_fibonacci))

text_size = total_size_text(gap_lists)
unary_size = total_size_bits(unary_encoded)
gamma_size = total_size_bits(gamma_encoded)
fibonacci_size = total_size_bits(fibonacci_encoded)

print("\nSIZE COMPARISON")
print("Textual gap list size:", text_size, "characters")
print("Unary encoded size:", unary_size, "bits")
print("Gamma encoded size:", gamma_size, "bits")
print("Fibonacci encoded size:", fibonacci_size, "bits")
print("Unary compression ratio vs text:", round(unary_size / text_size, 4))
print("Gamma compression ratio vs text:", round(gamma_size / text_size, 4))
print("Fibonacci compression ratio vs text:", round(fibonacci_size / text_size, 4))

target_doc = random.randint(1, DOC_COUNT)
print("\nSEARCH TEST")
print("Target docID:", target_doc)

plain_found, plain_time = time_function(lambda: search_plain(index, target_doc))
unary_found, unary_time = time_function(lambda: search_compressed(unary_encoded, unary_decode_stream, target_doc))
gamma_found, gamma_time = time_function(lambda: search_compressed(gamma_encoded, gamma_decode_stream, target_doc))
fibonacci_found, fibonacci_time = time_function(lambda: search_compressed(fibonacci_encoded, fibonacci_decode_stream, target_doc))

print("Plain search result:", plain_found, "lists contain the docID")
print("Unary search result:", unary_found, "lists contain the docID")
print("Gamma search result:", gamma_found, "lists contain the docID")
print("Fibonacci search result:", fibonacci_found, "lists contain the docID")

print("\nTIME COMPARISON")
print("Plain search time:", plain_time)
print("Unary search time:", unary_time)
print("Gamma search time:", gamma_time)
print("Fibonacci search time:", fibonacci_time)

print("\nSLOWDOWN VS PLAIN")
print("Unary slowdown:", round(unary_time / plain_time, 2))
print("Gamma slowdown:", round(gamma_time / plain_time, 2))
print("Fibonacci slowdown:", round(fibonacci_time / plain_time, 2))
