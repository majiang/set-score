import datetime
import hashlib
import os.path


class Index:
    def __init__(self, filename: str):
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
    dt = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    hs = hashlib.sha512(dt.encode(encoding="utf-8")).hexdigest()
    index = Index(os.path.join(dir_out, "index.html"))
    filename = f"{dt}.txt"
    with open(os.path.join(dir_out, filename), "w") as f:
        f.write(hs)
        index.add(filename)
    index.omit()
