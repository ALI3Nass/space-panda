from flask import jsonify
import os
import requests
from models.candidate import Candidate
from models.job import Job
from utils.pdf_parser import parse_pdf
from utils.scoring_algorithm import score_candidate

class CVProcessingService:
    def __init__(self, google_drive_service, google_sheets_service):
        self.google_drive_service = google_drive_service
        self.google_sheets_service = google_sheets_service
        self.shortlisted_cvs_dir = 'shortlisted_cvs'

    def process_cv_responses(self):
        responses = self.google_sheets_service.fetch_responses()
        job_candidates = {}

        for response in responses:
            candidate_name = response['candidate_name']
            job_id = response['job_id']
            cv_link = response['cv_link']

            # Download CV
            cv_file_path = self.download_cv(cv_link, candidate_name)

            # Parse CV
            cv_content = parse_pdf(cv_file_path)

            # Get job requirements
            job = Job(job_id)
            required_skills = job.get_required_skills()

            # Score candidate
            score = score_candidate(cv_content, required_skills)

            # Store candidate info
            candidate = Candidate(candidate_name, job_id, cv_link, score)
            if job_id not in job_candidates:
                job_candidates[job_id] = []
            job_candidates[job_id].append(candidate)

        shortlisted_candidates = self.select_top_candidates(job_candidates)
        return jsonify(shortlisted_candidates)

    def download_cv(self, cv_link, candidate_name):
        response = requests.get(cv_link)
        if response.status_code == 200:
            cv_file_path = os.path.join(self.shortlisted_cvs_dir, f"{candidate_name}.pdf")
            with open(cv_file_path, 'wb') as f:
                f.write(response.content)
            return cv_file_path
        else:
            raise Exception(f"Failed to download CV from {cv_link}")

    def select_top_candidates(self, job_candidates):
        shortlisted = {}
        for job_id, candidates in job_candidates.items():
            # Sort candidates by score
            candidates.sort(key=lambda x: x.score, reverse=True)
            top_candidates = candidates[:5]

            # Rename and save shortlisted CVs
            for index, candidate in enumerate(top_candidates, start=1):
                new_cv_name = f"{job_id}_{index}.pdf"
                os.rename(os.path.join(self.shortlisted_cvs_dir, f"{candidate.name}.pdf"),
                          os.path.join(self.shortlisted_cvs_dir, new_cv_name))

            shortlisted[job_id] = [{'name': candidate.name, 'score': candidate.score} for candidate in top_candidates]

        return shortlisted