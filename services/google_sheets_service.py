from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os

# Load Google Sheets API credentials
def get_google_sheets_service():
    creds = Credentials.from_service_account_file('path/to/credentials.json')
    service = build('sheets', 'v4', credentials=creds)
    return service

# Fetch form responses from Google Sheets
def fetch_form_responses(spreadsheet_id, range_name):
    service = get_google_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    return values

# Process the fetched data to extract candidates
def process_candidates(data):
    candidates = []
    for row in data[1:]:  # Skip header row
        if len(row) >= 3:
            candidate_name = row[0]
            job_id = row[1]
            cv_link = row[2]
            candidates.append({
                'name': candidate_name,
                'job_id': job_id,
                'cv_link': cv_link
            })
    return candidates