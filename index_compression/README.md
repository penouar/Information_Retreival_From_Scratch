# index_compression

Compresses the posting lists of an inverted index with unary, Elias gamma and Fibonacci codes, then measures how much space is saved and how much slower searching gets.

## What it does

`index_compression.py` builds a synthetic index: 1,000 random words, 10,000 documents and 1,000,000 word-document pairs in total (the random seed is fixed). Each posting list is converted to gaps between consecutive document ids, and the gaps are encoded with:

- **unary**
- **Elias gamma**
- **Fibonacci** (Zeckendorf) coding

Each code has an encoder and a decoder. The script:

1. checks the three codes on a few numbers and decodes them back
2. compares the encoded sizes with the plain-text gap lists
3. looks for a random document id in every list, once with binary search on the plain lists and once by decoding each list first, and reports the timings and the slowdown

## Run

From the repository root:

```
python index_compression/index_compression.py
```

Standard library only, about 10 seconds.

## Sample output

```
1: unary=1, gamma=1, fibonacci=11
2: unary=01, gamma=010, fibonacci=011
3: unary=001, gamma=011, fibonacci=0011
4: unary=0001, gamma=00100, fibonacci=1011
5: unary=00001, gamma=00101, fibonacci=00011
10: unary=0000000001, gamma=0001010, fibonacci=010011

Textual gap list size: 2336135 characters
Unary encoded size: 9987119 bits
Gamma encoded size: 5431166 bits
Fibonacci encoded size: 5086628 bits
```

In the run these numbers come from, searching the compressed lists was between 400 and 1500 times slower than searching the plain ones, because every list has to be decoded before it can be searched. Timings change from run to run.

## Notes

- The encoded lists are Python strings of `'0'` and `'1'` characters, not packed bytes. Their size is counted in bits, while the text size is counted in characters, so the printed "compression ratio" is bits per text character. Divide it by 8 for a byte-for-byte ratio.
