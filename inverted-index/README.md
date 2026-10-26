# Inverted Index

Run: `python3 inverted-index/inverted_index.py` (from the repo root)

- **Mapper:** emits `(word, file_name)` for every word.
- **Shuffle:** groups file names under each word.
- **Reducer:** removes duplicate file names and sorts them.
- Output: `word: book_01.txt, book_03.txt`
