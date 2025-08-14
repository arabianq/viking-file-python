from pathlib import Path

from aiohttp import ClientSession, ClientResponse, FormData, ClientTimeout

BASE_URL = "https://vikingfile.com/api/"


async def get_upload_url(size: int, session: ClientSession = None, timeout: int = 10) -> ClientResponse:
    """
    Get the URL of the upload server.

    Args:
        size (int): Size of file to upload in byte.
        session (aiohttp.ClientSession, optional): Client _session to use. Defaults to None.
        timeout (int, optional): Timeout for the request. Defaults to 10.

    Returns:
        aiohttp.ClientResponse: The response from the server containing the upload server URL.
    """
    close_session = session is None
    session = session or ClientSession()

    request_data = {
        "size": size,
    }

    response = await session.post(
        url=BASE_URL + "get-upload-url",
        data=request_data,
        timeout=timeout
    )

    if close_session:
        await session.close()

    return response


async def complete_upload(key: str, upload_id: str, parts: list[dict], filename: str, user: str = "", path: str = "",
                          session: ClientSession = None, timeout: int = 10) -> ClientResponse:
    """
    Complete the upload process.

    Args:
        key (str): Key of the file to upload.
        upload_id (str): Upload ID of the file to upload.
        parts (list[dict]): List of parts with their respective ETags.
        filename (str): New filename.
        user (str, optional): User's hash. Empty for anonymous upload. Defaults to "".
        path (str, optional): File path, example: Folder/My sub folder. Defaults to "".
        session (aiohttp.ClientSession, optional): Client _session to use. Defaults to None.
        timeout (int, optional): Timeout for the request. Defaults to 10.

    Returns:
        aiohttp.ClientResponse: Server response.
    """
    close_session = session is None
    session = session or ClientSession()

    request_data = {
        "key": key,
        "uploadId": upload_id,
        "name": filename,
        "user": user,
        "path": path,
    }

    for idx, part in enumerate(parts):
        request_data[f"parts[{idx}][PartNumber]"] = str(part["PartNumber"])
        request_data[f"parts[{idx}][ETag]"] = part["ETag"]

    response = await session.post(
        url=BASE_URL + "complete-upload",
        data=request_data,
        timeout=timeout
    )

    if close_session:
        await session.close()

    return response


async def get_upload_server(session: ClientSession = None, timeout: int = 10) -> ClientResponse:
    """
    Retrieve the upload server URL.

    Args:
        session (aiohttp.ClientSession, optional): Client _session to use. Defaults to None.
        timeout (int, optional): Timeout for the request. Defaults to 10.

    Returns:
        aiohttp.ClientResponse: The response from the server containing the upload server URL.
    """

    close_session = session is None
    session = session or ClientSession()

    response = await session.get(
        url=BASE_URL + "get-server",
        timeout=timeout
    )

    if close_session:
        await session.close()

    return response


async def upload_file_legacy(upload_url: str, filepath: str, user: str = "", path: str = "",
                             session: ClientSession = None,
                             timeout: int = 10) -> ClientResponse:
    """
    Upload a file to a server using the legacy method.

    Args:
        upload_url (str): URL of the upload server.
        filepath (str): The local file path to be uploaded.
        user (str, optional): User's hash. Empty for anonymous upload. Defaults to "".
        path (str, optional): File path on the server, example: Folder/My sub folder. Defaults to "".
        session (aiohttp.ClientSession, optional): Client _session to use. Defaults to None.
        timeout (int, optional): Timeout for the request in seconds. Defaults to 10.

    Returns:
        aiohttp.ClientResponse: Server response.
    """

    filepath = Path(filepath).resolve()
    assert filepath.exists(), f"File {filepath} doesn't exist!"

    close_session = session is None
    session = session or ClientSession()

    data = FormData()
    data.add_field("user", user)
    data.add_field("path", path)
    data.add_field("file", open(filepath, "rb"), filename=filepath.name)

    response = await session.post(
        url=upload_url,
        data=data,
        timeout=ClientTimeout(connect=timeout, sock_read=None, sock_connect=None)
    )

    if close_session:
        await session.close()

    return response


async def upload_remote_file(upload_server: str, link: str, user: str = "", filename: str = "", path: str = "",
                             session: ClientSession = None, timeout: int = 10) -> ClientResponse:
    """
    Upload a remote file to a server.

    Args:
        upload_server (str): URL of the upload server.
        link (str): URL of the file to upload.
        user (str, optional): User's hash. Empty for anonymous upload. Defaults to "".
        filename (str, optional): New filename. Defaults to "".
        path (str, optional): File path, example: Folder/My sub folder. Defaults to "".
        session (aiohttp.ClientSession, optional): Client _session to use. Defaults to None.
        timeout (int, optional): Timeout for the request. Defaults to 10.

    Returns:
        aiohttp.ClientResponse: Server response.
    """
    close_session = session is None
    session = session or ClientSession()

    request_data = {
        "link": link,
        "user": user,
        "name": filename,
        "path": path,
    }

    response = await session.post(
        url=upload_server,
        data=request_data,
        timeout=timeout
    )

    if close_session:
        await session.close()

    return response


async def delete_file(file_hash: str, user: str, session: ClientSession = None, timeout: int = 10) -> ClientResponse:
    """
    Delete a file.

    Args:
        file_hash (str): Hash file, example: TPRSfLvcIu.
        user (str): Your user's hash.
        session (aiohttp.ClientSession, optional): Client _session to use. Defaults to None.
        timeout (int, optional): Timeout for the request. Defaults to 10.

    Returns:
        aiohttp.ClientResponse: Server response.
    """
    close_session = session is None
    session = session or ClientSession()

    request_data = {
        "hash": file_hash,
        "user": user,
    }

    response = await session.post(
        url=BASE_URL + "delete-file",
        data=request_data,
        timeout=timeout
    )

    if close_session:
        await session.close()

    return response


async def rename_file(file_hash: str, user: str, filename: str, session: ClientSession = None,
                      timeout: int = 10) -> ClientResponse:
    """
    Rename a file.

    Args:
        file_hash (str): Hash file, example: TPRSfLvcIu.
        user (str): Your user's hash.
        filename (str): New filename.
        session (aiohttp.ClientSession, optional): Client _session to use. Defaults to None.
        timeout (int, optional): Timeout for the request. Defaults to 10.

    Returns:
        aiohttp.ClientResponse: Server response.
    """
    close_session = session is None
    session = session or ClientSession()

    request_data = {
        "hash": file_hash,
        "user": user,
        "filename": filename,
    }

    response = await session.post(
        url=BASE_URL + "rename-file",
        data=request_data,
        timeout=timeout
    )

    if close_session:
        await session.close()

    return response


async def check_file(file_hash: str, session: ClientSession = None, timeout: int = 10) -> ClientResponse:
    """
    Check if a file exists.

    Args:
        file_hash (str): Hash file, example: TPRSfLvcIu. Array possible ["TPRSfLvcIu", "anotherHash"]. Max 100 hashes.
        session (aiohttp.ClientSession, optional): Client _session to use. Defaults to None.
        timeout (int, optional): Timeout for the request. Defaults to 10.

    Returns:
        aiohttp.ClientResponse: Server response.
    """
    close_session = session is None
    session = session or ClientSession()

    request_data = {
        "hash": file_hash,
    }

    response = await session.post(
        url=BASE_URL + "check-file",
        data=request_data,
        timeout=timeout
    )

    if close_session:
        await session.close()

    return response


async def list_files(user: str, page: int, path: str = "", session: ClientSession = None,
                     timeout: int = 10) -> ClientResponse:
    """
    List all files uploaded by a user.

    Args:
        user (str): Your user's hash.
        page (int): Your current page.
        path (str, optional): File path, example: Folder/My sub folder. Defaults to "".
        session (aiohttp.ClientSession, optional): Client _session to use. Defaults to None.
        timeout (int, optional): Timeout for the request. Defaults to 10.

    Raises:
        ValueError: If page is not a positive number.

    Returns:
        aiohttp.ClientResponse: Server response.
    """
    close_session = session is None
    session = session or ClientSession()

    if page <= 0:
        raise ValueError("Page must be positive number")

    request_data = {
        "user": user,
        "page": page,
        "path": path
    }

    response = await session.post(
        url=BASE_URL + "list-files",
        data=request_data,
        timeout=timeout
    )

    if close_session:
        await session.close()

    return response
