import os

def clean_and_rename_files(directory: str) -> None:
    """
    The function `clean_and_rename_files` takes a directory path as input, deletes specific file types
    (.gif and .mp4) from the directory, and renames the remaining files in the directory with a
    numerical prefix.
    
    Author - Liam Scott
    Last update - 06/18/2024
    @param directory (str) - The directory path containing the files to be cleaned and renamed.
    """

    os.chdir(directory)
    files = [f for f in os.listdir() if os.path.isfile(f)]

    for file in files:
        if file.endswith('.gif') or file.endswith('.mp4'):
            os.remove(file)

    remaining_files = [f for f in os.listdir() if os.path.isfile(f)]

    counter = 1
    for file in sorted(remaining_files):
        extension = os.path.splitext(file)[1]
        new_name = f"{counter}{extension}"
        os.rename(file, new_name)
        counter += 1

    print("Files have been renamed and specified files deleted.")

# The code block `if __name__ == "__main__":` is a common Python idiom used to check whether the
# current script is being run directly by the Python interpreter. When a Python file is executed, the
# special variable `__name__` is set to `"__main__"` if the file is being run as the main program.
if __name__ == "__main__":
    directory_path = "assets/car_dec"
    clean_and_rename_files(directory_path)
