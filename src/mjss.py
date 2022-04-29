import os
import pathlib

import gb


class Index:
    def __init__(self, filename: pathlib.Path):
        self.filename = filename
        self.pages = []

    def add(self, page: str):
        self.pages.append(page)

    def omit(self):
        open(self.filename, "w").write(
            f"""
            <!doctype html>
            <html lang=en>
            <head>
            <meta charset=utf-8>
            <title>index</title>
            </head>
            <body><ul>
            {"".join(
                f'<li><a href="{page}">{page}</a></li>'
                for page
                in self.pages)}
            </ul></body>
            </html>
        """
        )


def main(dir_in: str = "data", dir_out: str = "build"):
    index = Index(pathlib.Path(dir_out, "index.html"))
    for in_filename, result in gb.pws.process(dir_in):
        out_filename = pathlib.Path(in_filename).relative_to(dir_in).with_suffix(".txt")
        os.makedirs(pathlib.Path(dir_out).joinpath(out_filename).parent, exist_ok=True)
        with open(pathlib.Path(dir_out).joinpath(out_filename), "w") as f:
            f.write(str(result))
        index.add(out_filename)
    index.omit()
