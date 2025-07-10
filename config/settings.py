import os


class Config:
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    SHORTLISTED_CVS_FOLDER = 'shortlisted_cvs'

    # More detailed skills with weights
    REQUIRED_SKILLS = {
        '1021': ['python', 'flask', 'api', 'sql', 'git'],
        'job_id_2': ['javascript', 'react', 'html', 'css', 'node'],
        'developer': ['python', 'javascript', 'api', 'git', 'sql'],
        'designer': ['figma', 'ui', 'ux', 'adobe', 'design'],
        # Add more job IDs and their required skills as needed
    }
