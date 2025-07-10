from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os


def get_sheets_service():
    """Create and return Google Sheets service client"""
    creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    return build('sheets', 'v4', credentials=creds)


def fetch_form_responses(spreadsheet_id, range_name):
    """Fetch form responses from Google Sheets"""
    service = get_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    return values


def process_candidates(data):
    """Process the fetched data to extract candidates"""
    candidates = []
    # Skip if no data
    if not data:
        return candidates

    # Skip header row
    for row in data[1:]:
        # Ensure row has enough columns
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


def update_sheet_with_result(result):
    """Update Google Sheet with CV processing result"""
    service = get_sheets_service()
    sheet_id = os.getenv('GOOGLE_SHEET_ID')

    # Prepare data row
    row = [
        result['name'],
        result['job_id'],
        result.get('drive_url', ''),
        result['score'],
        'Yes' if result['shortlisted'] else 'No',
        ','.join(result.get('matched_skills', [])
                 if 'matched_skills' in result else [])
    ]

    # Append to sheet
    body = {
        'values': [row]
    }

    sheet_range = 'Results!A:F'  # Update to match your sheet

    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=sheet_range,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
