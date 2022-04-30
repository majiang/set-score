import glob
import os

import gb


def process(dir_in: str):
    for filename in glob.glob(
        os.path.join(
            dir_in, "gb", "pws", "*", "*.json"  # rule  # regulation  # year?  # date?
        )
    ):
        set_score = gb.read_json_validate(filename)
        result = gb.DayResult.from_set_score(set_score)
        yield filename, set_score, result
