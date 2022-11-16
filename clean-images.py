#!/usr/bin/env python3

import os
from PIL import Image

for filename in os.listdir("./"):
    if ".jpg" in filename:
        filepath = filename

        with Image.open(filepath) as im:
            x, y = im.size

        totalsize = x * y
        if not totalsize == 2073600:
            print(f"Removing {filepath}")
            os.remove(filepath)
