# Top-K Words

Run: `python3 top-k-words/top_k.py 10` (K is optional, default 10)

Parallel: each file is mapped in its own thread (`ThreadPoolExecutor`), reducers also run in parallel threads.
The terminal shows which thread read which file.

- Same map/shuffle/reduce as Word Count.
- Extra step: sort the reduced results by count (highest first, ties alphabetical) and keep the first K.
