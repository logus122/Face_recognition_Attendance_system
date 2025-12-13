import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import json
import streamlit as st


class GoogleSheetsManager:
    """Manages Google Sheets integration for attendance logging"""

    def __init__(self):
        self.client = None
        self.sheet = None
        self.worksheet = None

    def connect_with_credentials(self, credentials_dict):
        """
        Connect to Google Sheets using service account credentials

        Args:
            credentials_dict: Dictionary containing service account credentials
        """
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]

            creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
            self.client = gspread.authorize(creds)
            return True, "✅ Connected to Google Sheets successfully!"
        except Exception as e:
            return False, f"❌ Connection failed: {str(e)}"

    def open_sheet_by_url(self, sheet_url):
        """
        Open a Google Sheet by URL

        Args:
            sheet_url: Full URL of the Google Sheet
        """
        try:
            self.sheet = self.client.open_by_url(sheet_url)
            # Use first worksheet by default
            self.worksheet = self.sheet.sheet1

            # Initialize headers if sheet is empty
            if len(self.worksheet.get_all_values()) == 0:
                self.worksheet.append_row(['Name', 'Date', 'Time', 'Timestamp'])

            return True, f"✅ Opened sheet: {self.sheet.title}"
        except Exception as e:
            return False, f"❌ Failed to open sheet: {str(e)}"

    def log_attendance(self, name):
        """
        Log attendance to Google Sheets

        Args:
            name: Name of the person

        Returns:
            tuple: (success, message, timestamp)
        """
        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

            # Append new row
            self.worksheet.append_row([name, date_str, time_str, timestamp_str])

            return True, f"✅ Attendance logged for {name}", timestamp_str
        except Exception as e:
            return False, f"❌ Failed to log attendance: {str(e)}", None

    def get_all_records(self):
        """
        Get all attendance records from Google Sheets

        Returns:
            pandas.DataFrame or None
        """
        try:
            records = self.worksheet.get_all_records()
            if not records:
                return None
            return pd.DataFrame(records)
        except Exception as e:
            print(f"Error reading records: {e}")
            return None

    def delete_all_records(self):
        """
        Delete all attendance records (keeps header row)

        Returns:
            tuple: (success, count)
        """
        try:
            all_values = self.worksheet.get_all_values()
            if len(all_values) <= 1:  # Only header or empty
                return True, 0

            # Delete all rows except header
            num_rows = len(all_values)
            if num_rows > 1:
                self.worksheet.delete_rows(2, num_rows)

            return True, num_rows - 1
        except Exception as e:
            print(f"Error deleting records: {e}")
            return False, -1

    def delete_records_by_name(self, name):
        """
        Delete all attendance records for a specific person

        Args:
            name: Name of the person

        Returns:
            tuple: (success, count)
        """
        try:
            all_values = self.worksheet.get_all_values()
            if len(all_values) <= 1:
                return True, 0

            # Find rows to delete (from bottom to top to avoid index shifting)
            rows_to_delete = []
            for idx, row in enumerate(all_values[1:], start=2):  # Start from row 2 (skip header)
                if row and row[0] == name:
                    rows_to_delete.append(idx)

            # Delete rows from bottom to top
            for row_idx in reversed(rows_to_delete):
                self.worksheet.delete_rows(row_idx)

            return True, len(rows_to_delete)
        except Exception as e:
            print(f"Error deleting records: {e}")
            return False, -1

    def is_connected(self):
        """Check if connected to a worksheet"""
        return self.worksheet is not None


# Singleton instance
_sheets_manager = GoogleSheetsManager()


def get_sheets_manager():
    """Get the global sheets manager instance"""
    return _sheets_manager


def setup_google_sheets_from_streamlit():
    """
    Setup Google Sheets connection using Streamlit secrets

    Returns:
        tuple: (success, message)
    """
    try:
        # Read credentials from Streamlit secrets
        if 'GOOGLE_SHEETS_CREDENTIALS' not in st.secrets:
            return False, "❌ Google Sheets credentials not found in secrets"

        credentials_dict = dict(st.secrets['GOOGLE_SHEETS_CREDENTIALS'])

        manager = get_sheets_manager()
        success, message = manager.connect_with_credentials(credentials_dict)

        return success, message
    except Exception as e:
        return False, f"❌ Setup failed: {str(e)}"