import os
import json

def find_json_files(root_dir, ignore_path):
    json_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.json'):
                file_path = os.path.abspath(os.path.join(root, file))
                if os.path.abspath(ignore_path) == file_path:
                    continue
                json_files.append(file_path)
    return json_files

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

def merge_json_files(json_files):
    merged = []
    for file in json_files:
        data = load_json(file)
        if data is None:
            continue
        if isinstance(data, list):
            merged.extend(data)
        else:
            merged.append(data)
    return merged

if __name__ == '__main__':
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_path = os.path.join(parent_dir, 'manifest.json')

    json_files = find_json_files(parent_dir, output_path)
    print(f"Found {len(json_files)} JSON files.")
    merged_data = merge_json_files(json_files)

    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump(merged_data, out, indent=2, ensure_ascii=False)
    print(f"Merged JSON saved to {output_path}")