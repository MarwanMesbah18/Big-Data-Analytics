"""Top-K Words with real parallel MapReduce, then keep the K most frequent.
Each file is mapped by its own thread, and the reducers also run in parallel threads."""
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor  # real OS threads (standard library)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "text-files")


def mapper(line):
    """Emit (word, 1) for every word in the line."""
    for word in re.findall(r"[a-z0-9]+", line.lower()):
        yield word, 1


def map_file(path):
    """Runs in a worker thread: apply the mapper to every line of one file."""
    print(f"[map]    thread {threading.current_thread().name} reads {os.path.basename(path)}", file=sys.stderr)
    pairs = []
    with open(path) as f:
        for line in f:
            pairs.extend(mapper(line))
    return pairs


def shuffle(pairs):
    """Group all values by key."""
    groups = {}
    for key, value in pairs:
        groups.setdefault(key, []).append(value)
    return groups


def reducer(item):
    """Runs in a worker thread: sum the counts of one word."""
    word, counts = item
    return word, sum(counts)


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 10  # K from command line, default 10

    files = [os.path.join(DATA_DIR, n) for n in sorted(os.listdir(DATA_DIR))
             if n.startswith("book_") and n.endswith(".txt")]

    with ThreadPoolExecutor(max_workers=len(files)) as pool:
        per_file_pairs = list(pool.map(map_file, files))            # map, in parallel
        all_pairs = [pair for pairs in per_file_pairs for pair in pairs]
        groups = shuffle(all_pairs)                           # shuffle
        counts = list(pool.map(reducer, sorted(groups.items())))    # reduce, in parallel

    # Sort by count (high first); ties are broken alphabetically
    counts.sort(key=lambda item: (-item[1], item[0]))
    for word, count in counts[:k]:
        print(f"{word} {count}")


if __name__ == "__main__":
    main()
