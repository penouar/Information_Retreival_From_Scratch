# tfidf_search

TF-IDF weighting, query ranking and document-to-document cosine similarity, written without any machine learning library.

## What it does

`tfidf_search.py` loads every `.txt` file in `corpus/`, lowercases the text, splits it into alphanumeric tokens and removes a short list of stopwords. Then it computes:

- **tf:** term count divided by the number of terms in the document
- **idf:** `ln(N / df)`, where `N` is the number of documents and `df` the number of documents containing the term
- **tf-idf:** `tf * idf`

It ranks all documents for a query (`artificial intelligence machine learning` by default) by summing the tf-idf weights of the query terms. It also finds the most similar pair of documents by cosine similarity, once with tf-idf vectors and once with plain tf vectors, to show what the idf weighting changes.

The printout includes the number of documents, the first terms of each document, tf, idf and tf-idf examples from the first document, the ranked list for the query, and the two most similar pairs.

## Run

Build the `corpus/` folder first with `corpus_builder`, then, from the repository root:

```
python tfidf_search/tfidf_search.py
```

To try another query, edit the `query` variable near the bottom of the script. Standard library only.

## Notes

- The all-pairs similarity step compares every pair of documents, so it is the slow part (around 20 seconds for 528 documents).
- A term that appears in every document gets an idf of 0 and no longer contributes to the score.
