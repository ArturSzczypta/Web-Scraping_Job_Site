import os
import sys

# Change the current working directory to 'scripts'
os.chdir('../')
# Add 'scripts' directory to the sys.path
sys.path.append('.')

directory = os.getcwd()
print(f"Current directory: {directory}")

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

# Replace the last folder name with a different one
new_directory = os.path.dirname(current_directory) + "/logging_files"
print("New directory:", new_directory)