"""Word Count with a simple MapReduce simulation (map -> shuffle -> reduce)."""
import os
import re
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "text-files")


def mapper(line):
    """Emit (word, 1) for every word in the line (lowercase, no punctuation)."""
    for word in re.findall(r"[a-z0-9]+", line.lower()):
        yield word, 1


def shuffle(pairs):
    """Group all values by key: {word: [1, 1, ...]}."""
    groups = {}
    for key, value in pairs:
        groups.setdefault(key, []).append(value)
    return groups


def reducer(word, counts):
    """Sum the counts of one word."""
    return word, sum(counts)


def main():
    # Map phase: read every book_*.txt file, line by line
    pairs = []
    for name in sorted(os.listdir(DATA_DIR)):
        if name.startswith("book_") and name.endswith(".txt"):
            with open(os.path.join(DATA_DIR, name)) as f:
                for line in f:
                    pairs.extend(mapper(line))

    # Shuffle phase, then Reduce phase (sorted by word)
    groups = shuffle(pairs)
    results = [reducer(word, counts) for word, counts in sorted(groups.items())]

    # Output "word count", one per line, same format as expected_word_count.txt
    out = "".join(f"{word} {count}\n" for word, count in results)
    sys.stdout.write(out)


if __name__ == "__main__":
    main()
