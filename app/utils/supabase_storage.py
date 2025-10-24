from supabase import create_client, Client
from fastapi import UploadFile

from app.core.config import settings
from app.utils.logger import logger

supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL, supabase_key=settings.SUPABASE_KEY
)


def upload_image_to_supabase(file: UploadFile, bucket: str, path: str) -> str:
    """
    Uploads an image to Supabase Storage and returns the public URL.
    Args:
        file (UploadFile): The image file to upload.
        bucket (str): The Supabase Storage bucket name.
        path (str): The path within the bucket to store the image.
    Returns:
        str: The public URL of the uploaded image.
    """

    try:
        file_bytes = file.file.read()
        file.file.seek(0)  # Reset file pointer after reading

        # Upload the file to Supabase Storage
        supabase.storage.from_(bucket).upload(
            path,
            file=file_bytes,
            file_options={"content_type": file.content_type, "upsert": "true"},
        )
    except Exception as e:
        logger.error(f"Failed to upload image: {str(e)}")
        raise Exception(f"Failed to upload image: {str(e)}") from e
    finally:
        file.file.close()

    # Get the public URL of the uploaded image
    public_url = supabase.storage.from_(bucket).get_public_url(path)

    logger.info(f"Image uploaded to Supabase Storage at {public_url['publicURL']}")

    return public_url["publicURL"]


def delete_image_from_supabase(bucket: str, path: str) -> None:
    """
    Deletes an image from Supabase Storage.
    Args:
        bucket (str): The Supabase Storage bucket name.
        path (str): The path within the bucket of the image to delete.
    """

    try:
        supabase.storage.from_(bucket).remove([path])
    except Exception as e:
        logger.error(f"Failed to delete image: {str(e)}")
        raise Exception(f"Failed to delete image: {str(e)}") from e

    logger.info(f"Image deleted from Supabase Storage at {path}")
