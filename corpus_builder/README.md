# corpus_builder

Splits one large text file into many small documents, so there is something to index and search.

`corpus_builder.py` reads `big_text.txt`, collapses all whitespace, splits the text into sentences (after `.`, `!` or `?`) and writes every 33 sentences to a separate file in a `corpus/` folder: `doc0.txt`, `doc1.txt`, and so on. A last group with fewer than 33 sentences is dropped. The script prints how many documents it created.

## Run

From the repository root, where `big_text.txt` lives and where `corpus/` will be created:

```
python corpus_builder/corpus_builder.py
```

With the included `big_text.txt` this creates 528 documents. Change `doc_size` at the top of the script to get longer or shorter documents.

Standard library only.

## Used by

The `corpus/` folder is the input for the `boolean_search` and `tfidf_search` projects.

## Data

`big_text.txt` (in the repository root) is text copied from Wikipedia articles (the Artificial intelligence article among others). Wikipedia text is available under CC BY-SA 4.0, so keep the attribution if you redistribute it.
