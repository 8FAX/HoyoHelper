# -------------------------------------------------------------------------------------
# HoYo Helper - a hoyolab helper tool
# Made with ♥ by 8FA (Uilliam.com)

# Copyright (C) 2024 copyright.Uilliam.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see https://github.com/8FAX/HoyoHelper/blob/main/LICENSE.md.
# SPDX-License-Identifier: AGPL-3.0-or-later
# do not remove this notice

# This file is part of HoYo Helper.
#version 0.2.0
# -------------------------------------------------------------------------------------

from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv
import os
import ssl
import requests
from requests.adapters import HTTPAdapter

# The `TLSAdapter` class is a custom adapter for handling TLS connections in Python's `requests`
# library.
class TLSAdapter(HTTPAdapter):
    def __init__(self, ssl_version=None, **kwargs):
        """
        The function `__init__` initializes a TLSAdapter object with an optional SSL version parameter
        and additional keyword arguments.
        
        Author - Liam Scott
        Last update - 11/16/2024
        
        @ param ssl_version ()  - The `ssl_version` parameter in the `__init__` method is used to
        specify the SSL version to be used in the TLSAdapter class. It is an optional parameter that can
        be passed when creating an instance of the TLSAdapter class. If a value is provided for
        `ssl_version`, it
        
        """
        self.ssl_version = ssl_version
        super(TLSAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        """
        The `init_poolmanager` function sets the SSL version and calls the superclass method with the
        provided arguments and keyword arguments.
        
        Author - Liam Scott
        Last update - 11/16/2024
        
        
        @ returns The `init_poolmanager` method of the `TLSAdapter` class is being called with the
        arguments `*args` and `**kwargs`, where the `ssl_version` key in the `kwargs` dictionary is set
        to `self.ssl_version`. The return value is the result of calling the `init_poolmanager` method
        of the superclass of `TLSAdapter` with the modified `kwargs`.
        
        """
        kwargs['ssl_version'] = self.ssl_version
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)
    



def upload(base_directory):
    """
    Uploads files from a directory to the CDN using PUT requests with a progress bar.
    """
    load_dotenv()
    auth_key = os.getenv('cf_auth')

    if not auth_key:
        print("Error: Authentication key not found. Please check your environment variables.")
        return

    base_url = "https://cdn.hoyohelper.com/"
    headers = {
        'Auth-Key': auth_key,
        'Source': 'HoYoHelper',
        'Version': '0.2.0'
    }

    session = requests.Session()
    session.mount(base_url, TLSAdapter(ssl_version=ssl.PROTOCOL_TLSv1_2))

    file_paths = []
    for root, _, files in os.walk(base_directory):
        for file in files:
            file_paths.append(os.path.join(root, file))

    with tqdm(total=len(file_paths), desc="Uploading files", unit="file") as pbar:
        for file_path in file_paths:
            key = Path(os.path.relpath(file_path, base_directory)).as_posix()
            try:
                with open(file_path, 'rb') as f:
                    response = session.put(f"{base_url}{key}", headers=headers, data=f)

                if response.status_code == 200:
                    pbar.write(f'{file_path} successfully uploaded as {key}')
                elif response.status_code == 401:
                    pbar.write(f'Unauthorized: Check your Auth-Key for {file_path}')
                elif response.status_code == 403:
                    pbar.write(f'Forbidden: Bot detection or improperly formatted request for {file_path}')
                elif response.status_code == 405:
                    pbar.write(f'Method Not Allowed: Invalid request method for {file_path}')
                else:
                    pbar.write(f'Failed to upload {file_path}. Status: {response.status_code}, Response: {response.text}')

            except requests.exceptions.RequestException as e:
                pbar.write(f'Network error while uploading {file_path}: {e}')
            except Exception as e:
                pbar.write(f'Error processing {file_path}: {e}')
            finally:
                pbar.update(1)


# The code snippet you provided is a common Python idiom that allows a Python script to be used both
# as a standalone program and as a module that can be imported into other scripts.
if __name__ == '__main__':
    directory = 'C:/Users/liam/OneDrive/Desktop/curent projects/hoyo-helper./assets'
    upload(directory)
    
