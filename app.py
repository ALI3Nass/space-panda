from flask import Flask, request, jsonify, render_template
from services.google_sheets_service import get_sheets_service, fetch_form_responses, process_candidates, update_sheet_with_result
from services.google_drive_service import download_cv, get_drive_service, upload_to_drive
from utils.pdf_parser import parse_pdf
from utils.scoring_algorithm import score_candidate
from config.settings import Config
import os
import shutil
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)


def fetch_candidates():
    """
    Fetches candidates from Google Sheet.
    Returns a list of candidates with their name, job_id and CV Drive URLs.
    """
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

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

    return score, matched_skills


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
    score, matched_skills = process_cv(cv_path, job_id)

    # Move to shortlisted folder if score is good enough
    result = {
        "name": cv_file.filename.replace('.pdf', ''),
        "job_id": job_id,
        "score": score,
        "matched_skills": matched_skills
    }

    if score >= 3:  # Threshold based on number of matched skills
        shortlist_path = f"shortlisted_cvs/{job_id}_{cv_file.filename}"
        shutil.copy(cv_path, shortlist_path)
        result["shortlisted"] = True
    else:
        result["shortlisted"] = False

    # Update Google Sheet with result
    try:
        update_sheet_with_result(result)
    except Exception as e:
        print(f"Error updating sheet: {str(e)}")

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
                score, matched_skills = process_cv(
                    cv_path, candidate['job_id'])

                # Add result
                result = {
                    "name": candidate['name'],
                    "job_id": candidate['job_id'],
                    "score": score,
                    "matched_skills": matched_skills
                }

                # Move to shortlisted folder if score is good enough
                if score >= 3:  # Threshold based on number of matched skills
                    os.makedirs("shortlisted_cvs", exist_ok=True)
                    shortlist_path = f"shortlisted_cvs/{candidate['job_id']}_{candidate['name'].replace(' ', '_')}.pdf"
                    shutil.copy(cv_path, shortlist_path)
                    result["shortlisted"] = True
                else:
                    result["shortlisted"] = False

                # Update Google Sheet with result
                try:
                    update_sheet_with_result(result)
                except Exception as e:
                    print(
                        f"Error updating sheet for {candidate['name']}: {str(e)}")

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
