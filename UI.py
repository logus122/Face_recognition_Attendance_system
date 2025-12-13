import streamlit as st
import data_manager
import api_service
import pandas as pd
from io import BytesIO
import os
from pathlib import Path
import google_sheet_manager

st.set_page_config(
    page_title="Attendance System",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'sheets_connected' not in st.session_state:
    st.session_state.sheets_connected = False
if 'sheets_url' not in st.session_state:
    st.session_state.sheets_url = ""
if 'use_google_sheets' not in st.session_state:
    st.session_state.use_google_sheets = False
if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = False

# CSS styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white; 
    }
    .stMarkdown, .stSubheader, .stTitle, .stExpander, .stTextInput > div > label, .stFileUploader label, .stSelectbox label {
        color: white !important; 
    }
    .stTextInput > div > div > input, .stFileUploader > div > div, .stSelectbox > div > div > div {
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        border: 1px solid #444;
        border-radius: 5px;
    }
    .stButton > button {
        color: white;
        background-color: #2c5364;
        border: none;
    }
    .streamlit-expanderHeader {
        color: white !important;
    }
    video {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        background-color: black !important;
        border: 2px solid #2c5364 !important;
        border-radius: 10px !important;
    }
    [data-testid="stCameraInput"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
        padding: 10px !important;
        border-radius: 10px !important;
    }
    [data-testid="stCameraInput"] button {
        background-color: #2c5364 !important;
        color: white !important;
        border: 1px solid white !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
        cursor: pointer !important;
        z-index: 1000 !important;
    }
    [data-testid="stCameraInput"] button:hover {
        background-color: #3d6475 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 ATTENDANCE SYSTEM")

# ==================== INSTRUCTIONS BUTTON ====================
if st.button("📖 Instructions", use_container_width=True, key="instruction_btn"):
    st.session_state.show_instructions = not st.session_state.show_instructions

if st.session_state.show_instructions:
    st.markdown("---")
    st.markdown("### 📖 How to Use This System")

    with st.expander("🔧 **1. Initial Setup - Google Sheets Configuration**", expanded=True):
        st.markdown("""
        **Before using the system, you MUST set up Google Sheets:**

        **Step 1: Create Google Cloud Service Account**
        - Go to [Google Cloud Console](https://console.cloud.google.com/)
        - Create a new project (e.g., "Attendance System")
        - Enable "Google Sheets API" and "Google Drive API"
        - Create a Service Account
        - Download the JSON key file

        **Step 2: Set Up Your Google Sheet**
        - Create a new Google Sheet or use existing one
        - Share it with your service account email (found in JSON: `client_email`)
        - Give "Editor" permission
        - Copy the Google Sheet URL

        **Step 3: Connect in This App**
        - Select "☁️ Google Sheets" as storage method
        - Paste your Google Sheets URL
        - Click "🔗 Connect to Google Sheets"
        - Wait for "✅ Connected" status

        💡 **Note:** Without Google Sheets connection, attendance will NOT be saved permanently!
        """)

    with st.expander("📝 **2. Registering New People**"):
        st.markdown("""
        **Two ways to register a person:**

        **Method A: Register via Camera** 📷
        1. Click "📷 Register via Camera"
        2. Enter the person's name
        3. Click "Take photo" and capture their face
        4. Click "Submit"
        5. System saves face to Cloud AI

        **Method B: Register via Image** 🖼️
        1. Click "🖼️ Register via Image"
        2. Enter the person's name
        3. Upload a clear photo of their face
        4. Click "Submit"
        5. System saves face to Cloud AI

        **✅ Best Practices:**
        - Use clear, well-lit photos
        - Face should be clearly visible
        - One person per photo
        - Look directly at camera
        - Remove glasses/masks if possible
        """)

    with st.expander("🔍 **3. Marking Attendance (Face Recognition)**"):
        st.markdown("""
        **How to mark attendance:**

        1. Click "▶️ Start Recognition"
        2. Adjust "Confidence Threshold" slider:
           - **85-90%**: Recommended (balanced)
           - **70-80%**: More lenient (may have false positives)
           - **90-100%**: Strict (may miss some people)
        3. Click "Take a photo to recognize"
        4. System will:
           - Recognize the face using AI
           - Show the person's name
           - Automatically log to Google Sheets with timestamp
        5. Click "⏹️ Stop Recognition" when done

        **What gets logged:**
        - Name of person
        - Date (YYYY-MM-DD)
        - Time (HH:MM:SS)
        - Full timestamp
        """)

    with st.expander("👁️ **4. Viewing Attendance Records**"):
        st.markdown("""
        **To view attendance data:**

        1. Click "👁️ View Records"
        2. System displays:
           - Total check-ins
           - Number of unique people
           - Full attendance table
        3. Data is loaded from your Google Sheets in real-time

        **You can also:**
        - Open your Google Sheet directly in browser
        - Use Google Sheets features (filter, sort, charts)
        - Share with other people
        - Access from any device
        """)

    with st.expander("🔄 **5. Smart Sync Feature**"):
        st.markdown("""
        **What is Smart Sync?**
        - Synchronizes Cloud database with uploaded images using AI face recognition
        - Keeps Cloud updated with current roster
        - Removes people who left

        **How to use:**
        1. Click "🔄 Smart Sync with Uploaded Files"
        2. Adjust "Face Matching Confidence" (85% recommended)
        3. Upload ALL images of people who should be in the system
        4. Click "✅ Start Smart Sync"

        **What happens:**
        - ✅ **Keeps** faces that match uploaded images
        - ➕ **Adds** new faces not in Cloud
        - 🗑️ **Deletes** faces not matched (people who left)

        **Example:**
        - Cloud has: Alice, Bob, Charlie
        - You upload: alice.jpg, bob.jpg, david.jpg
        - Result: Alice ✅, Bob ✅, David ➕, Charlie 🗑️
        """)

    with st.expander("☁️ **6. View Cloud Database**"):
        st.markdown("""
        **To see who is registered:**

        1. Click "☁️ View Cloud Database"
        2. System shows list of all registered people
        3. Each entry shows:
           - Person's name
           - Unique ID

        This shows who can be recognized by the system.
        """)

    with st.expander("🗑️ **7. Delete Operations**"):
        st.markdown("""
        **Delete by Name:**
        1. Click "❌ Delete by Name"
        2. Enter the person's name (exact match)
        3. Choose what to delete:
           - **Delete from Cloud**: Removes from AI system
           - **Delete Attendance**: Removes their attendance records from Google Sheets
           - **Delete Everything**: Both Cloud + Attendance

        **Delete All (Cloud):**
        - Removes all registered faces from AI system
        - ⚠️ Cannot be undone!

        **Delete All Attendance Records:**
        - Clears all attendance data from Google Sheets
        - Keeps registered faces
        - ⚠️ Cannot be undone!

        **💣 DELETE EVERYTHING:**
        - Removes ALL data (Cloud + Attendance)
        - ⚠️⚠️⚠️ Use with extreme caution!
        """)

    with st.expander("⚠️ **Important Notes & Troubleshooting**"):
        st.markdown("""
        **✅ Remember:**
        - Google Sheets connection is REQUIRED for attendance logging
        - Cloud faces are permanent (on Luxand servers)
        - Face recognition uses AI (not 100% accurate)

        **Common Issues:**

        **"Cannot recognize face"**
        - Lower the confidence threshold
        - Use better lighting
        - Make sure face is clearly visible
        - Person might not be registered

        **"Not connected to Google Sheets"**
        - Click "🔗 Connect to Google Sheets"
        - Check that sheet is shared with service account
        - Verify URL is correct

        **"Face already exists"**
        - System detected duplicate face
        - Person is already registered
        - Use different photo or adjust confidence

        **Camera not working:**
        - Allow browser camera permission
        - Use "Register via Image" instead
        - Check if camera works on other sites

        **Need Help?**
        - Contact: Waifu group, 25TNT1
        - HCMUS, VNU-HCM
        """)

    st.markdown("---")
    if st.button("✖️ Close Instructions", use_container_width=True):
        st.session_state.show_instructions = False
        st.rerun()

# ==================== GOOGLE SHEETS SETUP SECTION ====================
st.markdown("---")
st.subheader("📊 Storage Configuration")

storage_col1, storage_col2 = st.columns([2, 1])

with storage_col1:
    storage_type = st.radio(
        "Choose storage method:",
        ["☁️ Google Sheets (Recommended)"],
        index=0,
        horizontal=True
    )
    st.session_state.use_google_sheets = True

with storage_col2:
    if st.session_state.sheets_connected:
        st.success("✅ Connected")
    else:
        st.warning("⚠️ Not Connected")

# Google Sheets Configuration
with st.expander("🔧 Google Sheets Setup", expanded=not st.session_state.sheets_connected):
    st.markdown("""
    **Quick Setup:**
    1. Create a Google Sheet
    2. Share it with your service account email
    3. Paste the sheet URL below
    4. Click Connect

    💡 See Instructions above for detailed setup guide
    """)

    sheets_url_input = st.text_input(
        "Google Sheets URL:",
        value=st.session_state.sheets_url,
        placeholder="https://docs.google.com/spreadsheets/d/..."
    )

    col_connect, col_disconnect = st.columns(2)

    with col_connect:
        if st.button("🔗 Connect to Google Sheets", use_container_width=True):
            if not sheets_url_input:
                st.error("❌ Please enter a Google Sheets URL")
            else:
                with st.spinner("Connecting..."):
                    success, message = google_sheet_manager.setup_google_sheets_from_streamlit()

                    if not success:
                        st.error(message)
                        st.info("💡 Make sure GOOGLE_SHEETS_CREDENTIALS is set in Streamlit secrets")
                    else:
                        manager = google_sheet_manager.get_sheets_manager()
                        success, message = manager.open_sheet_by_url(sheets_url_input)

                        if success:
                            st.session_state.sheets_connected = True
                            st.session_state.sheets_url = sheets_url_input
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                            st.info("💡 Make sure the sheet is shared with your service account")

    with col_disconnect:
        if st.button("🔌 Disconnect", use_container_width=True):
            st.session_state.sheets_connected = False
            st.session_state.sheets_url = ""
            st.info("Disconnected from Google Sheets")
            st.rerun()

# ==================== REGISTER SECTION ====================
st.markdown("---")
st.subheader("📝 Register")

if 'show_camera_form' not in st.session_state:
    st.session_state.show_camera_form = False
if "show_upload_form" not in st.session_state:
    st.session_state.show_upload_form = False

col1, col2 = st.columns(2)

with col1:
    if st.button("📷 Register via Camera", use_container_width=True, key="reg_camera_btn"):
        st.session_state.show_camera_form = True
        st.session_state.show_upload_form = False

with col2:
    if st.button("🖼️ Register via Image", use_container_width=True, key="reg_image_btn"):
        st.session_state.show_upload_form = True
        st.session_state.show_camera_form = False

# Register via Camera Form
if st.session_state.show_camera_form:
    st.markdown("#### Register via Camera")
    name = st.text_input("Name:", key="camera_name").strip()
    image = st.camera_input("Take photo")

    if st.button('Submit', key="camera_submit"):
        if image is None:
            st.error("Please provide a valid image.")
        elif name == "":
            st.error("Please enter a valid name.")
        else:
            with st.spinner("Sending to Cloud..."):
                try:
                    image_bytes = image.getvalue()
                    response = api_service.add_person(name, image_bytes)

                    if response["ok"]:
                        st.success(f"✅ Successfully added '{name}' to Cloud!")
                        st.session_state.show_camera_form = False
                        st.rerun()
                    else:
                        st.error(f"❌ Cloud Error: {response.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Exception: {str(e)}")

# Register via Image Form
if st.session_state.show_upload_form:
    st.markdown("#### Register via Image Upload")
    name1 = st.text_input("Name:", key="upload_name").strip()
    file = st.file_uploader("Upload file", type=["jpg", "jpeg", "png"])

    if st.button('Submit', key="upload_submit"):
        if file is None:
            st.error("Please provide a valid file.")
        elif name1 == "":
            st.error("Please enter a valid name.")
        else:
            with st.spinner("Sending to Cloud..."):
                try:
                    image_bytes = file.getvalue()
                    response = api_service.add_person(name1, image_bytes)

                    if response["ok"]:
                        st.success(f"✅ Successfully added '{name1}' to Cloud!")
                        st.session_state.show_upload_form = False
                        st.rerun()
                    else:
                        st.error(f"❌ Cloud Error: {response.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Exception: {str(e)}")

# ==================== RECOGNITION SECTION ====================
st.markdown("---")
st.subheader("🔍 Recognition")

if st.button("▶️ Start Recognition", use_container_width=True, key="start_recog_btn"):
    st.session_state.recog = True

if st.session_state.get("recog", False):
    st.markdown("#### Face Recognition")

    recognition_threshold = st.slider(
        "Confidence Threshold (%)",
        min_value=70,
        max_value=100,
        value=85,
        step=5,
        format="%d%%",
        help="Recommended: 85%. Higher = stricter matching."
    )
    current_threshold = recognition_threshold / 100.0

    st.markdown("---")
    image = st.camera_input("Take a photo to recognize", key="recog_cam")

    if image is not None:
        st.write("Recognizing...")
        image_bytes = image.getvalue()
        r = api_service.recognize_face(image_bytes, threshold=current_threshold)

        if not r["ok"]:
            st.error("Cloud error: " + r.get("error", "unknown"))
        else:
            results = r["raw"]

            if not isinstance(results, list) or len(results) == 0:
                st.warning("Cannot recognize / Face is below threshold.")
            else:
                p = results[0]
                name = p.get("name")
                confidence = p.get("confidence", 0)

                if not name:
                    st.warning("Unknown / Not registered")
                else:
                    st.success(f"✅ Found: {name} (Confidence: {confidence:.2f})")

                    # Log to Google Sheets
                    if st.session_state.sheets_connected:
                        ok, time_str = data_manager.log_attendance_google_sheets(name)
                        if ok:
                            st.info(f"☁️ Logged to Google Sheets: {name}")
                            st.info(f"Time: {time_str}")
                        else:
                            st.error(f"Error: {time_str}")
                    else:
                        st.warning("⚠️ Not connected to Google Sheets. Attendance not saved!")
                        st.info("Please connect to Google Sheets in Storage Configuration")

    if st.button("⏹️ Stop Recognition", key="stop_recog_btn"):
        st.session_state.recog = False
        st.rerun()

# ==================== VIEW RECORDS SECTION ====================
st.markdown("---")
st.subheader("📊 View Attendance Records")

if st.button("👁️ View Records", use_container_width=True, key="view_records_btn"):
    if st.session_state.sheets_connected:
        df = data_manager.get_attendance_records_from_sheets()

        if df is None or len(df) == 0:
            st.info("No attendance records found in Google Sheets.")
        else:
            st.write(f"**Total Records:** {len(df)}")

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Check-ins", len(df))
            with col_b:
                unique_people = df['Name'].nunique() if 'Name' in df.columns else 0
                st.metric("Unique People", unique_people)

            st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ Not connected to Google Sheets")
        st.info("Please connect to Google Sheets to view records")

# ==================== DELETE SECTION ====================
st.markdown("---")
st.subheader("🗑️ Delete")

if "show_delete_name_form" not in st.session_state:
    st.session_state.show_delete_name_form = False

col1, col2 = st.columns(2)

with col1:
    if st.button("❌ Delete by Name", use_container_width=True, key="show_delete_name_btn"):
        st.session_state.show_delete_name_form = True

with col2:
    if st.button("⚠️ Delete All (Cloud)", use_container_width=True, key="delete_all_cloud_btn_main"):
        st.warning("Deleting all faces from Cloud...")
        people = api_service.get_all_subjects()

        if not people:
            st.info("No data in Cloud.")
        else:
            deleted = 0
            for p in people:
                pid = p.get("id") or p.get("uuid")
                if api_service.delete_person_by_uuid(pid):
                    deleted += 1
            st.success(f"✅ Successfully deleted all {deleted} people from Cloud!")

st.markdown("---")

col_x, col_y = st.columns(2)

with col_x:
    if st.button("📋 Delete All Attendance Records", use_container_width=True, key="delete_all_attendance_btn"):
        if st.session_state.sheets_connected:
            deleted_count = data_manager.delete_all_attendance_records_sheets()

            if deleted_count > 0:
                st.success(f"✅ Deleted {deleted_count} records from Google Sheets!")
            elif deleted_count == 0:
                st.info("No Attendance Records to delete.")
            else:
                st.error("❌ Error while deleting.")
        else:
            st.warning("⚠️ Not connected to Google Sheets")

with col_y:
    if st.button("💣 DELETE EVERYTHING", use_container_width=True, type="primary", key="delete_everything_btn"):
        # Delete from Cloud
        people = api_service.get_all_subjects()
        cloud_deleted = 0
        if people:
            for p in people:
                pid = p.get("id") or p.get("uuid")
                if api_service.delete_person_by_uuid(pid):
                    cloud_deleted += 1

        # Delete attendance records from Google Sheets
        attendance_deleted = 0
        if st.session_state.sheets_connected:
            attendance_deleted = data_manager.delete_all_attendance_records_sheets()

        st.success(f"🗑️ Everything deleted:")
        st.info(f"- Cloud: {cloud_deleted} people")
        st.info(f"- Attendance: {attendance_deleted} records")

# Delete by Name Form
if st.session_state.show_delete_name_form:
    st.markdown("#### Delete Face by Name")

    delete_name = st.text_input("Enter name to delete:", key="delete_name_input").strip()

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🗑️ Delete from Cloud", key="delete_cloud_btn"):
            if delete_name == "":
                st.error("Please enter a name.")
            else:
                success = data_manager.delete_person_from_cloud_by_name(delete_name)
                if success:
                    st.success(f"✅ Deleted '{delete_name}' from Cloud!")
                else:
                    st.error(f"❌ Cannot find '{delete_name}' in Cloud.")

    with col_b:
        if st.button("📋 Delete Attendance", key="delete_attendance_btn"):
            if delete_name == "":
                st.error("Please enter a name.")
            else:
                if st.session_state.sheets_connected:
                    deleted_count = data_manager.delete_attendance_records_by_name_sheets(delete_name)
                    if deleted_count > 0:
                        st.success(f"✅ Deleted {deleted_count} records of '{delete_name}'!")
                    elif deleted_count == 0:
                        st.info(f"No records found for '{delete_name}'.")
                    else:
                        st.error("❌ Error while deleting.")
                else:
                    st.warning("⚠️ Not connected to Google Sheets")

    st.markdown("---")

    if st.button("🗑️ Delete Everything (Cloud + Attendance)", key="delete_all_person", type="primary"):
        if delete_name == "":
            st.error("Please enter a name.")
        else:
            cloud_success = data_manager.delete_person_from_cloud_by_name(delete_name)

            attendance_count = 0
            if st.session_state.sheets_connected:
                attendance_count = data_manager.delete_attendance_records_by_name_sheets(delete_name)

            results = []
            if cloud_success:
                results.append("✅ Cloud")
            if attendance_count > 0:
                results.append(f"✅ {attendance_count} attendance records")

            if results:
                st.success(f"Deleted '{delete_name}' from: {', '.join(results)}")
            else:
                st.warning(f"Cannot find '{delete_name}' anywhere.")

    if st.button("❌ Cancel", key="cancel_delete"):
        st.session_state.show_delete_name_form = False
        st.rerun()

# ==================== SYNC SECTION ====================
st.markdown("---")
st.subheader("🔄 Smart Sync (Face Recognition)")

col_sync1, col_sync2 = st.columns(2)

with col_sync1:
    if st.button("🔄 Smart Sync with Uploaded Files", use_container_width=True, key="sync_folder_btn"):
        st.session_state.show_sync_form = True

with col_sync2:
    if st.button("☁️ View Cloud Database", use_container_width=True, key="view_cloud_db_btn"):
        people = api_service.get_all_subjects()

        if not people:
            st.info("Cloud database is empty. No faces registered yet.")
        else:
            st.success(f"Found {len(people)} people in Cloud:")

            for idx, person in enumerate(people, 1):
                name = person.get("name", "Unknown")
                person_id = person.get("id") or person.get("uuid")
                st.write(f"{idx}. **{name}** (ID: {person_id})")

if "show_sync_form" not in st.session_state:
    st.session_state.show_sync_form = False

if st.session_state.show_sync_form:
    st.markdown("---")
    st.markdown("#### 🔄 Smart Sync with Face Recognition")

    st.info("""
    **How Smart Sync Works:**
    1. 🔍 Each uploaded image is checked against Cloud using AI
    2. ✅ If face is recognized in Cloud, it stays
    3. ➕ If face is NOT in Cloud, it's registered as new person
    4. 🗑️ Cloud faces NOT matched by any upload are deleted
    """)

    sync_threshold = st.slider(
        "Face Matching Confidence (%)",
        min_value=70,
        max_value=95,
        value=85,
        step=5,
        format="%d%%",
        help="Higher = stricter matching"
    )

    uploaded_files = st.file_uploader(
        "Upload ALL face images to sync:",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="sync_file_uploader"
    )

    if uploaded_files:
        st.success(f"📁 {len(uploaded_files)} files uploaded")

    st.warning("⚠️ This will DELETE any Cloud faces not matched by uploaded images!")

    col_s1, col_s2 = st.columns([1, 4])

    with col_s1:
        if st.button("✅ Start Smart Sync", key="confirm_sync_btn", type="primary"):
            if not uploaded_files:
                st.error("❌ Please upload at least one image file.")
            else:
                with st.spinner(f"🔄 Processing {len(uploaded_files)} files..."):
                    from data_manager import smart_sync_uploaded_files_with_cloud

                    results = smart_sync_uploaded_files_with_cloud(
                        uploaded_files,
                        threshold=sync_threshold / 100.0
                    )

                    st.markdown("---")
                    st.markdown("### 📊 Sync Results")

                    col_r1, col_r2, col_r3 = st.columns(3)

                    with col_r1:
                        st.metric("➕ Added", results["added"])
                    with col_r2:
                        st.metric("✅ Kept", results["kept"])
                    with col_r3:
                        st.metric("🗑️ Deleted", results["deleted"])

                    if results["errors"]:
                        st.error(f"⚠️ {len(results['errors'])} errors occurred:")
                        for error in results["errors"]:
                            st.write(f"- {error}")
                    else:
                        st.success("✅ Sync completed successfully!")

                st.session_state.show_sync_form = False

    with col_s2:
        if st.button("❌ Cancel", key="cancel_sync_btn"):
            st.info("Sync canceled.")
            st.session_state.show_sync_form = False
            st.rerun()

# ==================== FOOTER SECTION ====================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: white; padding: 10px; font-size: 0.8em; line-height: 1.5;'>
        © 2025 Attendance System - Developed with Streamlit<br>
        Developed by: Waifu group, 25TNT1 <br>
        HCMUS, VNU-HCM
    </div>
""", unsafe_allow_html=True)