import os
import kaggle

# Set up the Kaggle API client
kaggle.api.authenticate()

# Define the dataset
dataset = "pauloarayasantiago/pokmon-stats-across-generations-and-typings"

# Get the project root directory (assuming the script is in the 'scripts' folder)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the path to the 'data' directory
data_dir = os.path.join(project_root, "data")

# Ensure the 'data' directory exists
os.makedirs(data_dir, exist_ok=True)

# Download the dataset to the 'data' directory
kaggle.api.dataset_download_files(dataset, path=data_dir, unzip=True)

print(f"Dataset downloaded and extracted to: {data_dir}")
