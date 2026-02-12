import os
import requests
import zipfile
import shutil
import sys

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip"
MODEL_ZIP = "model.zip"
EXTRACT_DIR = "models"
TARGET_DIR = "models/model"

def download_file(url, filename):
    print(f"Downloading model from {url}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_length = int(r.headers.get('content-length'))
        dl = 0
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: 
                    dl += len(chunk)
                    f.write(chunk)
                    done = int(50 * dl / total_length)
                    sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {dl//1024//1024}MB")
                    sys.stdout.flush()
    print("\nDownload complete.")

def setup_model():
    if not os.path.exists(EXTRACT_DIR):
        os.makedirs(EXTRACT_DIR)

    # 1. Download
    if not os.path.exists(MODEL_ZIP):
        download_file(MODEL_URL, MODEL_ZIP)
    else:
        print("Model zip already exists. Skipping download.")

    # 2. Extract
    print("Extracting model...")
    with zipfile.ZipFile(MODEL_ZIP, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
    print("Extraction complete.")

    # 3. Rename/Setup
    # The zip usually contains a folder like "vosk-model-en-us-0.22-lgraph"
    extracted_folder_name = "vosk-model-en-us-0.22-lgraph"
    extracted_path = os.path.join(EXTRACT_DIR, extracted_folder_name)
    
    if os.path.exists(TARGET_DIR):
        print(f"Backing up existing model to {TARGET_DIR}_old")
        if os.path.exists(f"{TARGET_DIR}_old"):
            shutil.rmtree(f"{TARGET_DIR}_old")
        shutil.move(TARGET_DIR, f"{TARGET_DIR}_old")
        
    if os.path.exists(extracted_path):
        print(f"Setting up new model at {TARGET_DIR}")
        os.rename(extracted_path, TARGET_DIR)
        print("Model setup successful!")
        
        # Cleanup
        os.remove(MODEL_ZIP)
        print("Cleaned up zip file.")
    else:
        print(f"Error: Could not find extracted folder {extracted_path}")

if __name__ == "__main__":
    setup_model()
