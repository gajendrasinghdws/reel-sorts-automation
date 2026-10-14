from pathlib import Path
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from config import DRIVE_FOLDER_ID
from google_client import drive_service

def upload_video(path: str, filename: str) -> str:
    service = drive_service()
    metadata = {
        "name": filename,
        "parents": [DRIVE_FOLDER_ID],
        "mimeType": "video/mp4",
    }
    media = MediaFileUpload(path, mimetype="video/mp4", resumable=True)
    result = service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,webViewLink",
    ).execute()
    return result["id"]

def download_file(file_id: str, destination: str):
    service = drive_service()
    request = service.files().get_media(fileId=file_id)
    with open(destination, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

def delete_file(file_id: str):
    drive_service().files().delete(fileId=file_id).execute()
