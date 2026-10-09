"""Zip-based formats, such as EPUB books and Word files, read with care.

A stranger's zip can hold a small file that unpacks to gigabytes, or XML whose
entities read local files. An archive counts what it unpacks and stops at a
limit, and its XML parser resolves no entities, loads no DTD, and opens no
network. Nothing is ever unpacked to disk.
"""

import zipfile

from lxml import etree  # pyright: ignore[reportAttributeAccessIssue]

PARSER = etree.XMLParser(
    resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False
)


class Archive:
    """A zip that counts what it unpacks, and stops at its limit."""

    def __init__(self, archive: zipfile.ZipFile, limit: int, kind: str) -> None:
        self.archive, self.limit, self.left, self.kind = archive, limit, limit, kind

    def read(self, name: str) -> bytes:
        with self.archive.open(name) as member:
            data = member.read(self.left + 1)
        self.left -= len(data)
        if self.left < 0:
            raise ValueError(
                f"the {self.kind} unpacks to more than {self.limit // 2**20} MB"
            )
        return data

    def xml(self, name: str) -> etree._Element:
        return etree.fromstring(self.read(name), PARSER)
