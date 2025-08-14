import asyncio
from pathlib import Path
from warnings import deprecated

from aiohttp import ClientSession

from viking_file.classes import File
from viking_file.clients.client_async import AsyncVikingClient


class VikingClient(AsyncVikingClient):
    def __init__(self, user_hash: str = "", api_timeout: int = 10):
        self._loop = asyncio.new_event_loop()
        session = ClientSession(loop=self._loop)
        super().__init__(user_hash, api_timeout, session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if not self._session.closed:
            self._loop.run_until_complete(self._session.close())
            self._loop.close()

    def _cleanup(self):
        if not self._session.closed:
            self._loop.run_until_complete(self._session.close())
        self._loop.close()

    def get_max_pages(self, path: str = "") -> int:
        return self._loop.run_until_complete(super().get_max_pages(path))

    def list_files(self, page: int, path: str = "") -> list[File]:
        return self._loop.run_until_complete(super().list_files(page, path))

    def list_all_files(self, path: str = "") -> list[File]:
        max_pages = self.get_max_pages(path)

        files = []
        for page in range(1, max_pages + 1):
            files.extend(self.list_files(page, path))

        return files

    def get_file(self, file: File | str) -> File:
        return self._loop.run_until_complete(super().get_file(file))

    def rename_file(self, file: File | str, new_filename: str):
        return self._loop.run_until_complete(super().rename_file(file, new_filename))

    def delete_file(self, file: File | str):
        return self._loop.run_until_complete(super().delete_file(file))

    def upload_remote_file(self, url: str, filename: str = "", path: str = ""):
        return self._loop.run_until_complete(super().upload_remote_file(url, filename, path))

    @deprecated("Use upload_file instead", category=None)
    def upload_file_legacy(self, filepath: Path | str, path: str = ""):
        return self._loop.run_until_complete(super().upload_file_legacy(filepath, path))

    def upload_file(self, filepath: Path | str, filename: str = "", path: str = ""):
        return self._loop.run_until_complete(super().upload_file(filepath, filename, path))
