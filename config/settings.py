import os

class Config:
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    SHORTLISTED_CVS_FOLDER = 'shortlisted_cvs'
    REQUIRED_SKILLS = {
        'job_id_1': ['skill1', 'skill2', 'skill3'],
        'job_id_2': ['skill4', 'skill5', 'skill6'],
        # Add more job IDs and their required skills as needed
    }