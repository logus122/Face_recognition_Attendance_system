# data_manager.py
import os
import cv2
import pandas as pd
from pathlib import Path
from datetime import datetime
import config
import api_service


def save_local_backup(name, image_data):
    """Saves image to the managed_faces folder"""
    safe_filename = "".join([c for c in name if c.isalnum() or c in (' ', '-', '_')]).strip()
    file_path = os.path.join(config.DB_FOLDER, f"{safe_filename}.jpg")

    try:
        # Case 1: Numpy array (OpenCV image)
        if hasattr(image_data, 'shape'):
            cv2.imwrite(file_path, image_data)
            print(f"   [Local] Saved backup: {file_path}")
            return True

        # Case 2: Bytes (from Streamlit camera/upload)
        elif isinstance(image_data, (bytes, bytearray)):
            with open(file_path, 'wb') as f:
                f.write(image_data)
            print(f"   [Local] Saved backup: {file_path}")
            return True

        # Case 3: File path string
        elif isinstance(image_data, str):
            # Check if it's a valid file path
            if os.path.exists(image_data):
                img = cv2.imread(image_data)
                if img is not None:
                    cv2.imwrite(file_path, img)
                    print(f"   [Local] Saved backup: {file_path}")
                    return True
                else:
                    print(f"   [Local] Failed to read image from: {image_data}")
                    return False
            else:
                print(f"   [Local] File not found: {image_data}")
                return False

        else:
            print(f"   [Local] Unsupported image_data type: {type(image_data)}")
            return False

    except Exception as e:
        print(f"   [Local] Error saving backup: {e}")
        return False


def log_attendance_excel(name):
    """Logs attendance record to the Excel file"""
    file_path = "diemdanh.xlsx"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[name, now]], columns=['Name', 'Time'])

    try:
        if os.path.exists(file_path):
            df_old = pd.read_excel(file_path)
            df_final = pd.concat([df_old, new_data], ignore_index=True)
            df_final.to_excel(file_path, index=False)
        else:
            new_data.to_excel(file_path, index=False)
        return True, now
    except Exception as e:
        print(f"Error writing to Excel: {e}")
        return False, now


def import_from_excel_file(excel_path):
    """Imports subjects from a local Excel file with 'name' and 'path' columns."""
    print(f"\n>>> Reading Excel file: {excel_path}")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    if 'name' not in df.columns or 'path' not in df.columns:
        print("Error: Excel file is missing columns 'name' or 'path'.")
        return

    print(f"Found {len(df)} rows. Starting import...\n")
    for _, row in df.iterrows():
        name = str(row['name']).strip()
        path = str(row['path']).strip().replace('"', '')

        if not os.path.exists(path):
            print(f"   X Error: Image not found at {path}")
            continue

        p = api_service.add_person(name, path)
        if p["ok"]:
            print(f"   ✓ Cloud OK: {name}")
            save_local_backup(name, path)
        else:
            print(f"   X Cloud Fail: {p['error']}")
    print("\n>>> IMPORT COMPLETE!")


# 💥 START OF CHANGES: SYNC FUNCTION REPLACEMENT
def sync_uploaded_files_with_cloud(uploaded_files_list):
    """
    Synchronizes Cloud by deleting subjects whose names do not match the uploaded file list.
    Rule: If a person is in the Cloud but NOT in the uploaded file list, they are deleted from the Cloud.

    Args:
        uploaded_files_list: List of uploaded file objects from Streamlit.
    """
    print(f"\n>>> Synchronizing Cloud with {len(uploaded_files_list)} uploaded files...")

    # 1. Get the list of names (stems) from the uploaded files
    local_names = [
        Path(f.name).stem.lower()
        for f in uploaded_files_list
    ]

    cloud_people = api_service.get_all_subjects()
    if not cloud_people:
        print("Cloud is empty. No synchronization needed.")
        return 0

    deleted_count = 0
    for p in cloud_people:
        pid = p.get("id") or p.get("uuid")
        pname = p.get("name", "")
        # Create a safe name (normalized) to compare with the file stem
        safe_cloud_name = "".join([c for c in pname if c.isalnum() or c in (' ', '-', '_')]).strip().lower()

        # If present in the Cloud but NOT in the uploaded list -> Delete from Cloud
        if safe_cloud_name not in local_names:
            print(f"⚠ Deleting '{pname}' from Cloud (not found in the uploaded list)...")
            if api_service.delete_person_by_uuid(pid):
                deleted_count += 1

    print(f">>> Synchronization complete! Deleted {deleted_count} people from Cloud.")
    return deleted_count


# 💥 END OF CHANGES: SYNC FUNCTION REPLACEMENT


def import_from_excel_df(df):
    """
    Imports subject list from an Excel DataFrame (loaded via Streamlit).
    DataFrame must have 'name' and 'path' columns (where path is a local file path).
    """
    print("\n>>> Importing via DataFrame...")

    if 'name' not in df.columns or 'path' not in df.columns:
        print("Error: Excel file is missing columns 'name' or 'path'.")
        return

    print(f"Found {len(df)} rows. Starting import...\n")

    for _, row in df.iterrows():
        name = str(row['name']).strip()
        path = str(row['path']).strip().replace('"', '')

        if not os.path.exists(path):
            print(f"   X Error: Image not found at {path}")
            continue

        p = api_service.add_person(name, path)
        if p["ok"]:
            print(f"   ✓ Cloud OK: {name}")
            save_local_backup(name, path)
        else:
            print(f"   X Cloud Fail: {p['error']}")

    print("\n>>> IMPORT COMPLETE!")


def delete_all_local_faces():
    """
    Deletes all images in the managed_faces folder.
    Returns the number of deleted files, or -1 on error.
    """
    try:
        if not os.path.exists(config.DB_FOLDER):
            print(f"Folder {config.DB_FOLDER} does not exist.")
            return 0

        files = os.listdir(config.DB_FOLDER)
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

        deleted_count = 0
        for file in image_files:
            file_path = os.path.join(config.DB_FOLDER, file)
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted: {file}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {file}: {e}")

        print(f"\n>>> Deleted {deleted_count}/{len(image_files)} images from {config.DB_FOLDER}")
        return deleted_count

    except Exception as e:
        print(f"❌ Error deleting files: {e}")
        return -1


def delete_local_face_by_name(name):
    """
    Deletes an image of a person by name from the managed_faces folder.
    Returns True on success, False if not found or on error.
    """
    try:
        if not os.path.exists(config.DB_FOLDER):
            print(f"Folder {config.DB_FOLDER} does not exist.")
            return False

        # Create safe filename as used during saving
        safe_filename = "".join([c for c in name if c.isalnum() or c in (' ', '-', '_')]).strip()

        # Check for different extensions
        for ext in ['.jpg', '.jpeg', '.png']:
            file_path = os.path.join(config.DB_FOLDER, f"{safe_filename}{ext}")
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Deleted local backup: {file_path}")
                return True

        print(f"❌ Image of '{name}' not found in the local folder.")
        return False

    except Exception as e:
        print(f"❌ Error deleting file: {e}")
        return False


def delete_person_from_cloud_by_name(name):
    """
    Deletes a person from the Cloud by name.
    Returns True on success, False if not found.
    """
    try:
        people = api_service.get_all_subjects()

        if not people:
            print("Cloud currently has no data.")
            return False

        # Find person by name (case-insensitive)
        name_lower = name.lower().strip()
        for p in people:
            person_name = p.get("name", "").lower().strip()
            if person_name == name_lower:
                pid = p.get("id") or p.get("uuid")
                if api_service.delete_person_by_uuid(pid):
                    print(f"✅ Deleted '{name}' from Cloud (ID: {pid})")
                    return True

        print(f"❌ '{name}' not found in the Cloud.")
        return False

    except Exception as e:
        print(f"❌ Error deleting from Cloud: {e}")
        return False


def delete_attendance_records_by_name(name):
    """
    Deletes all attendance records for a person from the Excel file.
    Returns the number of deleted records.
    """
    file_path = "diemdanh.xlsx"

    try:
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return 0

        df = pd.read_excel(file_path)

        if 'Name' not in df.columns:
            print("Excel file is missing the 'Name' column.")
            return 0

        # Count initial records
        initial_count = len(df)

        # Delete rows with matching name (case-insensitive)
        df = df[df['Name'].str.lower().str.strip() != name.lower().strip()]

        # Count deleted records
        deleted_count = initial_count - len(df)

        # Save the file
        df.to_excel(file_path, index=False)

        print(f"🗑️ Deleted {deleted_count} attendance records for '{name}'")
        return deleted_count

    except Exception as e:
        print(f"❌ Error deleting attendance records: {e}")
        return -1


def delete_all_attendance_records():
    """
    Deletes all attendance records (wipes the file or creates a new empty one).
    Returns the number of records deleted.
    """
    file_path = "diemdanh.xlsx"

    try:
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return 0

        df = pd.read_excel(file_path)
        record_count = len(df)

        # Create an empty DataFrame with the same columns
        empty_df = pd.DataFrame(columns=['Name', 'Time'])
        empty_df.to_excel(file_path, index=False)

        print(f"🗑️ Deleted all {record_count} attendance records.")
        return record_count

    except Exception as e:
        print(f"❌ Error deleting attendance records: {e}")
        return -1


def smart_sync_uploaded_files_with_cloud(uploaded_files, threshold=0.85):
    """
    Smart sync that uses face recognition instead of filename matching.

    Logic:
    1. For each uploaded file, check if the face exists in Cloud (using face recognition)
    2. If face exists in Cloud → Keep it (mark as "found")
    3. If face doesn't exist in Cloud → Add it (register new person)
    4. Delete any Cloud faces that were NOT matched by any uploaded file

    Args:
        uploaded_files: List of uploaded file objects from Streamlit
        threshold: Face matching confidence threshold (default 0.85)

    Returns:
        dict: {
            "added": int,           # Number of new faces added
            "kept": int,            # Number of existing faces kept
            "deleted": int,         # Number of faces deleted
            "errors": list          # List of error messages
        }
    """

    results = {
        "added": 0,
        "kept": 0,
        "deleted": 0,
        "errors": []
    }

    # Step 1: Get all current people in Cloud
    cloud_people = api_service.get_all_subjects()
    if not cloud_people:
        cloud_people = []

    # Track which Cloud IDs were matched (to keep)
    matched_cloud_ids = set()

    # Step 2: Process each uploaded file
    for file in uploaded_files:
        try:
            # Get filename without extension as the name
            name = Path(file.name).stem
            image_bytes = file.getvalue()

            print(f"Processing: {name}")

            # Step 2a: Check if this face already exists in Cloud
            recognition_result = api_service.recognize_face(image_bytes, threshold=threshold)

            if recognition_result["ok"] and recognition_result["raw"]:
                # Face found in Cloud!
                matches = recognition_result["raw"]

                if len(matches) > 0:
                    best_match = matches[0]
                    confidence = best_match.get("confidence", 0)
                    cloud_name = best_match.get("name", "")
                    cloud_id = best_match.get("id") or best_match.get("uuid")

                    print(f"  ✅ Face matched to '{cloud_name}' (confidence: {confidence:.2f})")

                    # Mark this Cloud ID as "keep" (don't delete)
                    matched_cloud_ids.add(cloud_id)
                    results["kept"] += 1
                    continue

            # Step 2b: Face not found in Cloud → Add it as new person
            print(f"  ➕ Face not found, adding as new person: {name}")

            add_result = api_service.add_person(
                name=name,
                image_input=image_bytes,
                skip_duplicate_check=True  # We already checked with recognize_face
            )

            if add_result["ok"]:
                print(f"  ✅ Successfully added '{name}' to Cloud")
                results["added"] += 1
            else:
                error_msg = f"Failed to add '{name}': {add_result.get('error', 'Unknown error')}"
                print(f"  ❌ {error_msg}")
                results["errors"].append(error_msg)

        except Exception as e:
            error_msg = f"Error processing '{file.name}': {str(e)}"
            print(f"❌ {error_msg}")
            results["errors"].append(error_msg)

    # Step 3: Delete Cloud faces that were NOT matched by any uploaded file
    print(f"\nChecking for faces to delete...")
    print(f"Total Cloud people: {len(cloud_people)}")
    print(f"Matched IDs: {len(matched_cloud_ids)}")

    for person in cloud_people:
        person_id = person.get("id") or person.get("uuid")
        person_name = person.get("name", "Unknown")

        if person_id not in matched_cloud_ids:
            # This person was NOT matched by any uploaded file → DELETE
            print(f"  🗑️ Deleting '{person_name}' (ID: {person_id})")

            if api_service.delete_person_by_uuid(person_id):
                print(f"  ✅ Successfully deleted '{person_name}'")
                results["deleted"] += 1
            else:
                error_msg = f"Failed to delete '{person_name}'"
                print(f"  ❌ {error_msg}")
                results["errors"].append(error_msg)

    # Summary
    print(f"\n=== SYNC COMPLETE ===")
    print(f"✅ Added: {results['added']} new faces")
    print(f"✅ Kept: {results['kept']} existing faces")
    print(f"🗑️ Deleted: {results['deleted']} faces")
    if results['errors']:
        print(f"❌ Errors: {len(results['errors'])}")

    return results


import google_sheet_manager


# Add these functions to data_manager.py

def log_attendance_google_sheets(name):
    """
    Log attendance to Google Sheets

    Args:
        name: Name of the person

    Returns:
        tuple: (success, timestamp_string)
    """
    manager = google_sheet_manager.get_sheets_manager()

    if not manager.is_connected():
        return False, "Not connected to Google Sheets"

    success, message, timestamp = manager.log_attendance(name)

    if success:
        return True, timestamp
    else:
        return False, message


def get_attendance_records_from_sheets():
    """
    Get all attendance records from Google Sheets

    Returns:
        pandas.DataFrame or None
    """
    manager = google_sheet_manager.get_sheets_manager()

    if not manager.is_connected():
        return None

    return manager.get_all_records()


def delete_all_attendance_records_sheets():
    """
    Delete all attendance records from Google Sheets

    Returns:
        int: Number of records deleted, or -1 on error
    """
    manager = google_sheet_manager.get_sheets_manager()

    if not manager.is_connected():
        return -1

    success, count = manager.delete_all_records()

    if success:
        return count
    else:
        return -1


def delete_attendance_records_by_name_sheets(name):
    """
    Delete attendance records for a specific person from Google Sheets

    Args:
        name: Name of the person

    Returns:
        int: Number of records deleted, or -1 on error
    """
    manager = google_sheet_manager.get_sheets_manager()

    if not manager.is_connected():
        return -1

    success, count = manager.delete_records_by_name(name)

    if success:
        return count
    else:
        return -1