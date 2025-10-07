import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

DATASET = "vignonantoine/combinedasldatasets"
DOWNLOAD_PATH = "external_asl_images"

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

api = KaggleApi()
api.authenticate()

print("⬇ Downloading ASL Alphabet image dataset...")
api.dataset_download_files(DATASET, path=DOWNLOAD_PATH, unzip=True)
print("✅ Download and extraction complete.")
