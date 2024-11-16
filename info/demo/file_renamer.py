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

import os
from datetime import datetime

def lowercase_file_extension_and_rename(base_directory):
    """
    The function `lowercase_file_extension_and_rename` recursively renames files in a directory by
    converting their extensions to lowercase and creates a text file with directory information.
    
    Author - Liam Scott
    Last update - 11/12/2024
    
    @ param base_directory ()  - The `base_directory` parameter in the
    `lowercase_file_extension_and_rename` function is the starting directory from which the function
    will recursively walk through all subdirectories and files to rename the files with lowercase file
    extensions and create a text file in each directory with information about the directory.
    
    """
    for root, dirs, files in os.walk(base_directory):
        rel_path = os.path.relpath(root, base_directory)
        path_str = rel_path.replace(os.sep, '_')
        if path_str == '.':
            path_str = ''
        
        i = 1
        last_modified_time = None
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_mtime = os.path.getmtime(file_path)
                if last_modified_time is None or file_mtime > last_modified_time:
                    last_modified_time = file_mtime
                
                file_name, file_ext = os.path.splitext(file)
                new_file_ext = file_ext.lower()
                if path_str:
                    new_file_name = f'{path_str}_{i}{new_file_ext}'
                else:
                    new_file_name = f'{i}{new_file_ext}'
                new_file_path = os.path.join(root, new_file_name)
                
                os.rename(file_path, new_file_path)
                print(f'{file_path} renamed to {new_file_path}')
                i += 1
            except Exception as e:
                print(f'Error renaming file {file_path}: {e}')
        
        txt_file_path = os.path.join(root, f'{path_str}_directory_info.txt')
        num_files = len(files)
        try:
            if last_modified_time is not None:
                last_modified_datetime = datetime.fromtimestamp(last_modified_time)
                last_modified_str = last_modified_datetime.strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_modified_str = 'N/A'
            
            with open(txt_file_path, 'w') as txt_file:
                txt_file.write(f'Number of files: {num_files}\n')
                txt_file.write(f'Last modified: {last_modified_str}\n')
            print(f'Directory info written to {txt_file_path}')
        except Exception as e:
            print(f'Error writing directory info to {txt_file_path}: {e}')



def remove_txt_files(base_directory):
    """
    The function `remove_txt_files` removes all .txt files within a specified base directory.
    
    Author - Liam Scott
    Last update - 11/12/2024
    
    @ param base_directory ()  - The `base_directory` parameter in the `remove_txt_files` function is
    the starting directory from which you want to remove all the .txt files. The function will
    recursively search through all directories and subdirectories within the `base_directory` and delete
    any files with a .txt extension.
    
    """
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f'{file_path} removed')

# The code snippet you provided is a common Python idiom that allows a Python script to be used both
# as a standalone program and as a module that can be imported into other scripts.
if __name__ == '__main__':
    directory = 'C:/Users/liam/OneDrive/Desktop/curent projects/hoyo-helper./assets'
    lowercase_file_extension_and_rename(directory)
    #remove_txt_files(directory)