"""
File management routes for upload, download, and file operations
"""

import base64
import mimetypes
from typing import Optional, List

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from app.database import get_db
from app.utils.security import get_current_user, TokenData

router = APIRouter(prefix="/files", tags=["files"])


class FileUpload(BaseModel):
    """File upload request"""
    name: str
    content: str  # Base64 encoded content
    parent_folder_id: Optional[int] = None


class FileRename(BaseModel):
    """File rename request"""
    name: str


class FileMove(BaseModel):
    """File move request"""
    parent_folder_id: Optional[int] = None


class FileMetadata(BaseModel):
    """File metadata response"""
    id: int
    name: str
    size: int
    mime_type: Optional[str]
    parent_folder_id: Optional[int]
    created_at: str


class FileDownload(BaseModel):
    """File download response"""
    id: int
    name: str
    content: str  # Base64 encoded
    mime_type: Optional[str]
    size: int


def detect_mime_type(filename: str) -> Optional[str]:
    """Detect MIME type from filename."""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


@router.post("", response_model=FileMetadata, status_code=status.HTTP_201_CREATED)
def upload_file(file_data: FileUpload, current_user: TokenData = Depends(get_current_user)):
    """
    Upload a file with base64-encoded content.
    
    - **name**: File name
    - **content**: Base64-encoded file content
    - **parent_folder_id**: Parent folder ID (optional, null for root)
    """
    if not file_data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required"
        )
    
    if not file_data.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content is required"
        )
    
    try:
        # Decode base64 content
        try:
            decoded_content = base64.b64decode(file_data.content)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid base64 content"
            )
        
        # Calculate file size
        file_size = len(decoded_content)
        
        # Detect MIME type
        mime_type = detect_mime_type(file_data.name)
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify parent folder exists (if provided) and belongs to user
            if file_data.parent_folder_id:
                cursor.execute(
                    "SELECT id FROM folders WHERE id = ? AND user_id = ?",
                    (file_data.parent_folder_id, current_user.user_id)
                )
                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Parent folder not found"
                    )
            
            # Insert file
            cursor.execute(
                """INSERT INTO files (name, content, size, mime_type, user_id, parent_folder_id) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (file_data.name, decoded_content, file_size, mime_type, current_user.user_id, file_data.parent_folder_id)
            )
            conn.commit()
            
            # Get the created file
            file_id = cursor.lastrowid
            cursor.execute(
                "SELECT id, name, size, mime_type, parent_folder_id, created_at FROM files WHERE id = ?",
                (file_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return FileMetadata(
                    id=row["id"],
                    name=row["name"],
                    size=row["size"],
                    mime_type=row["mime_type"],
                    parent_folder_id=row["parent_folder_id"],
                    created_at=row["created_at"]
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/{file_id}", response_model=FileMetadata)
def get_file_metadata(file_id: int, current_user: TokenData = Depends(get_current_user)):
    """
    Get file metadata.
    
    - **file_id**: File ID to retrieve
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get file and verify it belongs to user
            cursor.execute(
                "SELECT id, name, size, mime_type, parent_folder_id, created_at FROM files WHERE id = ? AND user_id = ?",
                (file_id, current_user.user_id)
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            return FileMetadata(
                id=row["id"],
                name=row["name"],
                size=row["size"],
                mime_type=row["mime_type"],
                parent_folder_id=row["parent_folder_id"],
                created_at=row["created_at"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/{file_id}/download", response_model=FileDownload)
def download_file(file_id: int, current_user: TokenData = Depends(get_current_user)):
    """
    Download file content.
    
    - **file_id**: File ID to download
    Returns base64-encoded content
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get file and verify it belongs to user
            cursor.execute(
                "SELECT id, name, content, mime_type, size FROM files WHERE id = ? AND user_id = ?",
                (file_id, current_user.user_id)
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Encode content to base64 for return
            encoded_content = base64.b64encode(row["content"]).decode('utf-8')
            
            return FileDownload(
                id=row["id"],
                name=row["name"],
                content=encoded_content,
                mime_type=row["mime_type"],
                size=row["size"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.patch("/{file_id}", response_model=FileMetadata)
def rename_file(file_id: int, file_data: FileRename, current_user: TokenData = Depends(get_current_user)):
    """
    Rename a file.
    
    - **file_id**: File ID to rename
    - **name**: New file name
    """
    if not file_data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required"
        )
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify file exists and belongs to user
            cursor.execute(
                "SELECT id FROM files WHERE id = ? AND user_id = ?",
                (file_id, current_user.user_id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Update file name
            cursor.execute(
                "UPDATE files SET name = ? WHERE id = ?",
                (file_data.name, file_id)
            )
            conn.commit()
            
            # Get updated file
            cursor.execute(
                "SELECT id, name, size, mime_type, parent_folder_id, created_at FROM files WHERE id = ?",
                (file_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return FileMetadata(
                    id=row["id"],
                    name=row["name"],
                    size=row["size"],
                    mime_type=row["mime_type"],
                    parent_folder_id=row["parent_folder_id"],
                    created_at=row["created_at"]
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update file"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: int, current_user: TokenData = Depends(get_current_user)):
    """
    Delete a file.
    
    - **file_id**: File ID to delete
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify file exists and belongs to user
            cursor.execute(
                "SELECT id FROM files WHERE id = ? AND user_id = ?",
                (file_id, current_user.user_id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Delete file
            cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()
            
            return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.patch("/{file_id}/move", response_model=FileMetadata)
def move_file(file_id: int, move_data: FileMove, current_user: TokenData = Depends(get_current_user)):
    """
    Move a file to a different folder (or root).
    
    - **file_id**: File ID to move
    - **parent_folder_id**: Target folder ID (optional, null for root)
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify file exists and belongs to user
            cursor.execute(
                "SELECT id FROM files WHERE id = ? AND user_id = ?",
                (file_id, current_user.user_id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Verify target folder exists (if provided) and belongs to user
            if move_data.parent_folder_id is not None:
                cursor.execute(
                    "SELECT id FROM folders WHERE id = ? AND user_id = ?",
                    (move_data.parent_folder_id, current_user.user_id)
                )
                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Target folder not found"
                    )
            
            # Update parent folder
            cursor.execute(
                "UPDATE files SET parent_folder_id = ? WHERE id = ?",
                (move_data.parent_folder_id, file_id)
            )
            conn.commit()
            
            # Get updated file
            cursor.execute(
                "SELECT id, name, size, mime_type, parent_folder_id, created_at FROM files WHERE id = ?",
                (file_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return FileMetadata(
                    id=row["id"],
                    name=row["name"],
                    size=row["size"],
                    mime_type=row["mime_type"],
                    parent_folder_id=row["parent_folder_id"],
                    created_at=row["created_at"]
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to move file"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
