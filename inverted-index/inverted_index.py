"""Inverted Index with real parallel MapReduce: word -> files that contain it.
Each file is mapped by its own thread, and the reducers also run in parallel threads."""
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor  # real OS threads (standard library)

# Folder with the book_*.txt files. Set the DATA_DIR environment variable to use your own folder.
DATA_DIR = os.environ.get("DATA_DIR") or os.path.join(os.path.dirname(__file__), "..", "datasets", "text-files")


def mapper(file_name, line):
    """Emit (word, file_name) for every word in the line."""
    for word in re.findall(r"[a-z0-9]+", line.lower()):
        yield word, file_name


def map_file(path):
    """Runs in a worker thread: apply the mapper to every line of one file."""
    file_name = os.path.basename(path)
    print(f"[map]    thread {threading.current_thread().name} reads {file_name}", file=sys.stderr)
    pairs = []
    with open(path) as f:
        for line in f:
            pairs.extend(mapper(file_name, line))
    return pairs


def shuffle(pairs):
    """Group all file names by word."""
    groups = {}
    for key, value in pairs:
        groups.setdefault(key, []).append(value)
    return groups


def reducer(item):
    """Runs in a worker thread: keep each file only once and sort the list."""
    word, files = item
    return word, sorted(set(files))


def main():
    files = [os.path.join(DATA_DIR, n) for n in sorted(os.listdir(DATA_DIR))
             if n.startswith("book_") and n.endswith(".txt")]

    with ThreadPoolExecutor(max_workers=len(files)) as pool:
        per_file_pairs = list(pool.map(map_file, files))            # map, in parallel
        all_pairs = [pair for pairs in per_file_pairs for pair in pairs]
        groups = shuffle(all_pairs)                           # shuffle
        results = list(pool.map(reducer, sorted(groups.items())))   # reduce, in parallel

    for word, file_list in results:
        print(f"{word}: {', '.join(file_list)}")


if __name__ == "__main__":
    main()
