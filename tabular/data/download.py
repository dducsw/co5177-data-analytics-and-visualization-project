import shutil
from pathlib import Path
import kagglehub

# Download dataset to local cache
cache_path = kagglehub.dataset_download("sgpjesus/bank-account-fraud-dataset-neurips-2022")
print("Downloaded to cache:", cache_path)

# Copy files to data/ folder
target_dir = Path(__file__).resolve().parent
for item in Path(cache_path).iterdir():
    dest = target_dir / item.name
    if item.is_dir():
        shutil.copytree(item, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(item, dest)

print("Files copied to destination folder successfully.")
