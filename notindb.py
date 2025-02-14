# Read the files from the database
with open('db_pdb_files.txt', 'r') as db_file:
    db_files = db_file.read().splitlines()

# Read the files from the directory
with open('dir_pdb_files.txt', 'r') as dir_file:
    dir_files = dir_file.read().splitlines()

# Remove headers, normalize file paths, and make comparison case-insensitive
db_files = [f.split('/')[-1].strip().lower() for f in db_files if f.endswith('.pdb')]
dir_files = [f.split('/')[-1].strip().lower() for f in dir_files if f.endswith('.pdb')]

# Convert to sets for easy comparison
db_set = set(db_files)
dir_set = set(dir_files)

# Find the files in the database that are not in the directory
non_intersecting_files = db_set - dir_set

# Print the counts and non-intersecting files
print(f"Number of database files: {len(db_files)}")
print(f"Number of directory files: {len(dir_files)}")
print(f"Number of files in database but not in directory: {len(non_intersecting_files)}")

if non_intersecting_files:
    print("\nFiles in database but not in directory:")
    for file in sorted(non_intersecting_files):
        print(file)
else:
    print("All files in the database are also in the directory.")
