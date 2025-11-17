from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List
from app.db.mongo import recon_db
from app.ftp.ftputil import FTPUtil
import os
import logging
import base64
import contextvars
from contextlib import asynccontextmanager
import errno
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.auth.auth import authenticate_user
from fastapi import File, UploadFile

# Holds the current connection (per async context)
current_ftp_connection = contextvars.ContextVar("current_ftp_connection", default=None)



router = APIRouter()
logger = logging.getLogger(__name__)

MOCK_DATA = [
    "PRIME_RSI_prod_daily_incoming_report_20241008.txt",
    "PRIME_RSI_prod_daily_incoming_report_20241009_with_two_valid_records 1.txt",
    "PRIME_RSI_prod_daily_incoming_report_20241009_with_two_valid_records_error.txt",
    "PRIME_RSI_prod_outgoing_daily_report_20240923.txt",
    "PRIME_RSI_prod_outgoing_daily_report_20240923_with_two_valid_records-renamed.txt",
    "PRIME_RSI_prod_outgoing_daily_report_20240923_with_two_valid_records.txt"
]






def decode (key: str) -> str:
    decoded_bytes = base64.b64decode(key )
    decoded_key  = decoded_bytes.decode("utf-8")  # convert bytes to string
    return decoded_key

def ensure_folder_exists(sftp, folder_path: str) -> None:
    """Ensure the specified folder exists in SFTP"""
    try:
        logger.debug(f"Checking if folder exists: {folder_path}")
        sftp.stat(folder_path)
        logger.info(f"Folder exists: {folder_path}")
    except IOError:
        logger.info(f"Creating folder: {folder_path}")
        try:
            sftp.mkdir(folder_path)
        except IOError as e:
            # If parent directory doesn't exist, try to create it
            parent_dir = os.path.dirname(folder_path)
            if parent_dir:
                logger.info(f"Parent folder doesn't exist, creating: {parent_dir}")
                try:
                    sftp.stat(parent_dir)
                except IOError:
                    sftp.mkdir(parent_dir)
                # Try creating the original folder again
                sftp.mkdir(folder_path)

def get_full_path(*parts: str) -> str:
    """
    Construct a clean path from parts, removing duplicate slashes and leading/trailing slashes
    """
    # Join all parts with '/', remove duplicate slashes, and strip leading/trailing slashes
    return '/'.join(p.strip('/') for p in parts if p).strip('/')

async def connect_to_ftp():
    host = os.getenv('PRIME_SFTP_SERVER')
    env = os.getenv("ENV", "PROD").upper()
    port = int(os.getenv('PRIME_SFTP_SERVER_PORT', '22').strip('"').strip("'"))
    user = os.getenv('PRIME_SFTP_USER')
    user_password = os.getenv('PRIME_SFTP_PASS')
    priv_key_str = os.getenv('PRIME_SFTP_PRIV_KEY_FILE').replace('\\n', '\n')


    priv_key_file_passphrase = os.getenv('PRIME_SFTP_PRIV_KEY_FILE_PASSPHRASE', None)
    pub_key_str = os.getenv('PRIME_SFTP_PUB_KEY_FILE').replace('\\n', '\n')

    if env == "LOCAL":
        try:

            priv_key_str  = decode(priv_key_str)
            pub_key_str  = decode(pub_key_str)


        except Exception as e:
            raise ValueError(f"Failed to decode  key: {e}")

    # Base path and folder configuration
    ftp_instance_folder = os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev')
    primerecon_folder = os.getenv('PRIMERECON_FTP_FOLDER', 'primerecon')
    primerecon_archive_folder = os.getenv('PRIMERECON_ARCHIVE_FOLDER', 'primerecon_archive')
    full_primerecon_path = get_full_path(ftp_instance_folder, primerecon_folder)
    full_archive_path = get_full_path(ftp_instance_folder, primerecon_archive_folder)
     # Log environment variables
    #logger.info(f"Recon type: {recon_type.upper()}")
    logger.info(f"FTP server: {host}:{port}")
    logger.info(f"FTP user: {user}")
    logger.info(f"Full primerecon path: {full_primerecon_path}")
    logger.info(f"Full archive path: {full_archive_path}")



    ftputil = None
    try:
        # Initialize FTP connection
        ftputil = FTPUtil(
            host=host,
            port=port,
            user=user,
            user_password=user_password,
            priv_key_str=priv_key_str,
            pub_key_str=pub_key_str,
            passphrase=priv_key_file_passphrase,
            known_hosts=None
        )
        sftp = ftputil.acquire_sftp_channel()
        logger.info(f"Connected to SFTP server: {host}:{port} as {user}")
        return ftputil
    except Exception as e:
        logger.error(f"Critical error in file processing: {str(e)}")
        return None
    finally:
        if ftputil:
            ftputil.release_sftp_channel()

@asynccontextmanager
async def ftp_connection():
    existing_conn = current_ftp_connection.get()

    if existing_conn:
        yield existing_conn
        return

    ftputil = None
    try:
        ftputil = await connect_to_ftp()
        if not ftputil:
            raise RuntimeError("Failed to establish SFTP connection")

        current_ftp_connection.set(ftputil)
        yield ftputil
    finally:
        if ftputil:
            ftputil.release_sftp_channel()
            current_ftp_connection.set(None)

async def list_recon_files() -> List[str]:
    folder = get_full_path(
        os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev'),
        os.getenv('PRIMERECON_FTP_FOLDER', 'primerecon')
    )


    async with ftp_connection() as ftputil:

        sftp = ftputil.acquire_sftp_channel()
        ensure_folder_exists(sftp, folder)
        return sftp.listdir(folder)


async def list_archive_files() -> List[str]:
    folder = get_full_path(
        os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev'),
        os.getenv('PRIMERECON_ARCHIVE_FOLDER', 'primerecon_archive')
    )

    async with ftp_connection() as ftputil:
        sftp = ftputil.acquire_sftp_channel()
        ensure_folder_exists(sftp, folder)
        return sftp.listdir(folder)

@router.get(
    "/recon_ftp",
    response_model=List[str],
    tags=["ftp"],
    responses={
        200: {
            "description": "List of ftp recon files",
            "content": {
                "application/json": {"example": MOCK_DATA}
            }
        }
    }
)
async def get_recon_ftp(user: dict = Depends(authenticate_user)):
    return await list_recon_files()


@router.get(
    "/recon_ftp_archives",
    response_model=List[str],
    tags=["ftp"],
    responses={
        200: {
            "description": "List of ftp recon archive files",
            "content": {
                "application/json": {"example": MOCK_DATA}
            }
        }
    }
)
async def get_recon_ftp_archives(user: dict = Depends(authenticate_user)):
    return await list_archive_files()

@router.get(
    "/recon_ftp_both",
    response_model=dict,
    tags=["ftp"],
    responses={200: {"description": "Recon + archive file list"}}
)
async def get_recon_ftp_both():
    # These will share the FTP connection under the hood
    recon_files = await list_recon_files()
    archive_files = await list_archive_files()
    return {
        "recon": recon_files,
        "archive": archive_files
    }



@router.delete(
    "/recon_ftp/delete",
    tags=["ftp"],
    status_code=200,
    responses={
        200: {"description": "File deleted successfully"},
        404: {"description": "File not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_recon_file(filename: str = Query(..., description="File path relative to the recon FTP folder"), user: dict = Depends(authenticate_user)):
    """
    Delete a file by filename inside the recon FTP folder.
    """
    folder = get_full_path(
        os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev'),
        os.getenv('PRIMERECON_FTP_FOLDER', 'primerecon')
    )
    # Construct the full remote path
    remote_path = '/' + get_full_path(folder, filename)

    async with ftp_connection() as ftputil:
        sftp = ftputil.acquire_sftp_channel()


        try:
            sftp.stat(remote_path)
            sftp.remove(remote_path)
            return {"message": f"File '{filename}' deleted successfully"}
        except OSError as e:
            if e.errno == errno.ENOENT:  # File not found
                raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
            else:
                logger.error(f"Unexpected SFTP error: {e}")
                raise HTTPException(status_code=500, detail="Unexpected SFTP error")


@router.delete(
    "/recon_ftp_archives/delete",
    tags=["ftp"],
    status_code=200,
    responses={
        200: {"description": "File deleted successfully"},
        404: {"description": "File not found"},
        500: {"description": "SFTP error occurred"}
    }
)
async def delete_file_from_archives(filename: str = Query(..., description="File path relative to the recon FTP folder"), user: dict = Depends(authenticate_user)):
    folder = get_full_path(
        os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev'),
        os.getenv('PRIMERECON_ARCHIVE_FOLDER', 'primerecon_archive')
    )

    remote_path = '/' + get_full_path(folder, filename)

    async with ftp_connection() as ftputil:
        sftp = ftputil.acquire_sftp_channel()


        try:
            sftp.stat(remote_path)
            sftp.remove(remote_path)
            return {"message": f"File '{filename}' deleted successfully"}
        except OSError as e:
            if e.errno == errno.ENOENT:  # File not found
                raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
            else:
                logger.error(f"Unexpected SFTP error: {e}")
                raise HTTPException(status_code=500, detail="Unexpected SFTP error")


from fastapi.responses import StreamingResponse
from io import BytesIO

@router.get(
    "/recon_ftp/download",
    tags=["ftp"],
    responses={
        200: {"description": "File downloaded successfully"},
        404: {"description": "File not found"},
        500: {"description": "SFTP error occurred"}
    }
)
async def download_recon_file(filename: str = Query(..., description="File path relative to the recon FTP folder"), user: dict = Depends(authenticate_user)):
    folder = get_full_path(
        os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev'),
        os.getenv('PRIMERECON_FTP_FOLDER', 'primerecon')
    )
    remote_path = '/' + get_full_path(folder, filename)

    async with ftp_connection() as ftputil:
        sftp = ftputil.acquire_sftp_channel()
        try:
            file_obj = BytesIO()
            sftp.getfo(remote_path, file_obj)
            file_obj.seek(0)
            return StreamingResponse(file_obj, media_type="application/octet-stream", headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(filename)}"
            })
        except OSError as e:
            if "No such file" in str(e):
                raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
            logger.error(f"Download error: {e}")
            raise HTTPException(status_code=500, detail="Failed to download file")

@router.get(
    "/recon_ftp_archives/download",
    tags=["ftp"],
    responses={
        200: {"description": "File downloaded successfully"},
        404: {"description": "File not found"},
        500: {"description": "SFTP error occurred"}
    }
)
async def download_archive_file(filename: str = Query(..., description="File path relative to the archive FTP folder"), user: dict = Depends(authenticate_user)):
    folder = get_full_path(
        os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev'),
        os.getenv('PRIMERECON_ARCHIVE_FOLDER', 'primerecon_archive')
    )
    remote_path = '/' + get_full_path(folder, filename)

    async with ftp_connection() as ftputil:
        sftp = ftputil.acquire_sftp_channel()
        try:
            file_obj = BytesIO()
            sftp.getfo(remote_path, file_obj)
            file_obj.seek(0)
            return StreamingResponse(file_obj, media_type="application/octet-stream", headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(filename)}"
            })
        except OSError as e:
            if "No such file" in str(e):
                raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
            logger.error(f"Download error: {e}")
            raise HTTPException(status_code=500, detail="Failed to download file")

@router.put(
    "/recon_ftp/rename",
    tags=["ftp"],
    status_code=200,
    responses={
        200: {"description": "File renamed successfully"},
        404: {"description": "Original file not found"},
        400: {"description": "New filename already exists"},
        500: {"description": "Failed to rename file"}
    }
)
async def rename_recon_file(
    old_filename: str = Query(..., description="Current filename"),
    new_filename: str = Query(..., description="New filename"),
    user: dict = Depends(authenticate_user)
):
    folder = get_full_path(
        os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev'),
        os.getenv('PRIMERECON_FTP_FOLDER', 'primerecon')
    )

    async with ftp_connection() as ftputil:
        sftp = ftputil.acquire_sftp_channel()
        old_path = '/' + get_full_path(folder, old_filename)
        new_path = '/' + get_full_path(folder, new_filename)

        try:
            sftp.stat(old_path)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File '{old_filename}' not found")

        # Prevent overwriting if new file exists
        try:
            sftp.stat(new_path)
            raise HTTPException(status_code=400, detail=f"File '{new_filename}' already exists")
        except FileNotFoundError:
            pass  # OK, target name doesn't exist

        try:
            sftp.rename(old_path, new_path)
            return {"message": f"Renamed '{old_filename}' to '{new_filename}'"}
        except Exception as e:
            logger.error(f"Error renaming file: {e}")
            raise HTTPException(status_code=500, detail="Failed to rename file")

@router.put(
    "/recon_ftp_archives/rename",
    tags=["ftp"],
    status_code=200,
    responses={
        200: {"description": "File renamed successfully"},
        404: {"description": "Original file not found"},
        400: {"description": "New filename already exists"},
        500: {"description": "Failed to rename file"}
    }
)
async def rename_archive_file(
    old_filename: str = Query(..., description="Current filename"),
    new_filename: str = Query(..., description="New filename"),
    user: dict = Depends(authenticate_user)
):
    folder = get_full_path(
        os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev'),
        os.getenv('PRIMERECON_ARCHIVE_FOLDER', 'primerecon_archive')
    )

    async with ftp_connection() as ftputil:
        sftp = ftputil.acquire_sftp_channel()
        old_path = '/' + get_full_path(folder, old_filename)
        new_path = '/' + get_full_path(folder, new_filename)

        try:
            sftp.stat(old_path)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File '{old_filename}' not found")

        try:
            sftp.stat(new_path)
            raise HTTPException(status_code=400, detail=f"File '{new_filename}' already exists")
        except FileNotFoundError:
            pass  # OK, target name doesn't exist

        try:
            sftp.rename(old_path, new_path)
            return {"message": f"Renamed '{old_filename}' to '{new_filename}'"}
        except Exception as e:
            logger.error(f"Error renaming archive file: {e}")
            raise HTTPException(status_code=500, detail="Failed to rename file")


@router.get(
    "/recon_ftp/count",
    tags=["ftp"],
    summary="Get count of recon FTP files"
)
async def count_recon_ftp_files(user: dict = Depends(authenticate_user)):
    try:
        files = await list_recon_files()
        return {"count": len(files)}
    except Exception as e:
        logger.error(f"Error counting recon files: {e}")
        raise HTTPException(status_code=500, detail="Failed to count recon files")


@router.get(
    "/recon_ftp_archives/count",
    tags=["ftp"],
    summary="Get count of recon FTP archive files"
)
async def count_recon_ftp_archive_files(user: dict = Depends(authenticate_user)):
    try:
        files = await list_archive_files()
        return {"count": len(files)}
    except Exception as e:
        logger.error(f"Error counting archive files: {e}")
        raise HTTPException(status_code=500, detail="Failed to count archive files")


from fastapi import File, UploadFile, Query

@router.post(
    "/recon_ftp/upload",
    tags=["ftp"],
    status_code=201,
    summary="Upload file to specified FTP folder",
    responses={
        201: {"description": "File uploaded successfully"},
        400: {"description": "Invalid upload or folder"},
        404: {"description": "Target folder not found"},
        500: {"description": "Failed to upload file"}
    }
)
async def upload_file_to_ftp(
    file: UploadFile = File(...),
    folder: str = Query(..., description="Folder name under FTP root (e.g. 'primerecon', 'primerecon_archive')"),
    #user: dict = Depends(authenticate_user)
):
    # Clean folder path
    folder = folder.strip("/")

    # Base path: e.g., dev/primerecon
    ftp_root = os.getenv('FTP_INSTANCE_FOLDER_NAME', 'dev')
    full_path = get_full_path(ftp_root, folder)
    remote_path = get_full_path(full_path, file.filename)

    async with ftp_connection() as ftputil:
        sftp = ftputil.acquire_sftp_channel()

        try:
            # Ensure target folder exists
            ensure_folder_exists(sftp, f'{full_path}')
        except Exception as e:
            logger.error(f"Folder validation failed for '{full_path}': {e}")
            raise HTTPException(status_code=404, detail=f"Folder '{folder}' not found or could not be created")

        try:
            file_content = await file.read()

            with sftp.open(remote_path, 'w') as remote_file:
                remote_file.write(file_content)

            return {"message": f"File '{file.filename}' uploaded successfully to '{folder}'"}
        except Exception as e:
            logger.error(f"Upload failed for file '{file.filename}' to '{folder}': {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file")



