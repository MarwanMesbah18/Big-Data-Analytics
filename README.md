# Big-Data-Analytics-

## Student Instructions

1. Fork this repository to your GitHub account.
2. Complete each programming task in its own folder in your fork, and push your work there.
3. Add your name and student ID to this README in your fork.

## Student Information

- **Name:** Marwan Omar Mesbah
- **Student ID:** 231004622

## Tasks

Each task is in its own folder, written in Python 3 (standard library only) and implements MapReduce (map -> shuffle -> reduce) with real parallel threads (`concurrent.futures.ThreadPoolExecutor`): one thread maps each file, and the reducers run in parallel threads. Each map thread prints its name to the terminal.

| Folder | Task | Run |
|---|---|---|
| `word-count/` | Count each word | `python3 word-count/word_count.py` |
| `top-k-words/` | K most frequent words | `python3 top-k-words/top_k.py 10` |
| `inverted-index/` | Word -> files containing it | `python3 inverted-index/inverted_index.py` |

## Optional GUI

`python3 gui.py` opens a page in your browser (http://localhost:8000): choose a task, press **Run**, and the output appears in the box (for Top-K, type K first). Stop it with Ctrl+C.
