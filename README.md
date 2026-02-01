# Document Management System (DMS) Backend API

A production-ready FastAPI backend for managing documents, folders, and user authentication with comprehensive file management capabilities.

## 🎯 Overview

This is a complete implementation of a Document Management System backend that provides:

- **User Authentication**: Secure registration and login with JWT tokens
- **Folder Management**: Hierarchical folder creation, deletion, and organization
- **File Management**: Upload, download, rename, and delete files with base64 encoding
- **Multi-user Support**: Complete user isolation and data security
- **Docker Deployment**: Ready-to-deploy with docker-compose

## ✨ Features

### Authentication System
- User registration with email validation
- Secure login with JWT tokens (30-minute expiration)
- Password hashing with bcrypt
- Bearer token authentication on protected routes

### Folder Management
- Create folders with hierarchical structure (nested folders)
- Retrieve folder contents with subfolders and files list
- Rename folders
- Delete folders with cascade deletion
- User isolation - each user only sees their own folders

### File Management
- Upload files with base64 encoding
- Download files in base64 format
- Automatic MIME type detection
- Automatic file size calculation
- Retrieve file metadata
- Rename files
- Delete files
- View folder contents with integrated file listings
- User isolation - each user only sees their own files

## 🏗️ Architecture

### Technology Stack
- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn 0.27.0
- **Database**: SQLite3 with raw SQL queries
- **Authentication**: JWT (python-jose) + bcrypt
- **Validation**: Pydantic 2.5.0
- **Containerization**: Docker & Docker Compose

### Project Structure
```
backend-exercise-2-main/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database connection and utilities
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── folders.py       # Folder management endpoints
│   │   ├── files.py         # File management endpoints
│   │   └── health.py        # Health check endpoint
│   └── utils/
│       ├── __init__.py
│       └── security.py      # JWT and password utilities
├── migrations/
│   ├── 002_create_users_table.py
│   ├── 003_create_folders_table.py
│   └── 004_create_files_table.py
├── Dockerfile
├── docker-compose.yml
├── migrate.py               # Database migration runner
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 📋 API Endpoints (11 Total)

### Authentication (2 endpoints)

#### Register User
```
POST /auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password"
}

Response: 200
{
    "message": "User registered successfully",
    "user_id": 1
}
```

#### Login
```
POST /auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password"
}

Response: 200
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### Folder Management (4 endpoints)

#### Create Folder
```
POST /folders
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "My Documents",
    "parent_folder_id": null  # Optional, null for root-level folders
}

Response: 201
{
    "id": 1,
    "name": "My Documents",
    "user_id": 1,
    "parent_folder_id": null,
    "created_at": "2026-02-01T10:30:00"
}
```

#### Get Folder Contents
```
GET /folders/{folder_id}
Authorization: Bearer <token>

Response: 200
{
    "id": 1,
    "name": "My Documents",
    "user_id": 1,
    "parent_folder_id": null,
    "subfolders": [
        {"id": 2, "name": "Projects"}
    ],
    "files": [
        {"id": 1, "name": "document.pdf", "mime_type": "application/pdf", "size": 1024}
    ]
}
```

#### Rename Folder
```
PATCH /folders/{folder_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "New Folder Name"
}

Response: 200
{
    "id": 1,
    "name": "New Folder Name",
    "user_id": 1
}
```

#### Delete Folder
```
DELETE /folders/{folder_id}
Authorization: Bearer <token>

Response: 200
{
    "message": "Folder deleted successfully"
}
```

### File Management (5 endpoints)

#### Upload File
```
POST /files
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "document.pdf",
    "content": "base64_encoded_file_content...",  # Base64-encoded file content
    "parent_folder_id": 1  # Optional
}

Response: 201
{
    "id": 1,
    "name": "document.pdf",
    "size": 5120,
    "mime_type": "application/pdf",
    "user_id": 1,
    "parent_folder_id": 1,
    "created_at": "2026-02-01T10:30:00"
}
```

#### Get File Metadata
```
GET /files/{file_id}
Authorization: Bearer <token>

Response: 200
{
    "id": 1,
    "name": "document.pdf",
    "size": 5120,
    "mime_type": "application/pdf",
    "user_id": 1,
    "parent_folder_id": 1,
    "created_at": "2026-02-01T10:30:00"
}
```

#### Download File
```
GET /files/{file_id}/download
Authorization: Bearer <token>

Response: 200
{
    "content": "base64_encoded_file_content...",
    "name": "document.pdf",
    "mime_type": "application/pdf",
    "size": 5120
}
```

#### Rename File
```
PATCH /files/{file_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "new_document_name.pdf"
}

Response: 200
{
    "id": 1,
    "name": "new_document_name.pdf",
    "size": 5120,
    "mime_type": "application/pdf"
}
```

#### Delete File
```
DELETE /files/{file_id}
Authorization: Bearer <token>

Response: 200
{
    "message": "File deleted successfully"
}
```

### Health Check (1 endpoint)

#### Health Status
```
GET /health

Response: 200
{
    "status": "healthy"
}
```

## 🚀 Installation & Setup

### Prerequisites
- Docker & Docker Compose (recommended)
- OR Python 3.11+

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/rkphariharan/xai-tutor-feb-Hariharan_Ravikumar.git
cd backend-exercise-2-main

# Start the application with Docker Compose
docker-compose up --build

# The API will be available at http://localhost:8000
```

**That's it!** Docker Compose will:
- Build the Docker image
- Create and start the container
- Run all database migrations automatically
- Start the Uvicorn server on port 8000

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/rkphariharan/xai-tutor-feb-Hariharan_Ravikumar.git
cd backend-exercise-2-main

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python migrate.py upgrade

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 Usage Examples

### 1. Register a User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

### 2. Login and Get Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'

# Save the access_token from response
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 3. Create a Folder
```bash
curl -X POST http://localhost:8000/folders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Documents",
    "parent_folder_id": null
  }'
```

### 4. Create a Nested Folder
```bash
curl -X POST http://localhost:8000/folders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Projects",
    "parent_folder_id": 1
  }'
```

### 5. Upload a File
```bash
# First, convert file to base64
# On Windows: [Convert]::ToBase64String([IO.File]::ReadAllBytes("file.pdf"))
# On Linux: base64 -w0 file.pdf

BASE64_CONTENT="JVBERi0xLjQK..."  # Your base64-encoded content

curl -X POST http://localhost:8000/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "document.pdf",
    "content": "'$BASE64_CONTENT'",
    "parent_folder_id": 1
  }'
```

### 6. Download a File
```bash
curl -X GET http://localhost:8000/files/1/download \
  -H "Authorization: Bearer $TOKEN" | jq '.content'
```

### 7. Get Folder Contents
```bash
curl -X GET http://localhost:8000/folders/1 \
  -H "Authorization: Bearer $TOKEN"
```

## 🔐 Security Features

- **Password Hashing**: Bcrypt with salt rounds
- **JWT Authentication**: Token-based API security
- **User Isolation**: Complete data separation per user
- **Input Validation**: Pydantic schema validation
- **SQL Injection Prevention**: Parameterized queries
- **Foreign Key Constraints**: Database-level referential integrity
- **Cascade Delete**: Automatic cleanup of related data

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
```

### Folders Table
```sql
CREATE TABLE folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    parent_folder_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_folder_id) REFERENCES folders(id) ON DELETE CASCADE
);
```

### Files Table
```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    content BLOB NOT NULL,
    size INTEGER NOT NULL,
    mime_type TEXT,
    user_id INTEGER NOT NULL,
    parent_folder_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_folder_id) REFERENCES folders(id) ON DELETE CASCADE
);
```

## 🧪 Testing

The API endpoints have been thoroughly tested. To test manually:

### Health Check
```bash
curl http://localhost:8000/health
```

### Full API Test Flow
1. Register user → Get user_id
2. Login → Get JWT token
3. Create folder → Get folder_id
4. Create nested folder → Get nested_folder_id
5. Upload file → Get file_id
6. Get file metadata → Verify file information
7. Download file → Verify content integrity
8. Rename folder → Verify name change
9. Rename file → Verify name change
10. Get folder contents → Verify structure
11. Delete file → Verify deletion
12. Delete folder → Verify cascade deletion

All endpoints have been verified and tested successfully.

## 🐳 Docker Configuration

### Dockerfile Highlights
- Multi-stage build for optimization
- Alpine Linux base image for minimal size
- Automatic migration runner on startup
- Uvicorn server configuration

### docker-compose.yml Highlights
- Complete service configuration
- Volume mounts for data persistence
- Port mapping (8000:8000)
- Environment variable configuration
- Automatic restart policy

## 📝 Environment Variables

Create a `.env` file if needed:
```
DATABASE_URL=sqlite:///./app.db
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
```

Currently, the application uses SQLite with a file-based database (app.db).

## ⚠️ Important Notes

- **Raw SQL**: This implementation uses raw SQL queries exclusively (no ORM)
- **SQLite**: Production-ready for small to medium deployments. For large scale, consider PostgreSQL.
- **JWT Expiration**: Tokens expire in 30 minutes
- **File Size Limit**: Determined by available disk space and memory
- **Base64 Encoding**: Files are stored in base64 format for text-safe transmission

## 🔧 Troubleshooting

### Docker Build Fails
```bash
# Clear Docker cache and rebuild
docker-compose down --volumes
docker-compose up --build
```

### Port 8000 Already in Use
```bash
# Change port in docker-compose.yml
# Or kill process using the port on Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Issues
```bash
# Reset database
rm app.db
python migrate.py upgrade
```

### Migration Errors
```bash
# Check migration status
python migrate.py --help

# Manually rollback
python migrate.py downgrade -1
```

## ✅ Implementation Status

All requirements have been successfully implemented:

✅ **All 11 API Endpoints:**
- ✅ 2 Authentication endpoints (register, login)
- ✅ 4 Folder management endpoints (create, get, rename, delete)
- ✅ 5 File management endpoints (upload, get metadata, download, rename, delete)

✅ **Core Features:**
- ✅ User registration and login with secure JWT
- ✅ Hierarchical folder structure with parent-child relationships
- ✅ Recursive folder deletion with cascade
- ✅ File upload with base64 encoding
- ✅ File download with base64 decoding
- ✅ Automatic MIME type detection
- ✅ Automatic file size calculation
- ✅ Complete user data isolation

✅ **Quality Assurance:**
- ✅ Comprehensive error handling
- ✅ Input validation with Pydantic
- ✅ Security with bcrypt and JWT
- ✅ SQL injection prevention
- ✅ All endpoints tested and verified

✅ **Deployment:**
- ✅ Docker containerization
- ✅ Automatic database migrations
- ✅ Single command startup: `docker-compose up --build`

## 📄 License

This project is part of the Document Management System assignment.

## 👤 Author

Backend Implementation - 2026

---

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **Last Updated**: February 2026
