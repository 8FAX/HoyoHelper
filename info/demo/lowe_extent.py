import os

def lowercase_file_extension(base_directory):
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_name, file_ext = os.path.splitext(file)
            new_file_ext = file_ext.lower()
            new_file_path = os.path.join(root, file_name + new_file_ext)
            
            if file_path != new_file_path:
                try:
                    os.rename(file_path, new_file_path)
                    print(f'Renamed: {file_path} -> {new_file_path}')
                except Exception as e:
                    print(f'Error renaming {file_path}: {e}')

# Example usage
directory = 'C:/Users/liam/OneDrive/Desktop/curent projects/hoyo-helper./assets'  # Replace with your desired directory 
# DO NOT SET TO ROOT DIRECTORY OF YOUR DRIVE (e.g. 'C:/'  or  '/') AS IT WILL RENAME ALL FILES ON YOUR DRIVE and what it cant it will throw an error
# I DID THIS AHHAHAHAHH we wll see if my pc is still alive after a restart
lowercase_file_extension(directory)
