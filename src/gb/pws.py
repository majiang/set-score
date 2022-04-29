import glob
import os

import gb


def process(dir_in: str):
    for filename in glob.glob(
        os.path.join(
            dir_in, "gb", "pws", "*", "*.json"  # rule  # regulation  # year?  # date?
        )
    ):
        yield filename, gb.read_json_validate(filename)
