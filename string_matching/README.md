# string_matching

Brute force, Knuth-Morris-Pratt (KMP) and Boyer-Moore-Horspool (BMH) pattern matching, compared by the number of character comparisons each one makes.

## What it does

`string_matching.py` implements the three algorithms. Each returns the match positions and the number of character comparisons it made while scanning the text (building the KMP prefix table and the BMH shift table is not counted).

The comparison is run on three texts:

- a short sentence
- the same sentence repeated 15 times
- a random 1000-letter DNA string (A, C, G, T), generated again on every run

with the patterns `SIMPLE`, `MATCH` and `SCIENCE`.

## Run

From the repository root:

```
python string_matching/string_matching.py
```

Standard library only.

## Sample output

```
=== SHORT TEXT ===
Pattern   Brute     KMP       BMH       
----------------------------------------
SIMPLE    76        74        25        
MATCH     73        73        21        
SCIENCE   74        74        20        

=== LONG TEXT ===
Pattern   Brute     KMP       BMH       
----------------------------------------
SIMPLE    1210      1110      375       
MATCH     1151      1095      343       
SCIENCE   1194      1110      300       
```

The DNA table changes from run to run because the text is random. Horspool makes far fewer comparisons than the other two on every text because it skips ahead by the pattern length whenever the last character of the window does not occur in the pattern.
