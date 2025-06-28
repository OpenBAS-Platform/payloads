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

def fix_and_load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        changed = False
        # Set required values
        if data.get('payload_source') != 'FILIGRAN':
            data['payload_source'] = 'FILIGRAN'
            changed = True
        if data.get('payload_status') != 'VERIFIED':
            data['payload_status'] = 'VERIFIED'
            changed = True
        # Remove unwanted keys
        for key in ['payload_external_id', 'payload_collector_type', 'payload_collector']:
            if key in data:
                del data[key]
                changed = True
        # Overwrite file if changes were made
        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def merge_json_files(json_files):
    merged = []
    for file in json_files:
        data = fix_and_load_json(file)
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
