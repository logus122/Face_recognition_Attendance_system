# 🎓 Face Recognition Attendance System

AI-powered attendance system using face recognition with Luxand Cloud API, Google Sheets storage, and Streamlit interface.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ Features

- 📷 **Face Registration** - Register via camera or image upload
- 🔍 **AI Face Recognition** - Real-time attendance marking with confidence threshold
- ☁️ **Google Sheets Integration** - Permanent cloud storage for attendance records
- 🔄 **Smart Sync** - AI-powered face synchronization with uploaded images
- 📊 **Live Dashboard** - View attendance records with statistics
- 🗑️ **Data Management** - Comprehensive delete operations
- 🎨 **Modern UI** - Beautiful gradient design with responsive interface

---

## 🚀 Demo

**Live Demo:** [Your Streamlit App URL]

**Features Demo:**
1. Click "📖 Instructions" for complete user guide
2. Connect your Google Sheets
3. Register faces via camera or image
4. Mark attendance with face recognition
5. View real-time attendance records

---

## 📋 Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- Luxand Cloud API account ([Sign up here](https://luxand.cloud))
- Google Cloud project with Sheets API enabled
- Google Sheet for attendance storage

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/attendance-system.git
cd attendance-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Luxand Cloud API

1. Sign up at [luxand.cloud](https://luxand.cloud)
2. Get your API key from the dashboard
3. Create `tokens.txt` in project root:

```bash
echo "YOUR_LUXAND_API_KEY" > tokens.txt
```

### 4. Set Up Google Sheets

**Create Service Account:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable "Google Sheets API" and "Google Drive API"
4. Create Service Account → Download JSON key

**Prepare Your Sheet:**
1. Create a Google Sheet
2. Share it with service account email (from JSON)
3. Give "Editor" permission
4. Copy the sheet URL

**Configure Locally:**

Create `.streamlit/secrets.toml`:

```toml
LUXAND_API_KEY = "your_luxand_api_key"

[GOOGLE_SHEETS_CREDENTIALS]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour key here\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### 5. Run the Application

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`

---

## 🌐 Deployment on Streamlit Cloud

### 1. Push to GitHub

Make sure `.gitignore` excludes sensitive files:
- ✅ `tokens.txt` is ignored
- ✅ `.streamlit/` is ignored
- ✅ No `.json` files committed

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Main file: `main.py`
6. Click "Advanced settings"

### 3. Add Secrets

In Streamlit Cloud settings, add:

```toml
LUXAND_API_KEY = "your_luxand_api_key"

[GOOGLE_SHEETS_CREDENTIALS]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour key\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### 4. Deploy!

Click "Deploy" and wait 2-5 minutes. Your app will be live! 🎉

---

## 📚 Usage Guide

### Register New Person

1. Click "📷 Register via Camera" or "🖼️ Register via Image"
2. Enter person's name
3. Capture/upload their photo
4. Click "Submit"
5. Face is saved to Luxand Cloud

### Mark Attendance

1. Click "▶️ Start Recognition"
2. Adjust confidence threshold (85% recommended)
3. Take photo of person
4. System recognizes face and logs to Google Sheets automatically

### View Records

1. Click "👁️ View Records"
2. See all attendance data from Google Sheets
3. View statistics (total check-ins, unique people)

### Smart Sync

1. Click "🔄 Smart Sync with Uploaded Files"
2. Upload ALL current member photos
3. System will:
   - ✅ Keep matching faces
   - ➕ Add new faces
   - 🗑️ Delete non-matching faces

### Delete Operations

- **Delete by Name**: Remove specific person
- **Delete All (Cloud)**: Clear all registered faces
- **Delete All Attendance**: Clear attendance records
- **DELETE EVERYTHING**: Nuclear option (use carefully!)

---

## 🏗️ Project Structure

```
attendance-system/
├── UI.py                     # Main Streamlit application
├── api_service.py              # Luxand Cloud API integration
├── config.py                   # Configuration & API key management
├── data_manager.py             # Data operations & Google Sheets
├── google_sheet_manager.py     # Google Sheets integration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── tokens.txt                  # API key (not committed)
```

---

## 🔧 Configuration

### Confidence Threshold

Adjust in Recognition section:
- **70-80%**: Lenient (more false positives)
- **85-90%**: Recommended (balanced)
- **90-100%**: Strict (may miss some matches)

### API Keys

- **Luxand API**: Face recognition service
- **Google Sheets**: Attendance storage

Both configured via Streamlit secrets (deployment) or local files (development).

---

## 📊 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web framework & UI |
| **Luxand Cloud** | Face recognition AI |
| **Google Sheets** | Cloud data storage |
| **Python** | Backend logic |
| **gspread** | Google Sheets API |
| **OpenCV** | Image processing |
| **Pandas** | Data manipulation |

---

## 🐛 Troubleshooting

### "Cannot recognize face"
- ✅ Lower confidence threshold
- ✅ Improve lighting
- ✅ Ensure face is clearly visible
- ✅ Check if person is registered

### "Not connected to Google Sheets"
- ✅ Verify service account email has access
- ✅ Check sheet URL is correct
- ✅ Ensure credentials are in secrets
- ✅ Confirm APIs are enabled in Google Cloud

### Camera not working
- ✅ Allow browser camera permission
- ✅ Use "Register via Image" instead
- ✅ Try different browser (Chrome recommended)

### "Face already exists"
- ✅ Person is already registered
- ✅ Use different photo
- ✅ Lower duplicate detection threshold

---

## 🔒 Security Notes

⚠️ **Never commit these files:**
- `tokens.txt` (Luxand API key)
- `.streamlit/secrets.toml` (All credentials)
- `*.json` (Service account keys)

✅ **Always use:**
- `.gitignore` to exclude sensitive files
- Streamlit secrets for deployment
- Environment variables for local development

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Credits

**Developed by:** Waifu Group, 25TNT1  
**Institution:** HCMUS, VNU-HCM  
**Year:** 2025

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Support

For support, email your-email@example.com or open an issue in this repository.

---

## 🎯 Roadmap

- [ ] Export attendance to PDF reports
- [ ] Email notifications for attendance
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Batch registration from folder

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ by Waifu Group**