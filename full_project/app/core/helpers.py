from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, UploadFile
from app.core.config import settings
from app.core.error_messages import ERROR_MESSAGES
import os
import uuid

UPLOAD_DIR = settings.upload_dir
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

def validation_error(key: str):
    raise ValueError(ERROR_MESSAGES[key])

def register_failed_login_attempt(user):

    """
    Increment failed login attempts and block user
    after reaching the configured limit.
    """

    user.failed_login_attempts += 1

    if user.failed_login_attempts >= settings.login_max_attempts:
        user.blocked_until = datetime.now() + timedelta(hours=settings.login_block_duration_hours)

        user.failed_login_attempts = 0  # reset attempts after blocking

def check_if_user_blocked(user):

    """
    Check if the user is currently blocked.
    """

    if not user.blocked_until:
        return
    
    current_time = datetime.now()

    if user.blocked_until > current_time:
        remaining = user.blocked_until - current_time
        minutes = int(remaining.total_seconds() // 60)

        raise HTTPException(
            status_code=403,
            detail=f"Account blocked. Try again after {minutes} minutes."
        )

def reset_failed_attempts(user):

    """
    Reset login attempts after successful login.
    """

    user.failed_login_attempts = 0
    user.blocked_until = None

def save_upload_file(file: UploadFile) -> str:

    """
    Save an uploaded file to the configured upload directory.
    Returns the filename of the saved file.
    """

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, PNG and GIF images are allowed."
            )
        )
    
    # Read file content
    contents = file.file.read()

    # Validate size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must not exceed 1 MB."
        )

    unique_filename = f"{uuid.uuid4()}{extension}"

    filepath = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )

    with open(filepath, "wb") as buffer:
        buffer.write(contents)

    return unique_filename