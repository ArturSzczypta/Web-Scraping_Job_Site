import os
import sys

# Change the current working directory to 'scripts'
os.chdir('../')
# Add 'scripts' directory to the sys.path
sys.path.append('.')

directory = os.getcwd()
print(f"Current directory: {directory}")
def example():
    current_directory = directory
    for _ in range(3):
        print(f"Current directory: {current_directory}")
        print("Directories:")
        for dir in os.listdir(current_directory):
            if os.path.isdir(os.path.join(current_directory, dir)):
                print(f"\t{dir}")
        print("Files:")
        for file in os.listdir(current_directory):
            if os.path.isfile(os.path.join(current_directory, file)):
                print(f"\t{file}")
        print()

        current_directory = os.path.dirname(current_directory)
        print(f"New current directory: {current_directory}")

    # Replace the last folder name with a different one
    new_directory = os.path.dirname(current_directory) + "/logging_files"
    print("New directory:", new_directory)

def find_file(dir_name, file_name):
    '''Find file in the directory'''
    for dir, subdirs, files in os.walk(dir_name):
        print(f"Searching '{dir}'")
        print("Subdirectories:", subdirs)
        print("Files:", files)
        if file_name in files:
            print(f"Found file '{file_name}' in '{dir}'")
            return os.path.join(dir, file_name)
    return None

find_file(directory, 'logging_configuration.json')