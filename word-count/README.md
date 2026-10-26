# Word Count

Run: `python3 word-count/word_count.py` (from the repo root)

Parallel: each file is mapped in its own thread (`ThreadPoolExecutor`), reducers also run in parallel threads.
The terminal shows which thread read which file.

- **Mapper:** lowercases each line, removes punctuation, emits `(word, 1)` per word.
- **Shuffle:** groups all the 1s under their word.
- **Reducer:** sums the 1s for each word.
- Output: `word count`, one per line, sorted alphabetically.

## Note on `expected_word_count.txt`
The provided file does not match the text files. It totals 227 words, but the books contain 235 (`cat book_0*.txt | wc -w`),
and it has errors, e.g. `an 2` (really 1), `this 4` (really 2), `to 4` (really 1).
My output was checked against an independent shell count (`tr | sort | uniq -c`) and matches it exactly.
