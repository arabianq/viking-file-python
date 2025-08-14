import asyncio
import atexit
import json
import os
from pathlib import Path
from warnings import deprecated

from itertools import chain
import aiofiles
from aiohttp import ClientSession, ClientResponse
from aiohttp.client_exceptions import ContentTypeError

from viking_file import api
from viking_file.classes import File
from viking_file.exceptions import ApiException


class AsyncVikingClient:
    """
    A class representing an asynchronous client for interacting with ViKiNG FiLE.

    Attrs:

    - hash (str): Account hash (empty string for anonymous usage).
    - timeout (int): API requests timeout in seconds. Defaults to 10.
    - _session (aiohttp.ClientSession): ClientSession to use. Defaults to None.
    """

    hash: str = ""
    timeout: int = 10
    _session: ClientSession = None

    def __init__(self, user_hash: str = "", api_timeout: int = 10, _session: ClientSession = None):
        self.hash = user_hash
        self.timeout = api_timeout
        self._close_session = _session is None
        self._session = _session or ClientSession()

        atexit.register(self._cleanup)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self._close_session:
            await self._session.close()

    async def close(self):
        """
        Closes the client _session.

        This method is a coroutine and should be used with the `await` keyword.

        This method is idempotent and can be called multiple times without issue.
        """
        if not self._session.closed:
            await self._session.close()

    def _cleanup(self):
        """
        Cleans up the client _session when exiting.

        This method is registered as an atexit handler and will be called
        when the program exits. It closes the client _session if it was
        created automatically by the client.
        """
        if self._close_session and not self._session.closed:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._session.close())

    @staticmethod
    def _get_file_hash(file: File | str) -> str:
        """
        Gets the hash of a file.

        If the argument is a File object, returns its hash attribute. Otherwise,
        it is assumed to be a string and is returned as is.

        Args:
            file (File | str): A File object or the hash of a file.

        Returns:
            str: The hash of a file.

        """
        if isinstance(file, File):
            file_hash = file.hash
        else:
            file_hash = file
        return file_hash

    @staticmethod
    async def _get_response_json(response: ClientResponse) -> dict:
        """
        Gets the JSON content of a response.

        This method assumes that the response is OK and either has a JSON
        content type or has a text content type with a JSON payload. If
        the response is not OK, it raises the exception set on the response.

        Args:
            response (ClientResponse): The response to get the JSON content of.

        Returns:
            dict: The JSON content of the response.

        Raises:
            aiohttp.ClientResponseError: If the response is not OK.
        """
        response.raise_for_status()
        try:
            return await response.json()
        except ContentTypeError:
            return json.loads((await response.text()).strip())

    async def _get_upload_server(self) -> str:
        """
        Retrieve the URL of the upload server.

        This method sends a request to obtain the upload server URL using
        the configured client session and timeout. It returns the server
        URL if successful, otherwise raises an ApiException with the error
        message from the response.

        Returns:
            str: The URL of the upload server.

        Raises:
            ApiException: If the server URL is not returned in the response.
        """
        api_response = await api.get_upload_server(
            session=self._session,
            timeout=self.timeout
        )
        api_response_json = await self._get_response_json(api_response)

        if server := api_response_json.get("server"):
            return server
        else:
            raise ApiException(await api_response.text())

    async def get_max_pages(self, path: str = "") -> int:
        """
        Retrieve the maximum number of pages in the user's file list.

        This method sends a request to obtain the maximum number of pages
        using the configured client session and timeout. It returns the
        number of pages if successful, otherwise raises an ApiException
        with the error message from the response.

        Args:
            path (str, optional): Directory path, example: Folder/My sub folder.
                Defaults to "".

        Returns:
            int: The maximum number of pages in the user's file list.

        Raises:
            ApiException: If the number of pages is not returned in the response.
        """
        api_response = await api.list_files(
            user=self.hash,
            page=1,
            path=path,
            session=self._session,
            timeout=self.timeout
        )
        api_response_json = await self._get_response_json(api_response)

        max_pages = api_response_json.get("maxPages")
        if isinstance(max_pages, int):
            return max_pages
        else:
            raise ApiException(await api_response.text())

    async def list_files(self, page: int, path: str = "") -> list[File]:
        """
        Retrieve the list of files from the user's file list.

        This method sends a request to obtain the list of files from the
        user's file list using the configured client session and timeout.
        It returns the list of files if successful, otherwise raises an
        ApiException with the error message from the response.

        Args:
            page (int): Page number to retrieve.
            path (str, optional): Directory path, example: Folder/My sub folder.
                Defaults to "".

        Returns:
            list[File]: The list of files in the user's file list.

        Raises:
            ApiException: If the list of files is not returned in the response.
        """
        api_response = await api.list_files(
            user=self.hash,
            page=page,
            path=path,
            session=self._session,
            timeout=self.timeout
        )
        api_response_json = await self._get_response_json(api_response)

        raw_files = api_response_json.get("files", [])
        files = []
        for raw_file in raw_files:
            file = File(
                hash=raw_file.get("hash"),
                name=raw_file.get("name"),
                size=raw_file.get("size"),
                downloads=raw_file.get("downloads")
            )
            files.append(file)

        return files

    async def list_all_files(self, path: str = "") -> list[File]:
        """
        Retrieve all files from the user's file list.

        This method sends multiple requests to obtain the list of files from
        the user's file list using the configured client session and timeout.
        It returns the list of all files if successful, otherwise raises an
        ApiException with the error message from the response.

        Args:
            path (str, optional): Directory path, example: Folder/My sub folder.
                Defaults to "".

        Returns:
            list[File]: The list of all files in the user's file list.

        Raises:
            ApiException: If the list of files is not returned in the response.
        """
        max_pages = await self.get_max_pages(path)

        tasks = []
        for page in range(1, max_pages + 1):
            tasks.append(asyncio.create_task(self.list_files(page, path)))

        files = await asyncio.gather(*tasks)
        files = list(chain.from_iterable(files))

        return files

    async def get_file(self, file: File | str) -> File:
        """
        Retrieve the file information by hash.

        This method sends a request to obtain the file information by hash
        using the configured client session and timeout. It returns the
        file information if successful, otherwise raises an ApiException
        with the error message from the response.

        Args:
            file (File | str): The file hash or a File object.

        Returns:
            File: The file information.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        file_hash = self._get_file_hash(file)

        api_response = await api.check_file(
            file_hash=file_hash,
            session=self._session,
            timeout=self.timeout
        )
        api_response_json = (await self._get_response_json(api_response))[0]
        if api_response_json["exist"]:
            return File(
                hash=api_response_json.get("hash"),
                name=api_response_json.get("name"),
                size=api_response_json.get("size"),
                downloads=api_response_json.get("downloads")
            )
        else:
            raise FileNotFoundError(f"File {file_hash} does not exist")

    async def rename_file(self, file: File | str, new_filename: str):
        """
        Rename a file.

        This method sends a request to rename a file using the configured
        client session and timeout. It raises an ApiException if the
        rename operation fails.

        Args:
            file (File | str): The file hash or a File object.
            new_filename (str): The new filename.

        Raises:
            ApiException: If the rename operation fails.
        """
        file_hash = self._get_file_hash(file)

        api_response = await api.rename_file(
            file_hash=file_hash,
            user=self.hash,
            filename=new_filename,
            session=self._session,
            timeout=self.timeout
        )
        api_response_json = await self._get_response_json(api_response)

        if (msg := api_response_json["error"]) == "success":
            return
        else:
            raise ApiException(msg)

    async def delete_file(self, file: File | str):
        """
        Delete a file.

        This method sends a request to delete a file using the configured
        client session and timeout. It raises an ApiException if the
        delete operation fails.

        Args:
            file (File | str): The file hash or a File object.

        Raises:
            ApiException: If the delete operation fails.
        """
        file_hash = self._get_file_hash(file)

        api_response = await api.delete_file(
            file_hash=file_hash,
            user=self.hash,
            session=self._session,
            timeout=self.timeout
        )
        api_response_json = await self._get_response_json(api_response)

        if (msg := api_response_json["error"]) == "success":
            return
        else:
            raise ApiException(msg)

    async def upload_remote_file(self, url: str, filename: str = "", path: str = ""):
        """
        Upload a remote file to the server.

        This method sends a request to upload a remote file using the
        configured client session and timeout. It returns the uploaded
        file information if successful, otherwise raises an ApiException
        with the error message from the response.

        Args:
            url (str): URL of the remote file to upload.
            filename (str, optional): New filename. Defaults to "".
            path (str, optional): File path, example: Folder/My sub folder.
                Defaults to "".

        Returns:
            File: The uploaded file information.

        Raises:
            ApiException: If the upload operation fails.
        """
        upload_server_url = await self._get_upload_server()

        api_response = await api.upload_remote_file(
            upload_server=upload_server_url,
            link=url,
            user=self.hash,
            filename=filename,
            path=path,
            session=self._session,
            timeout=self.timeout
        )
        api_response.raise_for_status()

        async for line in api_response.content:
            line = line.strip()
            line_json = json.loads(line)

            if line_json.get("progress"):
                continue

            return File(
                hash=line_json.get("hash"),
                name=line_json.get("name"),
                size=line_json.get("size"),
                downloads=0
            )

        raise ApiException(await api_response.text())

    @deprecated("Use upload_file instead", category=None)
    async def upload_file_legacy(self, filepath: Path | str, path: str = ""):
        """
        THIS METHOD IS DEPRECATED, USE upload_file INSTEAD

        Upload a file to the server.

        This method sends a request to upload a file using the configured client
        session and timeout. It returns the uploaded file information if
        successful, otherwise raises an ApiException with the error message from
        the response.

        Args:
            filepath (Path | str): The local file path to be uploaded.
            path (str, optional): Directory path, example: Folder/My sub folder.
                Defaults to "".

        Returns:
            File: The uploaded file information.

        Raises:
            ApiException: If the upload operation fails.
        """
        upload_server_url = await self._get_upload_server()

        api_response = await api.upload_file_legacy(upload_url=upload_server_url, filepath=filepath, user=self.hash,
                                                    path=path, session=self._session, timeout=self.timeout)
        api_response_json = await self._get_response_json(api_response)

        return File(
            hash=api_response_json.get("hash"),
            name=api_response_json.get("name"),
            size=api_response_json.get("size"),
            downloads=0
        )

    async def upload_file(self, filepath: Path | str, filename: str = "", path: str = ""):
        """
        Upload a file to the server.

        This method sends a request to upload a file using the configured client
        session and timeout. It returns the uploaded file information if
        successful, otherwise raises an ApiException with the error message from
        the response.

        Args:
            filepath (Path | str): The local file path to be uploaded.
            filename (str, optional): New filename. Defaults to "".
            path (str, optional): Directory path, example: Folder/My sub folder.
                Defaults to "".

        Returns:
            File: The uploaded file information.

        Raises:
            ApiException: If the upload operation fails.
        """
        filepath = Path(filepath).resolve()
        filename = filename or filepath.name
        filesize = os.path.getsize(filepath)

        upload_url_response = await api.get_upload_url(
            size=filesize,
            session=self._session,
            timeout=self.timeout
        )
        upload_url_response_json = await self._get_response_json(upload_url_response)

        upload_id: str = upload_url_response_json.get("uploadId")
        key: str = upload_url_response_json.get("key")
        part_size: int = upload_url_response_json.get("partSize")
        number_of_parts: int = upload_url_response_json.get("numberParts")
        urls: list[str] = upload_url_response_json.get("urls")

        async def file_reader(offset: int):
            nonlocal filepath
            nonlocal part_size

            async with aiofiles.open(filepath, "rb") as f:
                await f.seek(offset)

                part_sent = 0

                while part_sent < part_size:
                    remained = part_size - part_sent
                    chunk_size = min(4096 * 1024, remained)
                    data = await f.read(chunk_size)

                    if not data:
                        break

                    part_sent += len(data)

                    yield data

        async def upload_part(part_number: int):
            nonlocal filesize
            nonlocal part_size
            nonlocal urls

            upload_url = urls[part_number]
            file_offset = part_size * part_number
            current_part_size = min(part_size, filesize - file_offset)

            headers = {
                "Content-Length": str(current_part_size)
            }

            async with self._session.put(url=upload_url, data=file_reader(file_offset), headers=headers) as response:
                response.raise_for_status()
                etag = response.headers.get("ETag").strip("\"")

            return {"PartNumber": part_number + 1, "ETag": etag}

        tasks = []
        for i in range(number_of_parts):
            tasks.append(asyncio.create_task(upload_part(i)))
        parts = await asyncio.gather(*tasks)

        complete_upload_response = await api.complete_upload(
            key=key,
            upload_id=upload_id,
            parts=parts,
            filename=filename,
            user=self.hash,
            path=path,
            session=self._session,
            timeout=self.timeout
        )
        complete_upload_json = await self._get_response_json(complete_upload_response)

        if error := complete_upload_json.get("error"):
            raise ApiException(error)

        return File(
            hash=complete_upload_json.get("hash"),
            name=complete_upload_json.get("name"),
            size=complete_upload_json.get("size"),
        )
