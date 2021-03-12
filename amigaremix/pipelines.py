import os
from pathlib import Path
from shutil import move
from tempfile import NamedTemporaryFile

import scrapy

from amigaremix.items import *


def validatechars(s: str) -> str:
    """
    Filesystem friendly
    :param s:
    :return:
    """

    s = s.replace(r"\\", "_")
    s = s.replace(r"/", "_")
    s = s.replace(r"?", "_")
    return s


class AmigaremixPipeline:
    def process_item(self, item: Item, spider: scrapy.Spider):
        if not isinstance(item, Item):
            spider.log("Invalid item type")
            return

        filename = None
        basepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'items'))

        if isinstance(item, Tune):
            if item.data is None:
                spider.logger.info(f"Data is none")
                return

            if len(item.data) == 0:
                spider.logger.info(f"No data")
                return

            nitem: Tune = item
            # Remove filesystem unfriendly characters
            nitem.arranger = validatechars(nitem.arranger)
            nitem.title = validatechars(nitem.title)
            nitem.composer = validatechars(nitem.composer)

            filename = f"{nitem.arranger} - {nitem.title} [{nitem.composer}] {nitem.added.strftime('%Y-%m-%d')}.mp3"

        if filename is None:
            raise ValueError("No filename")

        if not os.path.isdir(basepath):
            Path(basepath).mkdir(parents=True, exist_ok=True)

        # Save to temporary file
        tmpf = NamedTemporaryFile("wb", prefix="amigaremix-", suffix=f".mp3", delete=False)
        with tmpf as f:
            f.write(item.data)
            f.flush()
            spider.logger.info(f"saved as {f.name}")

        # Rename and move the temporary file to actual file
        newpath = move(tmpf.name, os.path.join(basepath, filename))
        spider.logger.info(f"renamed {tmpf.name} to {newpath}")
