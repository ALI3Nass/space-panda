from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os

def download_cv(file_url, destination_folder):
    """Download CV from Google Drive using the file URL."""
    drive_service = build('drive', 'v3')
    
    file_id = file_url.split('/')[-2]  # Extract file ID from URL
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    
    # Save the file to the destination folder
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    file_path = os.path.join(destination_folder, f"{file_id}.pdf")
    with open(file_path, 'wb') as f:
        f.write(fh.getbuffer())
    
    return file_path

def get_file_metadata(file_url):
    """Get metadata of the file from Google Drive."""
    drive_service = build('drive', 'v3')
    
    file_id = file_url.split('/')[-2]  # Extract file ID from URL
    file = drive_service.files().get(fileId=file_id, fields='name').execute()
    
    return file.get('name')