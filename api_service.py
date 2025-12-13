import requests
import cv2
import io
import config
from pathlib import Path


# --- Helper functions ---
def _prepare_file(image_input, field):
    """
    Prepares the image input for a multi-part file POST request.

    Args:
        image_input: Image as bytes, numpy array, string URL, or local file path.
        field: The form field name Luxand expects (e.g., "photos", "photo").

    Returns:
        tuple: (files dictionary, file handler or None)
    """
    # 1. If bytes -> handle as file upload
    if isinstance(image_input, (bytes, bytearray)):
        file_obj = io.BytesIO(image_input)
        file_obj.name = "image.jpg"
        return {field: file_obj}, file_obj

    # 2. If numpy array (OpenCV image)
    if hasattr(image_input, "shape"):
        is_success, buffer = cv2.imencode(".jpg", image_input)
        if not is_success:
            raise ValueError("Failed to encode image")
        file_obj = io.BytesIO(buffer.tobytes())
        file_obj.name = "image.jpg"
        return {field: file_obj}, file_obj

    # 3. If string URL
    if isinstance(image_input, str) and image_input.startswith(("http://", "https://")):
        return {field: image_input}, None

    # 4. If string local path
    if isinstance(image_input, str):
        try:
            f = open(image_input, "rb")
            return {field: f}, f
        except FileNotFoundError:
            raise FileNotFoundError(f"Local image file not found: {image_input}")

    raise TypeError("Unsupported image_input type for _prepare_file")


# --- SIMPLIFIED REQUEST SENDER (No token rotation needed) ---
def _send_request(method, url, files=None, data=None, headers=None):
    """
    Sends a request using the permanent API key.
    No token refresh needed - Luxand uses permanent keys.
    """
    # Get the permanent API key
    current_token = config.get_current_token()

    if not current_token:
        print("❌ Failed to retrieve API Key.")
        return None

    req_headers = headers or {}
    # Send token in the 'token' Header
    req_headers["token"] = current_token

    # Reset file pointers if needed
    if files:
        for k, f in files.items():
            if hasattr(f, "seek"):
                f.seek(0)

    try:
        res = requests.request(method, url, headers=req_headers, files=files, data=data, timeout=30)

        # Log the response for debugging
        print(f"📡 {method} {url}")
        print(f"📊 Status: {res.status_code}")
        if res.status_code != 200:
            print(f"📄 Response: {res.text[:500]}")

        return res

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None


# --- PUBLIC API ---
def add_person(name, image_input, collections="", skip_duplicate_check=False):
    """
    Add a person to Luxand Cloud.

    Args:
        name: Person's name
        image_input: Image as bytes, numpy array, or file path
        collections: Collection name (optional)
        skip_duplicate_check: Skip checking for duplicates
    """

    # Check for duplicates only if not skipped
    if not skip_duplicate_check:
        try:
            # CALL RECOGNIZE_FACE with a high THRESHOLD (0.90) for accuracy
            search = recognize_face(image_input, threshold=0.90)

            # Only proceed with duplicate check if search was successful
            if search.get("ok") and isinstance(search.get("raw"), list) and len(search.get("raw", [])) > 0:
                top = search["raw"][0]

                if isinstance(top, dict):
                    confidence = top.get("confidence", 0)
                    found_name = top.get("name", "")

                    if confidence > 0.90:
                        return {
                            "ok": False,
                            "error": f"This face is similar to '{found_name}' (confidence={confidence:.2f}). Cannot register duplicate!"
                        }
        except Exception as e:
            print(f"⚠️ Warning: Duplicate check failed ({e}), proceeding with registration anyway...")

    # Proceed with registration
    files, handler = None, None
    try:
        files, handler = _prepare_file(image_input, "photos")

        res = _send_request(
            "POST",
            "https://api.luxand.cloud/v2/person",
            data={"name": name, "store": "1", "collections": collections},
            files=files
        )
    finally:
        if handler and hasattr(handler, 'close'):
            handler.close()

    if res is None:
        return {
            "ok": False,
            "error": "Network error - Could not connect to API. Check your internet connection or API key."
        }

    if res.status_code != 200:
        try:
            error_detail = res.json()
            error_msg = error_detail.get("message") or error_detail.get("error") or res.text
        except:
            error_msg = f"HTTP {res.status_code}: {res.text[:200]}"

        return {
            "ok": False,
            "error": error_msg,
            "status_code": res.status_code,
            "raw": res.text
        }

    return {"ok": True, "uuid": res.json().get("uuid"), "raw": res.json()}


def recognize_face(image_input, threshold=0.85):
    """
    Recognize a face using Luxand Cloud.

    Args:
        image_input: Image as bytes, numpy array, or file path
        threshold: Minimum confidence level (0.0 to 1.0) to consider a match.
    """
    files, handler = None, None
    try:
        files, handler = _prepare_file(image_input, "photo")

        # Build URL with threshold parameter
        base_url = "https://api.luxand.cloud/photo/search/v2"
        # Luxand API uses 'threshold' in the Query Parameter
        url_with_threshold = f"{base_url}?threshold={threshold}"

        res = _send_request(
            "POST",
            url_with_threshold,
            files=files
        )
    finally:
        if handler and hasattr(handler, 'close'):
            handler.close()

    if res is None:
        return {
            "ok": False,
            "error": "Network error - Could not connect to API. Check your internet connection or API key."
        }

    if res.status_code != 200:
        try:
            error_detail = res.json()
            error_msg = error_detail.get("message") or error_detail.get("error") or res.text
        except:
            error_msg = f"HTTP {res.status_code}: {res.text[:200]}"

        return {
            "ok": False,
            "error": error_msg,
            "status_code": res.status_code,
            "raw": res.text
        }

    return {"ok": True, "raw": res.json()}


def get_all_subjects():
    """
    Retrieves a list of all subjects (people) registered in the Cloud.
    """
    url = "https://api.luxand.cloud/subject"
    res = _send_request("GET", url)

    if res and res.status_code == 200:
        return res.json()

    return []


def delete_person_by_uuid(uuid):
    """
    Deletes a specific person (subject) from the Cloud by their UUID.
    Returns True if the deletion was successful (HTTP 200).
    """
    url = f"https://api.luxand.cloud/subject/{uuid}"
    res = _send_request("DELETE", url)
    return res and res.status_code == 200


def delete_all_people():
    """
    Deletes all registered people (subjects) from the Cloud.
    """
    people = get_all_subjects()
    if not people:
        print("Subject list is empty.")
        return

    print(f"Found {len(people)} people. Starting deletion...")
    count = 0
    for p in people:
        pid = p.get("id") or p.get("uuid")
        if pid and delete_person_by_uuid(pid):
            print(f"Deleted: {p.get('name')} (ID: {pid})")
            count += 1
    print(f"\n>>> Complete! Deleted {count} people.")