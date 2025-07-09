from flask import Flask, request, jsonify, render_template  # Added render_template
from services.google_sheets_service import process_candidates  # Updated import
from services.google_drive_service import download_cv
from services.cv_processing_service import CVProcessingService
from utils.pdf_parser import parse_pdf
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')  # Serve the index.html template


@app.route('/shortlist', methods=['GET'])
def shortlist_candidates():
    candidates = fetch_candidates()
    shortlisted = {}

    for candidate in candidates:
        job_id = candidate['job_id']
        cv_link = candidate['cv_link']
        name = candidate['name']

        # Download CV
        cv_file_path = download_cv(cv_link)

        # Process CV and score
        score = process_cv(cv_file_path, job_id)

        if job_id not in shortlisted:
            shortlisted[job_id] = []

        shortlisted[job_id].append({'name': name, 'score': score})

    # Select top 5 candidates for each job ID
    for job_id in shortlisted:
        shortlisted[job_id] = sorted(
            shortlisted[job_id], key=lambda x: x['score'], reverse=True)[:5]

        # Rename and save shortlisted CVs
        for index, candidate in enumerate(shortlisted[job_id]):
            new_file_name = f"{job_id}_{index + 1}.pdf"
            os.rename(
                f"shortlisted_cvs/{candidate['name']}.pdf", f"shortlisted_cvs/{new_file_name}")

    return jsonify(shortlisted)


if __name__ == '__main__':
    app.run(debug=True)
