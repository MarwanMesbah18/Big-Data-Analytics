"""Inverted Index: map each word to the list of files that contain it."""
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "text-files")


def mapper(file_name, line):
    """Emit (word, file_name) for every word in the line."""
    for word in re.findall(r"[a-z0-9]+", line.lower()):
        yield word, file_name


def shuffle(pairs):
    """Group all file names by word."""
    groups = {}
    for key, value in pairs:
        groups.setdefault(key, []).append(value)
    return groups


def reducer(word, files):
    """Keep each file only once (unique) and sort the list."""
    return word, sorted(set(files))


def main():
    pairs = []
    for name in sorted(os.listdir(DATA_DIR)):
        if name.startswith("book_") and name.endswith(".txt"):
            with open(os.path.join(DATA_DIR, name)) as f:
                for line in f:
                    pairs.extend(mapper(name, line))

    for word, files in sorted(shuffle(pairs).items()):
        word, unique_files = reducer(word, files)
        print(f"{word}: {', '.join(unique_files)}")


if __name__ == "__main__":
    main()
