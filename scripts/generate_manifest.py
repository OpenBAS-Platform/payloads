import os
import json
import zipfile

def ensure_generated_dir(root_dir):
    gen_dir = os.path.join(root_dir, "_generated")
    os.makedirs(gen_dir, exist_ok=True)
    return gen_dir

def fix_and_load_json(file_path):
    changed = False
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        info = data.get("payload_information", None)
        if info and isinstance(info, dict):
            # Set required values
            if info.get('payload_source') != 'FILIGRAN':
                info['payload_source'] = 'FILIGRAN'
                changed = True
            if info.get('payload_status') != 'VERIFIED':
                info['payload_status'] = 'VERIFIED'
                changed = True

            # Handle payload_external_id and payload_id
            if 'payload_id' in info:
                if info.get('payload_external_id') != info['payload_id']:
                    info['payload_external_id'] = info['payload_id']
                    changed = True
                del info['payload_id']
                changed = True

            # Remove unwanted keys
            for key in ['payload_collector_type', 'payload_collector']:
                if key in info:
                    del info[key]
                    changed = True

        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def find_payload_jsons(root_dir):
    payloads = []
    for folder, dirs, files in os.walk(root_dir):
        if "payload.json" in files:
            payload_json_path = os.path.join(folder, "payload.json")
            attachments_path = os.path.join(folder, "attachments.zip")
            has_attachments = os.path.isfile(attachments_path)
            payloads.append({
                "payload_json": payload_json_path,
                "attachments": attachments_path if has_attachments else None,
                "dir": folder,
                "dir_name": os.path.basename(folder)
            })
    return payloads

def create_nested_payload_zip(payload_json_path, attachments_path, payload_external_id, dir_name, generated_dir):
    # Step 1: Create the inner zip named after the directory
    inner_zip_path = os.path.join(generated_dir, f"{dir_name}.zip")
    with zipfile.ZipFile(inner_zip_path, 'w') as zf:
        # Add payload.json with comment "Payload"
        zinfo = zipfile.ZipInfo("payload.json")
        zinfo.comment = b"Payload"
        with open(payload_json_path, "rb") as f:
            zf.writestr(zinfo, f.read())
        # If attachments.zip exists, add it with comment "EncryptedAttachment"
        if attachments_path:
            zinfo = zipfile.ZipInfo("attachments.zip")
            zinfo.comment = b"EncryptedAttachment"
            with open(attachments_path, "rb") as f:
                zf.writestr(zinfo, f.read())
    # Step 2: Create the outer zip named after payload_external_id
    outer_zip_path = os.path.join(generated_dir, f"{payload_external_id}.zip")
    with zipfile.ZipFile(outer_zip_path, 'w') as zf:
        zinfo = zipfile.ZipInfo(f"{dir_name}.zip")
        zinfo.comment = b"PayloadArchive"
        with open(inner_zip_path, "rb") as f:
            zf.writestr(zinfo, f.read())
    # Remove the inner zip after nesting to clean up
    os.remove(inner_zip_path)
    print(f"Created {outer_zip_path}")

def build_manifest_payload(info, tags_lookup):
    result = {}
    result['payload_external_id'] = info.get('payload_external_id', '')
    result['payload_name'] = info.get('payload_name', '')
    result['payload_description'] = info.get('payload_description', '')
    result['payload_platforms'] = info.get('payload_platforms', [])

    # Simplified attack patterns
    attack_patterns = []
    for ap in info.get('payload_attack_patterns', []):
        if isinstance(ap, dict):
            attack_patterns.append({
                "attack_pattern_external_id": ap.get("attack_pattern_external_id"),
                "attack_pattern_name": ap.get("attack_pattern_name")
            })
        elif isinstance(ap, str):  # fallback: string id
            attack_patterns.append({
                "attack_pattern_external_id": ap,
                "attack_pattern_name": ""
            })
    result['payload_attack_patterns'] = attack_patterns

    # Simplified tags: map tag IDs to names using tags_lookup
    tag_ids = info.get('payload_tags', [])
    tag_names = [tags_lookup.get(tag_id) for tag_id in tag_ids if tag_id in tags_lookup]
    result['payload_tags'] = tag_names

    return result

def merge_json_files(payloads, generated_dir):
    manifest_list = []
    for payload in payloads:
        data = fix_and_load_json(payload['payload_json'])
        if data is None:
            continue
        info = data.get('payload_information', {})
        tags_list = data.get('payload_tags', [])
        tags_lookup = {tag['tag_id']: tag['tag_name'] for tag in tags_list if 'tag_id' in tag and 'tag_name' in tag}
        payload_external_id = info.get('payload_external_id')
        # create nested zip only if payload_external_id present
        if payload_external_id:
            create_nested_payload_zip(
                payload['payload_json'],
                payload['attachments'],
                payload_external_id,
                payload['dir_name'],
                generated_dir
            )
        # Add simplified info to manifest, with tag name extraction
        manifest_list.append(build_manifest_payload(info, tags_lookup))
    return manifest_list

if __name__ == '__main__':
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_path = os.path.join(parent_dir, 'manifest.json')
    generated_dir = ensure_generated_dir(parent_dir)

    payloads = find_payload_jsons(parent_dir)

    print(f"Found {len(payloads)} payload.json files.")
    manifest_data = merge_json_files(payloads, generated_dir)

    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump(manifest_data, out, indent=2, ensure_ascii=False)
    print(f"Merged manifest saved to {output_path}")
