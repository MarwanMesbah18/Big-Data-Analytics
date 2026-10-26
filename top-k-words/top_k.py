"""Top-K Words: word count with MapReduce, then keep the K most frequent."""
import os
import re
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "text-files")


def mapper(line):
    """Emit (word, 1) for every word in the line."""
    for word in re.findall(r"[a-z0-9]+", line.lower()):
        yield word, 1


def shuffle(pairs):
    """Group all values by key."""
    groups = {}
    for key, value in pairs:
        groups.setdefault(key, []).append(value)
    return groups


def reducer(word, counts):
    """Sum the counts of one word."""
    return word, sum(counts)


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 10  # K from command line, default 10

    pairs = []
    for name in sorted(os.listdir(DATA_DIR)):
        if name.startswith("book_") and name.endswith(".txt"):
            with open(os.path.join(DATA_DIR, name)) as f:
                for line in f:
                    pairs.extend(mapper(line))

    counts = [reducer(w, c) for w, c in shuffle(pairs).items()]

    # Sort by count (high first); ties are broken alphabetically
    counts.sort(key=lambda item: (-item[1], item[0]))
    for word, count in counts[:k]:
        print(f"{word} {count}")


if __name__ == "__main__":
    main()
