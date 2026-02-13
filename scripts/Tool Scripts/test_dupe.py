import os

dataset9 = "raw_pdfs/Dataset 9"

all_files = []
for folder in os.listdir(dataset9):
    folder_path = os.path.join(dataset9, folder)
    for f in os.listdir(folder_path):
        all_files.append(f)

print("Total files:", len(all_files))
print("Unique files:", len(set(all_files)))
print("Duplicates detected:", len(all_files) - len(set(all_files)))
