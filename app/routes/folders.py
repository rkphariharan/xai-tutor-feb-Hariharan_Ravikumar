"""
Folder management routes for hierarchical folder operations
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from app.utils.security import get_current_user, TokenData

router = APIRouter(prefix="/folders", tags=["folders"])


class FolderCreate(BaseModel):
    """Create folder request"""
    name: str
    parent_folder_id: Optional[int] = None


class FolderUpdate(BaseModel):
    """Update folder request"""
    name: str


class FolderItem(BaseModel):
    """Folder item in response"""
    id: int
    name: str
    parent_folder_id: Optional[int]
    created_at: str


class FileItem(BaseModel):
    """File item in folder"""
    id: int
    name: str
    size: int
    mime_type: Optional[str]


class FolderResponse(BaseModel):
    """Folder details with contents"""
    id: int
    name: str
    parent_folder_id: Optional[int]
    created_at: str
    subfolders: List[FolderItem]
    files: List[FileItem]


@router.post("", response_model=FolderItem, status_code=status.HTTP_201_CREATED)
def create_folder(folder: FolderCreate, current_user: TokenData = Depends(get_current_user)):
    """
    Create a new folder.
    
    - **name**: Folder name
    - **parent_folder_id**: Parent folder ID (optional, null for root level)
    """
    if not folder.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Folder name is required"
        )
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify parent folder exists (if provided) and belongs to user
            if folder.parent_folder_id:
                cursor.execute(
                    "SELECT id FROM folders WHERE id = ? AND user_id = ?",
                    (folder.parent_folder_id, current_user.user_id)
                )
                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Parent folder not found"
                    )
            
            # Create folder
            cursor.execute(
                "INSERT INTO folders (name, user_id, parent_folder_id) VALUES (?, ?, ?)",
                (folder.name, current_user.user_id, folder.parent_folder_id)
            )
            conn.commit()
            
            # Get the created folder
            folder_id = cursor.lastrowid
            cursor.execute(
                "SELECT id, name, parent_folder_id, created_at FROM folders WHERE id = ?",
                (folder_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return FolderItem(
                    id=row["id"],
                    name=row["name"],
                    parent_folder_id=row["parent_folder_id"],
                    created_at=row["created_at"]
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create folder"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/{folder_id}", response_model=FolderResponse)
def get_folder(folder_id: int, current_user: TokenData = Depends(get_current_user)):
    """
    Get folder details and list its contents (subfolders and files).
    
    - **folder_id**: Folder ID to retrieve
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify folder exists and belongs to user
            cursor.execute(
                "SELECT id, name, parent_folder_id, created_at FROM folders WHERE id = ? AND user_id = ?",
                (folder_id, current_user.user_id)
            )
            folder_row = cursor.fetchone()
            
            if not folder_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder not found"
                )
            
            # Get subfolders
            cursor.execute(
                "SELECT id, name, parent_folder_id, created_at FROM folders WHERE parent_folder_id = ? AND user_id = ?",
                (folder_id, current_user.user_id)
            )
            subfolders = [
                FolderItem(
                    id=row["id"],
                    name=row["name"],
                    parent_folder_id=row["parent_folder_id"],
                    created_at=row["created_at"]
                )
                for row in cursor.fetchall()
            ]
            
            # Get files in folder
            cursor.execute(
                "SELECT id, name, size, mime_type FROM files WHERE parent_folder_id = ? AND user_id = ?",
                (folder_id, current_user.user_id)
            )
            files = [
                FileItem(
                    id=row["id"],
                    name=row["name"],
                    size=row["size"],
                    mime_type=row["mime_type"]
                )
                for row in cursor.fetchall()
            ]
            
            return FolderResponse(
                id=folder_row["id"],
                name=folder_row["name"],
                parent_folder_id=folder_row["parent_folder_id"],
                created_at=folder_row["created_at"],
                subfolders=subfolders,
                files=files
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.patch("/{folder_id}", response_model=FolderItem)
def rename_folder(folder_id: int, folder: FolderUpdate, current_user: TokenData = Depends(get_current_user)):
    """
    Rename a folder.
    
    - **folder_id**: Folder ID to rename
    - **name**: New folder name
    """
    if not folder.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Folder name is required"
        )
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify folder exists and belongs to user
            cursor.execute(
                "SELECT id FROM folders WHERE id = ? AND user_id = ?",
                (folder_id, current_user.user_id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder not found"
                )
            
            # Update folder name
            cursor.execute(
                "UPDATE folders SET name = ? WHERE id = ?",
                (folder.name, folder_id)
            )
            conn.commit()
            
            # Get updated folder
            cursor.execute(
                "SELECT id, name, parent_folder_id, created_at FROM folders WHERE id = ?",
                (folder_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return FolderItem(
                    id=row["id"],
                    name=row["name"],
                    parent_folder_id=row["parent_folder_id"],
                    created_at=row["created_at"]
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update folder"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(folder_id: int, current_user: TokenData = Depends(get_current_user)):
    """
    Delete a folder and all its contents (recursive delete).
    
    - **folder_id**: Folder ID to delete
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify folder exists and belongs to user
            cursor.execute(
                "SELECT id FROM folders WHERE id = ? AND user_id = ?",
                (folder_id, current_user.user_id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder not found"
                )
            
            # Delete folder and all its contents (cascade via foreign keys)
            cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
            conn.commit()
            
            return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
