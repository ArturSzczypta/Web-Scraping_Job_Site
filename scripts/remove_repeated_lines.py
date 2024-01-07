'''Remove repeated lines from a file'''

file_path = "C:/Users/Artur/Documents/GitHub/Web-Scraping_Job_Site/txt_files/succesfull_extractions.txt"

# Read the file
with open(file_path, "r", encoding='utf8') as file:
    lines = file.readlines()

# Remove repeated lines
unique_lines = list(set(lines))

# Write the unique lines back to the file
with open(file_path, "w", encoding='utf8') as file:
    file.writelines(unique_lines)
