import os
import hashlib
import asyncio
import aiohttp
from tqdm import tqdm
from unittest import mock

# Import the function you want to test
from main import download_repo_contents


# Test if the download is successful for a single file
async def test_download_file(tmp_path):
    url = 'https://gitea.radium.group/radium/project-configuration/src/branch/master/LICENSE'
    file_path = os.path.join(tmp_path, 'LICENSE')
    async with aiohttp.ClientSession() as session:
        with mock.patch.object(tqdm, 'update') as update_mock:
            await download_file(session, url, file_path, progress_bar=tqdm(total=1))
            update_mock.assert_called_with(9)  # Replace with the expected update count for file.txt
    assert os.path.exists(file_path)
    with open(file_path, 'rb') as f:
        assert hashlib.sha256(f.read()).hexdigest() == '561d439a4f6e13c7ea9fe03e0e9f408295a8cff7a70e5297bba0933287dbdca0'  # Replace with the expected SHA-256 hash for file.txt


# Test if the download is successful for multiple files
async def test_download_repo_contents(tmp_path):
    async with aiohttp.ClientSession() as session:
        with mock.patch.object(tqdm, 'update') as update_mock:
            sha256_hashes = await download_repo_contents(session, tmp_path)
            update_mock.assert_called_with(len(urls) + len(urls_nitpic))  # Replace with the expected total update count
    for filename, expected_hash in expected_sha256_hashes.items():
        file_path = os.path.join(tmp_path, filename)
        assert os.path.exists(file_path)
        with open(file_path, 'rb') as f:
            assert hashlib.sha256(f.read()).hexdigest() == expected_hash


# Test if the temporary folder is created if it doesn't exist
async def test_temp_folder_creation(tmp_path):
    assert not os.path.exists(os.path.join(tmp_path, 'tmp'))
    await download_repo_contents(aiohttp.ClientSession(), tmp_path)
    assert os.path.exists(os.path.join(tmp_path, 'tmp'))


# Test if the download is skipped for a file with a non-200 status code
async def test_download_file_non_200_status(tmp_path):
    url = 'https://example.com/404'
    file_path = os.path.join(tmp_path, '404')
    async with aiohttp.ClientSession() as session:
        with mock.patch.object(tqdm, 'update') as update_mock:
            await download_file(session, url, file_path, progress_bar=tqdm(total=1))
            update_mock.assert_not_called()
    assert not os.path.exists(file_path)


# Test if the download is skipped for a non-existent URL
async def test_download_file_nonexistent_url(tmp_path):
    url = 'https://nonexistent.com/file.txt'
    file_path = os.path.join(tmp_path, 'file.txt')
    async with aiohttp.ClientSession() as session:
        with mock.patch.object(tqdm, 'update') as update_mock:
            await download_file(session, url, file_path, progress_bar=tqdm(total=1))
            update_mock.assert_not_called()
    assert not os.path.exists(file_path)


# Test if the function returns an empty dictionary if no files are downloaded
async def test_download_repo_contents_no_files(tmp_path):
    async with aiohttp.ClientSession() as session:
        sha256_hashes = await download_repo_contents(session, tmp_path, [])
        assert sha256_hashes == {}
