# pip install google-api-python-client
from googleapiclient.discovery import build
from google.oauth2 import service_account
import subprocess
from datetime import datetime


BASE_PATH = "C:/Users/david/Documents/CoursePaper/backend/CourseProject/"
SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = f"{BASE_PATH}service_account.json"
BACKUP_DIR = f"{BASE_PATH}backup/"
PARENT_FOLDER_ID = "1X6AFbFsxTccFrr5TQFHXvP6ojfuEdep-"


def execute_command():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"backup_{timestamp}.json"
    file_path = f"{BACKUP_DIR}{file_name}"

    command = [
        "python",
        f"{BASE_PATH}manage.py",
        "dumpdata",
        "--natural-foreign",
        "--natural-primary",
        "--exclude=auth.permission",
        "--exclude=contenttypes",
        "--indent=4",
    ]

    try:
        with open(file_path, "w") as output_file:
            subprocess.run(command, stdout=output_file, check=True)
        print(
            f"The command executed successfully, and the file was saved to '{file_path}'."
        )
        return file_path
    except subprocess.CalledProcessError as e:
        print(f"Error while executing the command: {e}")
    except FileNotFoundError:
        print(
            f"The directory '{BACKUP_DIR}' does not exist. Please create it before running the script."
        )
    return None


def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return creds


def upload_to_drive(file_path):
    if not file_path:
        print("No file specified for upload.")
        return

    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    file_name = file_path.split("/")[-1]

    file_metadata = {"name": file_name, "parents": [PARENT_FOLDER_ID]}

    try:
        with open(file_path, "rb") as file:
            service.files().create(body=file_metadata, media_body=file_path).execute()
        print(f"The file '{file_name}' was successfully uploaded to Google Drive.")
    except Exception as e:
        print(f"Error uploading the file to Google Drive: {e}")


if __name__ == "__main__":
    backup_file = execute_command()
    upload_to_drive(backup_file)
    input()
