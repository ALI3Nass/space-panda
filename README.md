# Flask CV Scoring Application

This project is a Flask web application designed to process candidate CVs from Google Sheets form responses. It evaluates candidates based on their CV content against a predefined list of required skills for specific job IDs. The application selects the top candidates for each job and renames their CV files for easy identification.

## Project Structure

```
flask-cv-scoring-app
├── app.py                     # Entry point of the Flask application
├── requirements.txt           # Project dependencies
├── config                     # Configuration settings
│   └── settings.py
├── services                   # Services for Google Sheets and Drive interactions
│   ├── __init__.py
│   ├── google_sheets_service.py
│   ├── google_drive_service.py
│   └── cv_processing_service.py
├── models                     # Data models for candidates and jobs
│   ├── __init__.py
│   ├── candidate.py
│   └── job.py
├── utils                      # Utility functions for PDF parsing and scoring
│   ├── __init__.py
│   ├── pdf_parser.py
│   └── scoring_algorithm.py
├── shortlisted_cvs            # Directory for storing shortlisted CVs
│   └── .gitkeep
├── templates                  # HTML templates for the application
│   ├── index.html
│   └── results.html
├── static                     # Static files (CSS and JS)
│   ├── css
│   │   └── style.css
│   └── js
│       └── main.js
└── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd flask-cv-scoring-app
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Settings**
   Update the `config/settings.py` file with your Google API credentials and any other necessary configuration.

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Access the Application**
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- Upload CVs or view the results of the CV scoring process through the web interface.
- The application will process the CVs, score them based on the required skills, and display the top candidates for each job ID.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.