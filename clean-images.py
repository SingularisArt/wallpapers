#!/usr/bin/env python3

import argparse
from collections import defaultdict
import hashlib
import os

from PIL import Image


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
    hashobj = hash()
    file_object = open(filename, "rb")

    if first_chunk_only:
        hashobj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hashobj.update(chunk)
    hashed = hashobj.digest()

    file_object.close()
    return hashed


def check_for_duplicates(paths, hash=hashlib.sha1):
    hashes_by_size = defaultdict(list)
    hashes_on_1k = defaultdict(list)
    hashes_full = {}  # dict of full_file_hash: full_path_to_file_string

    for path in paths:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                try:
                    full_path = os.path.realpath(full_path)
                    file_size = os.path.getsize(full_path)
                    hashes_by_size[file_size].append(full_path)
                except (OSError,):
                    # not accessible (permissions, etc) - pass on
                    continue

    for size_in_bytes, files in hashes_by_size.items():
        if len(files) < 2:
            continue

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
                hashes_on_1k[(small_hash, size_in_bytes)].append(filename)
            except (OSError,):
                # the file access might've changed till the exec point got here
                continue

    for _, files_list in hashes_on_1k.items():
        if len(files_list) < 2:
            continue

        for filename in files_list:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
                duplicate = hashes_full.get(full_hash)
                if duplicate:
                    print(
                        "Duplicate found: {} and {}".format(
                            filename,
                            duplicate,
                        )
                    )
                else:
                    hashes_full[full_hash] = filename
            except (OSError,):
                # the file access might've changed till the exec point got here
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "type",
        help="What are you going to do?",
        choices=["check_for_duplicates", "check_for_non_4k_images"],
    )

    args = parser.parse_args()
    if args.type == "check_for_duplicates":
        check_for_duplicates(["."])
    else:
        for filename in os.listdir("./"):
            if ".jpg" in filename:
                filepath = filename

                with Image.open(filepath) as im:
                    x, y = im.size

                totalsize = x * y
                if not totalsize == 2073600:
                    print(f"Non 4k image found: {filepath}")
