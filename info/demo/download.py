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
#version 0.1.0
# -------------------------------------------------------------------------------------

import requests


def download_file(url, save_path):
    """
    This function downloads a file from a given URL and saves it to a specified path.
    
    Author - Liam Scott
    Last update - 11/16/2024
    
    @ param url ()  - The `url` parameter is the URL from which the file needs to be downloaded.
    @ param save_path ()  - The `save_path` parameter is the location where the downloaded file will be
    saved on your local machine. It should be a string representing the full path including the file
    name where you want to save the downloaded file. For example, if you want to save a file named
    "example.txt" in the
    
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Source": "HoYoHelper",
        "Version": "0.2.0"
    }

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192): 
                file.write(chunk)

        print(f"File downloaded successfully and saved to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download file: {e}")



if __name__ == '__main__':

    url = 'https://cdn.hoyohelper.com/gi/stickers/gi_stickers_36.png'
    save_path = 'gi_stickers_36.png'
    download_file(url, save_path)

# we will use this code to upload the file to the CDN we will keep the gh-pages branch as a way to keep and update the list of files that are uploaded to the CDN as well as a static website that will be used to display the files that are uploaded to the CDN.
# we wil also use the gh-pages branch as a wiki for the project. 
# i will keep adding more features to the project as i go along.