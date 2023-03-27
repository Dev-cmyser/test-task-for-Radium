import os

import hashlib
import asyncio
import aiohttp
import tqdm.asyncio
from tqdm import tqdm
import tqdm.asyncio



                    
                    

async def download_file(session, url, filename, progress_bar=None):
    async with session.head(url) as resp:
        if resp.status != 200:
            return
        async with session.get(url) as resp:
            with open(filename, 'wb') as f:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    if progress_bar:
                        progress_bar.update(len(chunk))

async def download_repo_contents():
    temp_folder = 'tmp/'
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    async with aiohttp.ClientSession() as session:
        base_url = 'https://gitea.radium.group/radium/project-configuration/src/branch/master/'
        urls = [
            'README.md',
            'LICENSE'
            
        ]
        urls_nitpic = [
            'all.toml',
            'darglint.toml',
            'editorconfig.toml',
            'file-structure.toml',
            'flake8.toml',
            'isort.toml',
            'pytest.toml',
            'styleguide.toml'
        ]
        tasks = [download_file(session, base_url + url, os.path.join(temp_folder, url)) for url in urls]
        tasks += [download_file(session, base_url + 'nitpick/' + url, os.path.join(temp_folder, url)) for url in urls_nitpic]
        with tqdm.asyncio.tqdm(total=len(tasks)) as progress_bar:
            await asyncio.gather(*[download_file(session, base_url + url, os.path.join(temp_folder, url), progress_bar=progress_bar) for url in urls])
            await asyncio.gather(*[download_file(session, base_url + 'nitpick/' + url, os.path.join(temp_folder, url), progress_bar=progress_bar) for url in urls_nitpic])
    sha256_hashes = {}
    for filename in os.listdir(temp_folder):
        if os.path.isfile(os.path.join(temp_folder, filename)):
            with open(os.path.join(temp_folder, filename), 'rb') as f:
                sha256_hash = hashlib.sha256(f.read()).hexdigest()
                sha256_hashes[filename] = sha256_hash
    return sha256_hashes

async def run():
    sha256_hashes = await download_repo_contents()
    for k, v in sha256_hashes.items():
        print(f'File tmp/{k}: hash: {v}')

if __name__ == '__main__':
    asyncio.run(run())
