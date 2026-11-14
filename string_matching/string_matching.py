import random

def brute_force(text, pattern):
    n = len(text)
    m = len(pattern)
    comparisons = 0
    positions = []
    for i in range(n - m + 1):
        match = True
        for j in range(m):
            comparisons += 1
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            positions.append(i)
    return positions, comparisons

def kmp_prefix(pattern):
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp(text, pattern):
    n = len(text)
    m = len(pattern)
    lps = kmp_prefix(pattern)
    comparisons = 0
    positions = []
    i = 0
    j = 0
    while i < n:
        comparisons += 1
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                positions.append(i - j)
                j = lps[j - 1]
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return positions, comparisons

def bmh(text, pattern):
    n = len(text)
    m = len(pattern)
    shift = {c: m for c in set(text)}
    for i in range(m - 1):
        shift[pattern[i]] = m - 1 - i
    comparisons = 0
    positions = []
    i = 0
    while i <= n - m:
        j = m - 1
        while j >= 0:
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            j -= 1
        if j < 0:
            positions.append(i)
            i += m
        else:
            i += shift.get(text[i + m - 1], m)
    return positions, comparisons

def print_table(name, text, patterns):
    print(f"\n=== {name} TEXT ===")
    print(f"{'Pattern':<10}{'Brute':<10}{'KMP':<10}{'BMH':<10}")
    print("-" * 40)

    for pattern in patterns:
        bf_pos, bf_comp = brute_force(text, pattern)
        kmp_pos, kmp_comp = kmp(text, pattern)
        bmh_pos, bmh_comp = bmh(text, pattern)
        print(f"{pattern:<10}{bf_comp:<10}{kmp_comp:<10}{bmh_comp:<10}")

short_text = "THISISASIMPLEEXAMPLETOSTUDYPATTERNMATCHINGALGORITHMSINCOMPUTERSCIENCE"
long_text = short_text * 15
dna_text = "".join(random.choice("AGCT") for _ in range(1000))

patterns = ["SIMPLE", "MATCH", "SCIENCE"]

print_table("SHORT", short_text, patterns)
print_table("LONG", long_text, patterns)
print_table("DNA", dna_text, patterns)
