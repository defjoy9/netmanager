import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(service, local_file_path, drive_folder_id='1jIkJ-v9g3z94cLAGFSkBKSI_zrX-_y7C'):
    file_metadata = {
        'name': os.path.basename(local_file_path),
        'parents': [drive_folder_id] if drive_folder_id else []
    }
    media = MediaFileUpload(local_file_path, mimetype='application/octet-stream')
    file = service.files().create(body=file_metadata, media_body=media, fields='id, name, createdTime').execute()
    print(f"File ID: {file.get('id')}, Name: {file.get('name')} uploaded to Google Drive.")
    if drive_folder_id:
        print(f"Uploaded to folder ID: {drive_folder_id}")
    else:
        print("Uploaded to the root directory.")

def delete_oldest_files_in_googledrive(service, folder_id, max_file_count=30):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        pageSize=1000, # The maximum number of files to return per page.
        fields="nextPageToken, files(id, name, createdTime)"
    ).execute()
    files = results.get('files', [])

    # Sort files by creation date (oldest first)
    files.sort(key=lambda x: x['createdTime'])
    
    print(f"Files in folder ID {folder_id} sorted by creation date (oldest to newest):")
    for file in files:
        print(f"ID: {file['id']}, Name: {file['name']}, Created Time: {file['createdTime']}")

    file_count = len(files)
    # Delete the specified number of oldest files
    if file_count > max_file_count:
        num_files_to_delete = file_count - max_file_count 
        for file in files[:num_files_to_delete]:
            try:
                service.files().delete(fileId=file['id']).execute()
                print(f"File ID: {file['name']} has been deleted.")
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    service = get_drive_service()
    
    # Folder ID and number of oldest files to delete
    folder_id = '1jIkJ-v9g3z94cLAGFSkBKSI_zrX-_y7C'
    
    delete_oldest_files_in_googledrive(service, folder_id,30)

if __name__ == '__main__':
    main()
