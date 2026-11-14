# information-retrieval-from-scratch

A small text search stack written in plain Python, with no libraries: building a document collection, a Boolean search engine, TF-IDF ranking, index compression and classic string matching. Everything is implemented by hand so the mechanics are visible.

## Projects

| Folder | What it covers |
|---|---|
| [`corpus_builder`](corpus_builder) | Splits one large text file into small documents |
| [`boolean_search`](boolean_search) | Inverted index, AND / OR / NOT queries with parentheses, and a ranked Boolean variant |
| [`tfidf_search`](tfidf_search) | TF-IDF weights, query ranking and cosine similarity between documents |
| [`index_compression`](index_compression) | Unary, Elias gamma and Fibonacci coding of posting lists: space saved against search speed |
| [`string_matching`](string_matching) | Brute force, KMP and Boyer-Moore-Horspool compared by number of comparisons |

Each folder has its own README with details and sample output.

## Quick start

Python 3, standard library only. Run everything from the repository root: the scripts look for `big_text.txt` and `corpus/` in the current directory.

```
python corpus_builder/corpus_builder.py
python boolean_search/boolean_search.py
python tfidf_search/tfidf_search.py
python index_compression/index_compression.py
python string_matching/string_matching.py
```

The first command creates the `corpus/` folder (528 documents) used by the next two. The last two need no input files.

## Layout

```
.
├── big_text.txt
├── corpus_builder/
├── boolean_search/
├── tfidf_search/
├── index_compression/
└── string_matching/
```

## Data

`big_text.txt` is text copied from Wikipedia articles. Wikipedia text is available under CC BY-SA 4.0, so keep the attribution if you reuse it.
