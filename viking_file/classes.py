from dataclasses import dataclass


@dataclass(frozen=True)
class File:
    """
    A class representing file information.

    Attrs:

    - hash (str): File hash.
    - name (str): File name.
    - size (int): File size in bytes.
    - downloads (int | None): Number of downloads.
    - url (str): File URL.
    """

    hash: str
    name: str

    size: int
    downloads: int | None = 0

    @property
    def url(self) -> str:
        return f"https://vikingfile.com/f/{self.hash}"
