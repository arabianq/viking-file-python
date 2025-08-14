# viking-file-python

API Wrapper for [ViKiNG FiLE API](https://vikingfile.com/api)

## Features and Functionality

This Python library provides a convenient way to interact with the ViKiNG FiLE API, allowing you to:

* Upload files (both local and remote URLs).
* Delete files.
* Rename files.
* Check if a file exists.
* List files in your account.
* Manage files in specific paths/folders. .

## Prerequisites

* Python 3.13 or higher
* A ViKiNG FiLE account (if you need to upload files to your account)

## Installation Instructions

1. Install the package using pip:

   ```bash
   pip install viking-file
   ```

## Usage Guide

### Initialization

Import the `VikingClient` or `AsyncVikingClient` class and initialize it with your user hash (if you want to upload
files to your account, otherwise, leave it empty for anonymous upload):

```python
from viking_file import VikingClient, AsyncVikingClient

# Synchronous client
client = VikingClient(user_hash="YOUR_USER_HASH")  # Replace with your actual user hash

# Asynchronous client
async_client = AsyncVikingClient(user_hash="YOUR_USER_HASH")  # Replace with your actual user hash

# also you can use context manager both synchronous and asynchronous

# with VikingClient(user_hash="YOUR_USER_HASH") as client:
    # Your code here

# async with AsyncVikingClient(user_hash="YOUR_USER_HASH") as async_client:
    # Your asynchronous code here
```

### Uploading a Local File (Synchronous)

```python
from viking_file import VikingClient
from pathlib import Path

client = VikingClient(user_hash="YOUR_USER_HASH")

# Upload a file
file_path = Path("path/to/your/file.txt")  # Replace with the actual path to your file
uploaded_file = client.upload_file(
    filepath=file_path,
    path="Optional/Path/On/Server"
)  # path argument is optional

print(f"Uploaded file hash: {uploaded_file.hash}")
print(f"Uploaded file name: {uploaded_file.name}")
print(f"Uploaded file URL: {uploaded_file.url}")
```

### Uploading a Local File (Asynchronous)

```python
import asyncio
from viking_file import AsyncVikingClient
from pathlib import Path


async def upload_file():
    client = AsyncVikingClient(user_hash="YOUR_USER_HASH")

    # Upload a file
    file_path = Path("path/to/your/file.txt")  # Replace with the actual path to your file
    uploaded_file = await client.upload_file(
        filepath=file_path,
        path="Optional/Path/On/Server"
    )  # path argument is optional

    print(f"Uploaded file hash: {uploaded_file.hash}")
    print(f"Uploaded file name: {uploaded_file.name}")
    print(f"Uploaded file URL: {uploaded_file.url}")


asyncio.run(upload_file())
```

### Uploading a Remote File (Asynchronous)

```python
import asyncio
from viking_file import AsyncVikingClient


async def upload_remote_file():
    client = AsyncVikingClient(user_hash="YOUR_USER_HASH")

    # Upload a remote file
    remote_url = "https://example.com/remote_file.zip"  # Replace with the actual URL
    uploaded_file = await client.upload_remote_file(
        url=remote_url,
        filename="new_name.zip",
        path="Optional/Path/On/Server"
    )  # filename and path arguments are optional

    print(f"Uploaded file hash: {uploaded_file.hash}")
    print(f"Uploaded file name: {uploaded_file.name}")
    print(f"Uploaded file URL: {uploaded_file.url}")


asyncio.run(upload_remote_file())
```

### Deleting a File (Asynchronous)

```python
import asyncio
from viking_file import AsyncVikingClient


async def delete_file():
    client = AsyncVikingClient(user_hash="YOUR_USER_HASH")

    # Delete a file
    file_hash = "FILE_HASH_TO_DELETE"  # Replace with the actual file hash
    await client.delete_file(file_hash)

    print(f"File {file_hash} deleted successfully.")


asyncio.run(delete_file())
```

### Renaming a File (Asynchronous)

```python
import asyncio
from viking_file import AsyncVikingClient


async def rename_file():
    client = AsyncVikingClient(user_hash="YOUR_USER_HASH")

    # Rename a file
    file_hash = "FILE_HASH_TO_RENAME"  # Replace with the actual file hash
    new_filename = "new_file_name.txt"
    await client.rename_file(file_hash, new_filename)

    print(f"File {file_hash} renamed to {new_filename} successfully.")


asyncio.run(rename_file())
```

### Listing Files (Asynchronous)

```python
import asyncio
from viking_file import AsyncVikingClient


async def list_files():
    client = AsyncVikingClient(user_hash="YOUR_USER_HASH")

    # List files on page 1
    page_number = 1
    files = await client.list_files(
        page=page_number,
        path="Optional/Path/On/Server"
    )  # path argument is optional

    for file in files:
        print(f"File Hash: {file.hash}, Name: {file.name}, Size: {file.size}, URL: {file.url}")


asyncio.run(list_files())
```

### Listing all files (Asynchronous)

```python
import asyncio
from viking_file import AsyncVikingClient


async def list_all_files():
    client = AsyncVikingClient(user_hash="YOUR_USER_HASH")

    # List all files
    files = await client.list_all_files(
        path="Optional/Path/On/Server"
    )  # path argument is optional

    for file in files:
        print(f"File Hash: {file.hash}, Name: {file.name}, Size: {file.size}, URL: {file.url}")


asyncio.run(list_all_files())
```

### Getting File Information (Asynchronous)

```python
import asyncio
from viking_file import AsyncVikingClient


async def get_file_information():
    client = AsyncVikingClient(user_hash="YOUR_USER_HASH")

    # Get file information
    file_hash = "FILE_HASH_TO_GET_INFO"  # Replace with the actual file hash
    file = await client.get_file(file_hash)


asyncio.run(get_file_information())
```

## API

The `viking_file/api.py` file contains the low-level API functions that are used by the `VikingClient` and
`AsyncVikingClient` classes. These functions are primarily intended for internal use but can be used directly if needed.

## Contributing Guidelines

Contributions are welcome!  To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Implement your changes.
4. Write tests for your changes.
5. Ensure all tests pass.
6. Submit a pull request.

## License Information

This project is licensed under the [MIT License](https://github.com/arabianq/viking-file-python/blob/main/LICENSE)

## Contact/Support Information

For questions, bug reports, or feature requests, please open an issue on
the [GitHub repository](https://github.com/arabianq/viking-file-python).
