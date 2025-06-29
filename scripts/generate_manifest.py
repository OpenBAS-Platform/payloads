import os
import json


def find_json_files(root_dir, ignore_path):
    json_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".json"):
                file_path = os.path.abspath(os.path.join(root, file))
                if os.path.abspath(ignore_path) == file_path:
                    continue
                json_files.append(file_path)
    return json_files


def fix_and_load_json(file_path, parent_dir):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        changed = False

        info = data.get("payload_information", None)
        if info and isinstance(info, dict):
            # Set required values
            if info.get("payload_source") != "FILIGRAN":
                info["payload_source"] = "FILIGRAN"
                changed = True
            if info.get("payload_status") != "VERIFIED":
                info["payload_status"] = "VERIFIED"
                changed = True

            # Handle payload_external_id and payload_id
            if "payload_external_id" not in info or info["payload_external_id"] is None:
                info["payload_external_id"] = info["payload_id"]
                changed = True

            # Remove unwanted keys
            for key in ["payload_collector_type", "payload_collector", "payload_id"]:
                if key in info:
                    del info[key]
                    changed = True

        # Handle document_path in payload_document if attachments.zip exists
        payload_doc = data.get("payload_document")
        if payload_doc is not None and isinstance(payload_doc, dict):
            dir_path = os.path.dirname(file_path)
            attachment_path = os.path.join(dir_path, "attachments.zip")
            if os.path.isfile(attachment_path):
                # Compute relative path from parent_dir and make URL-compatible
                rel_path = os.path.relpath(attachment_path, parent_dir).replace(
                    os.sep, "/"
                )
                if payload_doc.get("document_path") != rel_path:
                    payload_doc["document_path"] = rel_path
                    changed = True

        if changed:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def merge_json_files(json_files, parent_dir):
    merged = []
    for file in json_files:
        data = fix_and_load_json(file, parent_dir)
        if data is None:
            continue
        if isinstance(data, list):
            merged.extend(data)
        else:
            merged.append(data)
    return merged


if __name__ == "__main__":
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_path = os.path.join(parent_dir, "manifest.json")

    json_files = find_json_files(parent_dir, output_path)
    print(f"Found {len(json_files)} JSON files.")
    merged_data = merge_json_files(json_files, parent_dir)

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(merged_data, out, indent=2, ensure_ascii=False)
    print(f"Merged JSON saved to {output_path}")
