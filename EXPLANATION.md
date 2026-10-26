# Project Explanation (for revision)

## 1. What is the project?

The assignment is to practice **MapReduce**, a way to process big data by splitting the work into steps that can run in parallel:

1. **Map**: many workers each read a piece of the data and turn it into `(key, value)` pairs.
2. **Shuffle**: all pairs with the same key are grouped together.
3. **Reduce**: many workers each combine one group into a result.

I implemented three tasks in plain Python (standard library only, no installs). Map and reduce run in **real parallel threads**.

## 2. Folder structure

```
Big-Data-Analytics/
├── README.md                      name, student ID, task table, how to run
├── EXPLANATION.md                 this file
├── gui.py                         optional browser GUI (runs the 3 scripts)
├── datasets/text-files/           input data (given by the instructor)
│   ├── book_01.txt ... book_05.txt    5 files x 5 sentences
│   ├── expected_word_count.txt        instructor answer key (has errors, see section 8)
│   └── README.md                      instructor's description of the dataset
├── word-count/
│   ├── word_count.py              Task 1
│   └── README.md
├── top-k-words/
│   ├── top_k.py                   Task 2
│   └── README.md
└── inverted-index/
    ├── inverted_index.py          Task 3
    └── README.md
```

## 3. How to run

From the repo root:

| Command | What it shows |
|---|---|
| `python3 word-count/word_count.py` | every word and how many times it appears |
| `python3 top-k-words/top_k.py 5` | the 5 most frequent words (K is optional, default 10) |
| `python3 inverted-index/inverted_index.py` | every word and the files that contain it |
| `python3 gui.py` | browser page at http://localhost:8000 with a dropdown, a K box and a Run button (Ctrl+C to stop) |

The three scripts print their result to the terminal (stdout) and print which thread read which file as `[map] thread ... reads book_0X.txt` (stderr).

## 4. Task 1: `word-count/word_count.py`

**Purpose:** count how many times each word appears across all 5 files.

### Imports
```python
import os, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
```
- `os`: build file paths and list the folder.
- `re`: regular expressions, used to split lines into words.
- `sys`: write the thread messages to stderr.
- `threading`: get the name of the current thread, to show which thread works on which file.
- `ThreadPoolExecutor`: a pool of real operating-system threads from the standard library.

### `DATA_DIR`
```python
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "text-files")
```
The path to the data, built relative to the script, so it works from any folder.

### `mapper(line)`: the MAP logic
```python
for word in re.findall(r"[a-z0-9]+", line.lower()):
    yield word, 1
```
- `line.lower()` makes `Big` and `big` the same word.
- `re.findall(r"[a-z0-9]+", ...)` returns only runs of letters and digits, so punctuation disappears.
- `yield word, 1` emits one pair per word, e.g. `("big", 1)`. Every occurrence is counted as 1.

### `map_file(path)`: one map task, runs in a worker thread
- Prints the thread name and file name (to stderr).
- Opens the file, sends each line to `mapper`, collects all pairs in a list and returns it.
- One call handles one whole file, so 5 files means 5 map tasks that can run at the same time.

### `shuffle(pairs)`: the SHUFFLE step
```python
groups.setdefault(key, []).append(value)
```
Builds a dictionary: word -> list of its values. Example: `("big",1) ("data",1) ("big",1)` becomes `{"big": [1,1], "data": [1]}`. `setdefault` creates the empty list the first time a key is seen.

### `reducer(item)`: the REDUCE logic, runs in a worker thread
```python
word, counts = item
return word, sum(counts)
```
Takes one group such as `("big", [1,1])` and returns `("big", 2)`.

### `main()`: connects everything
1. Builds the list of files (names starting `book_` and ending `.txt`, sorted).
2. `with ThreadPoolExecutor(max_workers=len(files)) as pool:` creates up to one thread per file. The `with` block closes the pool when done.
3. **Map phase:** `pool.map(map_file, files)` runs `map_file` for each file in parallel. `list(...)` waits for all of them.
4. Flattens the per-file lists into one big list of pairs.
5. **Shuffle phase:** `shuffle(...)` runs in the main thread, because it needs all mapper output before it can group.
6. **Reduce phase:** `pool.map(reducer, sorted(groups.items()))` runs the reducers in parallel.
7. Prints `word count` per line (sorted alphabetically).

### `if __name__ == "__main__": main()`
Runs `main()` only when the file is run directly, not when it is imported.

## 5. Task 2: `top-k-words/top_k.py`

**Purpose:** show only the K most frequent words.

It is identical to Word Count (same `mapper`, `map_file`, `shuffle`, `reducer`) with two differences in `main()`:

1. **Reading K:** `k = int(sys.argv[1]) if len(sys.argv) > 1 else 10`. `sys.argv[1]` is the first command-line argument (`python3 top_k.py 5` gives K = 5). Without it, K defaults to 10.
2. **Sorting and cutting:**
   ```python
   counts.sort(key=lambda item: (-item[1], item[0]))
   for word, count in counts[:k]: ...
   ```
   Sort key is `(-count, word)`: highest count first (the minus flips the order), and ties are broken alphabetically so the output is always the same. `counts[:k]` keeps the first K.

**What "K (Top-K only)" in the GUI means:** K is the number of words to show. Only this task uses it. Word Count and Inverted Index ignore it.

## 6. Task 3: `inverted-index/inverted_index.py`

**Purpose:** for each word, list the files that contain it (like the index at the back of a book).

Differences from Word Count:

- **`mapper(file_name, line)`** emits `(word, file_name)` instead of `(word, 1)`. It also receives the file name.
- **`map_file`** takes `os.path.basename(path)` (e.g. `book_02.txt`) and passes it to the mapper.
- **`shuffle`** groups file names by word: `{"students": ["book_01.txt", "book_01.txt", "book_03.txt"]}`.
- **`reducer`** does `sorted(set(files))`. `set` removes duplicates (a word can appear many times in one file), and `sorted` makes the list ordered.
- Output format: `students: book_01.txt, book_03.txt, book_04.txt`.

## 7. The GUI: `gui.py`

**Purpose:** optional. A page where you pick a task and click Run, instead of typing commands. It does **no** MapReduce itself: it runs the same three scripts and shows what they print.

- **`TASKS`**: dictionary mapping the dropdown name to the script path.
- **`PAGE`**: the HTML page (dropdown, K box, Run button, output box). A small JavaScript function `run()` calls the address `/run?task=...&k=...` and puts the reply in the output box.
- **`Handler`**: the web server logic (`do_GET`):
  - If the address is `/run`, it builds the command `[python, script]` (adding K for Top-K), runs it with `subprocess.run(..., capture_output=True, text=True)`, and sends back `stdout` plus the thread lines from `stderr`.
  - Otherwise it sends the page.
  - `log_message` is overridden to an empty function to keep the terminal quiet.
- **Last lines:** print the address, `webbrowser.open(...)` opens your browser, and `HTTPServer(...).serve_forever()` keeps the server running until Ctrl+C.

Why a browser and not a desktop window? The Tkinter version rendered blank on this Mac because macOS's built-in Tk 8.5 does not draw most widgets, so the web version was used. It needs no installs.

### Custom data
- Each task script reads its folder from `DATA_DIR = os.environ.get("DATA_DIR") or <sample folder>`. If the environment variable `DATA_DIR` is set, the script uses that folder, otherwise the sample files.
- In the GUI, text pasted in the "Custom data" box is split on lines containing `---`. `run_script` writes each part to `book_1.txt`, `book_2.txt`, ... in a temporary folder, sets `DATA_DIR` to it for that one run, and the folder is deleted afterwards.
- Terminal use: `DATA_DIR=/path/to/folder python3 word-count/word_count.py` (files must be named `book_*.txt`).
- The Run button sends a POST request (the text can be long), so the server has `do_POST`; `do_GET` only serves the page.
- Enter runs the task; inside the text box Enter makes a new line and Ctrl+Enter runs.

## 8. The dataset and the answer-key problem

- The 5 books contain **235 words** (`cat book_0*.txt | wc -w`).
- `expected_word_count.txt` totals only **227** and has wrong counts, e.g. `an 2` (really 1), `this 4` (really 2), `to 4` (really 1).
- My output was compared with an independent shell count (`tr | sort | uniq -c`) and matches it exactly, so the instructor's file is the one that is wrong. This is also noted in `word-count/README.md`.

## 9. Threads vs processes (likely question)

- The map and reduce steps run in **real OS threads** (`ThreadPoolExecutor`).
- Python's **GIL** lets only one thread run Python code at a time, so threads overlap but give no speedup on CPU-bound work, and this data is tiny anyway.
- For true multi-core parallelism, swap `ThreadPoolExecutor` for `ProcessPoolExecutor` (same structure, separate processes).
- **Shuffle is not parallel** on purpose: it must see all map output before grouping.
- In a real cluster (Hadoop/Spark), mappers and reducers run on different machines. This project shows the same idea on one machine.

## 10. Quick revision questions

1. What are the three phases of MapReduce and what does each do?
2. What does the mapper emit in Word Count? In Inverted Index?
3. Why do we lowercase and strip punctuation?
4. What does `shuffle` return and why is it needed?
5. Why does Top-K sort by `(-count, word)`?
6. Why is shuffle done in one thread?
7. What is the GIL and how does it affect this project?
8. Why does the output differ from `expected_word_count.txt`?
