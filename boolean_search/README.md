# boolean_search

A small search engine over a folder of text documents: an inverted index, Boolean queries with AND, OR, NOT and parentheses, and a ranked variant of Boolean search.

## What it does

`boolean_search.py` loads every `.txt` file in `corpus/` (it needs at least 500 non-empty files, otherwise it raises an error), lowercases the text, splits it into alphanumeric tokens and removes stopwords.

- **Index:** term -> {document id: term frequency}. A compact version stores the document ids as gaps and keeps the frequencies in a parallel list.
- **Query parsing:** the query is tokenised, checked for balanced parentheses and valid operator placement, converted to postfix notation (shunting-yard) and evaluated with set operations. Operators are case-insensitive.
- **Standard Boolean model:** returns the set of matching documents.
- **Extended Boolean model:** ranks the matching documents with
  `0.8 * (average normalised tf of the query terms) + 0.2 * (share of query terms present) - 0.3 * (normalised tf of NOT terms)`,
  where tf is divided by the highest term frequency in the document.

On start it prints index statistics, runs the sample query `(data AND search) OR retrieval` with both models, and then opens an interactive prompt. Type `exit` to quit.

## Run

Build the `corpus/` folder first with `corpus_builder`, then, from the repository root:

```
python boolean_search/boolean_search.py
```

Standard library only.

## Sample output

With the 528-document corpus from `corpus_builder`:

```
INDEX STATISTICS
Number of unique tokens: 22753
Average posting list length: 4.46
Total number of entries: 101498
```

## Notes

- Document ids are positions in the sorted list of file names (`doc0.txt`, `doc1.txt`, `doc10.txt`, ...), so the id printed in the results is not the number in the file name.
- Query terms that are stopwords match nothing, since stopwords are not indexed.
