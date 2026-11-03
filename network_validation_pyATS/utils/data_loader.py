import yaml
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def load_yaml_data(relative_path):
    """Safely load expected state data from a YAML file."""

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    file_path = os.path.join(base_dir, relative_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Expected data file not found: {file_path}")
        
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data