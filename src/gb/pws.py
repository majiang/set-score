import glob
import os

import gb


def process(dir_in: str):
    for filename in sorted(glob.glob(
        os.path.join(
            dir_in, "gb", "pws", "*", "*.json"  # rule  # regulation  # year?  # date?
        )
    )):
        input_score = gb.from_json_file(filename)
        validated_score = input_score.validate()
        result = gb.DayResult.from_set_score(validated_score)
        yield filename, validated_score, result
