from flask import Flask, request, jsonify, render_template
from services.google_sheets_service import get_sheets_service, fetch_form_responses, process_candidates
from utils.pdf_parser import parse_pdf
from utils.scoring_algorithm import score_candidate, score_candidates
from config.settings import Config
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
import os
import shutil


def get_drive_service():
    """Create and return Google Drive service client"""
    creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    return build('drive', 'v3', credentials=creds)


def download_cv(file_url, destination_path):
    """
    Download CV from Google Drive using the file URL.

    Args:
        file_url: URL of the file in Google Drive
        destination_path: Full path where the file should be saved

    Returns:
        Path to the downloaded file
    """
    drive_service = get_drive_service()

    # Extract file ID from URL - handle different URL formats
    if '/d/' in file_url:
        file_id = file_url.split('/d/')[1].split('/')[0]
    else:
        file_id = file_url.split('/')[-2]  # Extract file ID from URL

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()

    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    # Ensure the directory exists
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    # Save the file
    with open(destination_path, 'wb') as f:
        f.write(fh.getbuffer())

    return destination_path


def upload_to_drive(file_path, file_name):
    """Upload file to Google Drive"""
    drive_service = get_drive_service()
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webViewLink'
    ).execute()

    return file.get('id'), file.get('webViewLink')


def get_file_metadata(file_url):
    """Get metadata of the file from Google Drive."""
    drive_service = get_drive_service()

    # Extract file ID from URL - handle different URL formats
    if '/d/' in file_url:
        file_id = file_url.split('/d/')[1].split('/')[0]
    else:
        file_id = file_url.split('/')[-2]

    file = drive_service.files().get(fileId=file_id, fields='name').execute()

    return file.get('name')


# Load .env file
load_dotenv()

app = Flask(__name__)


def fetch_candidates():
    """
    Fetches candidates from Google Sheet.
    Returns a list of candidates with their name, job_id and CV Drive URLs.
    """
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    service = get_sheets_service()
    # Fetch data from Form Responses sheet
    form_responses = fetch_form_responses(sheet_id, "Form Responses 1")
    # Process candidates from the responses
    candidates = process_candidates(form_responses)
    return candidates


def process_cv(cv_path, job_id):
    """
    Process a candidate's CV:
    1. Parse the PDF
    2. Score against required skills for the job

    Args:
        cv_path: Path to the CV file
        job_id: Job ID to match against required skills

    Returns:
        Score of the CV
    """
    # Parse PDF text
    cv_text = parse_pdf(cv_path)

    # Get required skills for this job_id
    required_skills = Config.REQUIRED_SKILLS.get(job_id, [])

    # Score the CV against required skills
    score, matched_skills = score_candidate(cv_text, required_skills)
    return score


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    """Handle single CV upload from the form"""
    job_id = request.form.get('job_id')
    cv_file = request.files.get('cv_file')
    if not cv_file or not job_id:
        return jsonify({"status": "error", "message": "Missing job ID or CV file"}), 400
    # Create directories if they don't exist
    os.makedirs("temp_cvs", exist_ok=True)
    os.makedirs("shortlisted_cvs", exist_ok=True)
    # Save the uploaded file
    cv_path = f"temp_cvs/{cv_file.filename}"
    cv_file.save(cv_path)
    # Process the CV
    score = process_cv(cv_path, job_id)
    # Move to shortlisted folder if score is good enough
    result = {
        "name": cv_file.filename.replace('.pdf', ''),
        "job_id": job_id,
        "score": score
    }
    if score >= 3:  # Threshold based on number of matched skills
        shortlist_path = f"shortlisted_cvs/{job_id}_{cv_file.filename}"
        shutil.copy(cv_path, shortlist_path)
        result["shortlisted"] = True
    else:
        result["shortlisted"] = False
    # Upload to Google Drive
    file_id, file_url = upload_to_drive(
        cv_path, f"{job_id}_{cv_file.filename}")
    result["drive_file_id"] = file_id
    result["drive_url"] = file_url
    return jsonify(result)


@app.route('/process_cvs', methods=['POST'])
def process_cvs():
    """Process all candidates from the Google Sheet"""
    try:
        # Fetch candidates from Google Sheet
        candidates = fetch_candidates()
        if not candidates:
            return jsonify({"status": "error", "message": "No candidates found in sheet"}), 404
        results = []
        for candidate in candidates:
            # Download CV
            cv_path = f"temp_cvs/{candidate['name'].replace(' ', '_')}.pdf"
            os.makedirs("temp_cvs", exist_ok=True)
            try:
                download_cv(candidate['cv_link'], cv_path)
                # Process the CV
                score = process_cv(cv_path, candidate['job_id'])
                # Add result
                result = {
                    "name": candidate['name'],
                    "job_id": candidate['job_id'],
                    "score": score
                }
                # Move to shortlisted folder if score is good enough
                if score >= 3:  # Threshold based on number of matched skills
                    os.makedirs("shortlisted_cvs", exist_ok=True)
                    shortlist_path = f"shortlisted_cvs/{candidate['job_id']}_{candidate['name'].replace(' ', '_')}.pdf"
                    shutil.copy(cv_path, shortlist_path)
                    result["shortlisted"] = True
                else:
                    result["shortlisted"] = False

                results.append(result)

            except Exception as e:
                print(f"Error processing {candidate['name']}: {str(e)}")
                results.append({
                    "name": candidate['name'],
                    "job_id": candidate['job_id'],
                    "score": 0,
                    "error": str(e)
                })

        return jsonify(results)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
