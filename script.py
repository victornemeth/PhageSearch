with open('db_pdb_files.txt', 'r') as file:
    db_files = [line.strip().split('/')[-1] for line in file.readlines() if line.strip() and not line.startswith('pdb_file')]

# Read directory files, also stripping the path
with open('dir_pdb_files.txt', 'r') as file:
    dir_files = [line.strip().split('/')[-1] for line in file.readlines() if line.strip()]

# Convert lists to sets to find differences
db_files_set = set(db_files)
dir_files_set = set(dir_files)

print(db_files_set)
print("dir")
print(dir_files_set)

# Get the difference: files in db not in dir
diff_files = db_files_set - dir_files_set

# Output the result
print("Files in the database but not in the directory:")
for file in sorted(diff_files):
    print(file)

# Check if there are no missing files
if not diff_files:
    print("All database files are present in the directory.")
