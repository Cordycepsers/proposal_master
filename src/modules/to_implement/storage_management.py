"""
Storage Management Module - Independent Storage and File Management

This module handles comprehensive storage management across multiple platforms.
It can be developed, tested, and upgraded independently of other modules.
Includes Google Drive API, Google Cloud Storage, local storage, and backup management.

Features:
- Multi-platform storage support (Google Drive, Google Cloud Storage, Local)
- File lifecycle management and versioning
- Automated backup and disaster recovery
- Access control and permissions management
- Storage optimization and cleanup
- File synchronization and replication
- Metadata management and search
"""

import asyncio
import logging
import json
import os
import shutil
import hashlib
import mimetypes
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Union, BinaryIO
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import zipfile
import tarfile
from concurrent.futures import ThreadPoolExecutor
import threading

# Google Cloud libraries
try:
    from google.cloud import storage as gcs
    from google.oauth2 import service_account
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

# Google Drive API libraries
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    import pickle
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

# AWS S3 libraries (for multi-cloud support)
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

# File monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FileMetadata:
    """File metadata structure"""
    file_id: str
    name: str
    path: str
    size: int
    mime_type: str
    created_date: datetime
    modified_date: datetime
    checksum: str
    storage_provider: str
    storage_path: str
    version: int = 1
    tags: List[str] = field(default_factory=list)
    access_permissions: Dict[str, str] = field(default_factory=dict)
    backup_locations: List[str] = field(default_factory=list)
    retention_policy: Optional[str] = None
    encryption_status: bool = False
    compression_status: bool = False

@dataclass
class StorageConfig:
    """Storage configuration"""
    provider: str  # 'google_drive', 'google_cloud_storage', 'local', 'aws_s3'
    credentials: Dict[str, Any]
    bucket_name: Optional[str] = None
    folder_path: Optional[str] = None
    encryption_enabled: bool = True
    compression_enabled: bool = False
    versioning_enabled: bool = True
    backup_enabled: bool = True
    retention_days: int = 365
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = field(default_factory=lambda: ['pdf', 'docx', 'txt', 'json', 'csv', 'xlsx'])

@dataclass
class StorageOperation:
    """Storage operation tracking"""
    operation_id: str
    operation_type: str  # 'upload', 'download', 'delete', 'copy', 'move'
    file_path: str
    storage_provider: str
    status: str = 'pending'  # 'pending', 'in_progress', 'completed', 'failed'
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class StorageProviderInterface(ABC):
    """Abstract interface for storage providers"""
    
    @abstractmethod
    async def upload_file(self, local_path: str, remote_path: str, metadata: Optional[Dict[str, Any]] = None) -> FileMetadata:
        """Upload file to storage"""
        pass
    
    @abstractmethod
    async def download_file(self, remote_path: str, local_path: str) -> str:
        """Download file from storage"""
        pass
    
    @abstractmethod
    async def delete_file(self, remote_path: str) -> bool:
        """Delete file from storage"""
        pass
    
    @abstractmethod
    async def list_files(self, folder_path: str = "", recursive: bool = False) -> List[FileMetadata]:
        """List files in storage"""
        pass
    
    @abstractmethod
    async def get_file_metadata(self, remote_path: str) -> Optional[FileMetadata]:
        """Get file metadata"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name"""
        pass

class GoogleDriveProvider(StorageProviderInterface):
    """Google Drive storage provider"""
    
    def __init__(self, config: StorageConfig):
        if not GDRIVE_AVAILABLE:
            raise ImportError("Google Drive API libraries are required")
        
        self.config = config
        self.service = None
        self.folder_id = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Drive service"""
        try:
            credentials = None
            
            # Load credentials from different sources
            if 'service_account_file' in self.config.credentials:
                # Service account authentication
                from google.oauth2 import service_account
                credentials = service_account.Credentials.from_service_account_file(
                    self.config.credentials['service_account_file'],
                    scopes=['https://www.googleapis.com/auth/drive']
                )
            elif 'token_file' in self.config.credentials:
                # OAuth token authentication
                if os.path.exists(self.config.credentials['token_file']):
                    with open(self.config.credentials['token_file'], 'rb') as token:
                        credentials = pickle.load(token)
            
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    # OAuth flow for user authentication
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.credentials.get('client_secrets_file', 'credentials.json'),
                        ['https://www.googleapis.com/auth/drive']
                    )
                    credentials = flow.run_local_server(port=0)
                
                # Save credentials for future use
                if 'token_file' in self.config.credentials:
                    with open(self.config.credentials['token_file'], 'wb') as token:
                        pickle.dump(credentials, token)
            
            self.service = build('drive', 'v3', credentials=credentials)
            
            # Create or find the main folder
            if self.config.folder_path:
                self.folder_id = self._get_or_create_folder(self.config.folder_path)
            
            logger.info("Google Drive service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            raise
    
    def _get_or_create_folder(self, folder_name: str) -> str:
        """Get or create folder in Google Drive"""
        try:
            # Search for existing folder
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return folders[0]['id']
            else:
                # Create new folder
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                
                return folder.get('id')
                
        except Exception as e:
            logger.error(f"Failed to get/create folder {folder_name}: {e}")
            raise
    
    async def upload_file(self, local_path: str, remote_path: str, metadata: Optional[Dict[str, Any]] = None) -> FileMetadata:
        """Upload file to Google Drive"""
        try:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file not found: {local_path}")
            
            # Prepare file metadata
            file_name = os.path.basename(remote_path)
            mime_type, _ = mimetypes.guess_type(local_path)
            
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            # Add custom metadata if provided
            if metadata:
                file_metadata['description'] = json.dumps(metadata)
            
            # Upload file
            media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,mimeType,createdTime,modifiedTime,md5Checksum'
            ).execute()
            
            # Create FileMetadata object
            file_size = int(file.get('size', 0))
            created_date = datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00'))
            modified_date = datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00'))
            
            file_meta = FileMetadata(
                file_id=file['id'],
                name=file['name'],
                path=remote_path,
                size=file_size,
                mime_type=file.get('mimeType', mime_type or 'application/octet-stream'),
                created_date=created_date,
                modified_date=modified_date,
                checksum=file.get('md5Checksum', ''),
                storage_provider='google_drive',
                storage_path=file['id']
            )
            
            logger.info(f"File uploaded to Google Drive: {file_name} (ID: {file['id']})")
            return file_meta
            
        except Exception as e:
            logger.error(f"Failed to upload file to Google Drive: {e}")
            raise
    
    async def download_file(self, remote_path: str, local_path: str) -> str:
        """Download file from Google Drive"""
        try:
            # Find file by name or ID
            if remote_path.startswith('drive_id:'):
                file_id = remote_path.replace('drive_id:', '')
            else:
                file_id = await self._find_file_id(remote_path)
            
            if not file_id:
                raise FileNotFoundError(f"File not found in Google Drive: {remote_path}")
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            
            logger.info(f"File downloaded from Google Drive: {remote_path} -> {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download file from Google Drive: {e}")
            raise
    
    async def _find_file_id(self, file_name: str) -> Optional[str]:
        """Find file ID by name"""
        try:
            query = f"name='{file_name}'"
            if self.folder_id:
                query += f" and '{self.folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            return files[0]['id'] if files else None
            
        except Exception as e:
            logger.error(f"Failed to find file ID: {e}")
            return None
    
    async def delete_file(self, remote_path: str) -> bool:
        """Delete file from Google Drive"""
        try:
            file_id = await self._find_file_id(remote_path)
            if not file_id:
                logger.warning(f"File not found for deletion: {remote_path}")
                return False
            
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"File deleted from Google Drive: {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file from Google Drive: {e}")
            return False
    
    async def list_files(self, folder_path: str = "", recursive: bool = False) -> List[FileMetadata]:
        """List files in Google Drive"""
        try:
            query = "trashed=false"
            if self.folder_id:
                query += f" and '{self.folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id,name,size,mimeType,createdTime,modifiedTime,md5Checksum)"
            ).execute()
            
            files = results.get('files', [])
            file_list = []
            
            for file in files:
                file_size = int(file.get('size', 0))
                created_date = datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00'))
                modified_date = datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00'))
                
                file_meta = FileMetadata(
                    file_id=file['id'],
                    name=file['name'],
                    path=file['name'],
                    size=file_size,
                    mime_type=file.get('mimeType', 'application/octet-stream'),
                    created_date=created_date,
                    modified_date=modified_date,
                    checksum=file.get('md5Checksum', ''),
                    storage_provider='google_drive',
                    storage_path=file['id']
                )
                
                file_list.append(file_meta)
            
            return file_list
            
        except Exception as e:
            logger.error(f"Failed to list files from Google Drive: {e}")
            return []
    
    async def get_file_metadata(self, remote_path: str) -> Optional[FileMetadata]:
        """Get file metadata from Google Drive"""
        try:
            file_id = await self._find_file_id(remote_path)
            if not file_id:
                return None
            
            file = self.service.files().get(
                fileId=file_id,
                fields="id,name,size,mimeType,createdTime,modifiedTime,md5Checksum"
            ).execute()
            
            file_size = int(file.get('size', 0))
            created_date = datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00'))
            modified_date = datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00'))
            
            return FileMetadata(
                file_id=file['id'],
                name=file['name'],
                path=remote_path,
                size=file_size,
                mime_type=file.get('mimeType', 'application/octet-stream'),
                created_date=created_date,
                modified_date=modified_date,
                checksum=file.get('md5Checksum', ''),
                storage_provider='google_drive',
                storage_path=file['id']
            )
            
        except Exception as e:
            logger.error(f"Failed to get file metadata from Google Drive: {e}")
            return None
    
    def get_provider_name(self) -> str:
        return "Google Drive"

class GoogleCloudStorageProvider(StorageProviderInterface):
    """Google Cloud Storage provider"""
    
    def __init__(self, config: StorageConfig):
        if not GCS_AVAILABLE:
            raise ImportError("Google Cloud Storage libraries are required")
        
        self.config = config
        self.client = None
        self.bucket = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Cloud Storage client"""
        try:
            if 'service_account_file' in self.config.credentials:
                credentials = service_account.Credentials.from_service_account_file(
                    self.config.credentials['service_account_file']
                )
                self.client = gcs.Client(credentials=credentials)
            else:
                # Use default credentials
                self.client = gcs.Client()
            
            if self.config.bucket_name:
                self.bucket = self.client.bucket(self.config.bucket_name)
            
            logger.info("Google Cloud Storage client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Storage client: {e}")
            raise
    
    async def upload_file(self, local_path: str, remote_path: str, metadata: Optional[Dict[str, Any]] = None) -> FileMetadata:
        """Upload file to Google Cloud Storage"""
        try:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file not found: {local_path}")
            
            # Prepare blob path
            blob_path = remote_path
            if self.config.folder_path:
                blob_path = f"{self.config.folder_path.rstrip('/')}/{remote_path}"
            
            blob = self.bucket.blob(blob_path)
            
            # Set metadata
            if metadata:
                blob.metadata = metadata
            
            # Upload file
            with open(local_path, 'rb') as file_obj:
                blob.upload_from_file(file_obj)
            
            # Get file info
            blob.reload()
            file_size = blob.size
            created_date = blob.time_created
            modified_date = blob.updated
            checksum = blob.md5_hash
            
            file_meta = FileMetadata(
                file_id=blob.name,
                name=os.path.basename(remote_path),
                path=remote_path,
                size=file_size,
                mime_type=blob.content_type or 'application/octet-stream',
                created_date=created_date,
                modified_date=modified_date,
                checksum=checksum,
                storage_provider='google_cloud_storage',
                storage_path=blob_path
            )
            
            logger.info(f"File uploaded to Google Cloud Storage: {blob_path}")
            return file_meta
            
        except Exception as e:
            logger.error(f"Failed to upload file to Google Cloud Storage: {e}")
            raise
    
    async def download_file(self, remote_path: str, local_path: str) -> str:
        """Download file from Google Cloud Storage"""
        try:
            blob_path = remote_path
            if self.config.folder_path:
                blob_path = f"{self.config.folder_path.rstrip('/')}/{remote_path}"
            
            blob = self.bucket.blob(blob_path)
            
            if not blob.exists():
                raise FileNotFoundError(f"File not found in Google Cloud Storage: {blob_path}")
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as file_obj:
                blob.download_to_file(file_obj)
            
            logger.info(f"File downloaded from Google Cloud Storage: {blob_path} -> {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download file from Google Cloud Storage: {e}")
            raise
    
    async def delete_file(self, remote_path: str) -> bool:
        """Delete file from Google Cloud Storage"""
        try:
            blob_path = remote_path
            if self.config.folder_path:
                blob_path = f"{self.config.folder_path.rstrip('/')}/{remote_path}"
            
            blob = self.bucket.blob(blob_path)
            
            if not blob.exists():
                logger.warning(f"File not found for deletion: {blob_path}")
                return False
            
            blob.delete()
            logger.info(f"File deleted from Google Cloud Storage: {blob_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file from Google Cloud Storage: {e}")
            return False
    
    async def list_files(self, folder_path: str = "", recursive: bool = False) -> List[FileMetadata]:
        """List files in Google Cloud Storage"""
        try:
            prefix = folder_path
            if self.config.folder_path:
                prefix = f"{self.config.folder_path.rstrip('/')}/{folder_path}" if folder_path else self.config.folder_path
            
            blobs = self.bucket.list_blobs(prefix=prefix)
            file_list = []
            
            for blob in blobs:
                # Skip directories if not recursive
                if not recursive and '/' in blob.name.replace(prefix, '').lstrip('/'):
                    continue
                
                file_meta = FileMetadata(
                    file_id=blob.name,
                    name=os.path.basename(blob.name),
                    path=blob.name.replace(self.config.folder_path or '', '').lstrip('/'),
                    size=blob.size,
                    mime_type=blob.content_type or 'application/octet-stream',
                    created_date=blob.time_created,
                    modified_date=blob.updated,
                    checksum=blob.md5_hash,
                    storage_provider='google_cloud_storage',
                    storage_path=blob.name
                )
                
                file_list.append(file_meta)
            
            return file_list
            
        except Exception as e:
            logger.error(f"Failed to list files from Google Cloud Storage: {e}")
            return []
    
    async def get_file_metadata(self, remote_path: str) -> Optional[FileMetadata]:
        """Get file metadata from Google Cloud Storage"""
        try:
            blob_path = remote_path
            if self.config.folder_path:
                blob_path = f"{self.config.folder_path.rstrip('/')}/{remote_path}"
            
            blob = self.bucket.blob(blob_path)
            
            if not blob.exists():
                return None
            
            blob.reload()
            
            return FileMetadata(
                file_id=blob.name,
                name=os.path.basename(remote_path),
                path=remote_path,
                size=blob.size,
                mime_type=blob.content_type or 'application/octet-stream',
                created_date=blob.time_created,
                modified_date=blob.updated,
                checksum=blob.md5_hash,
                storage_provider='google_cloud_storage',
                storage_path=blob_path
            )
            
        except Exception as e:
            logger.error(f"Failed to get file metadata from Google Cloud Storage: {e}")
            return None
    
    def get_provider_name(self) -> str:
        return "Google Cloud Storage"

class LocalStorageProvider(StorageProviderInterface):
    """Local file system storage provider"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.base_path = config.folder_path or "/tmp/rfp_storage"
        os.makedirs(self.base_path, exist_ok=True)
        logger.info(f"Local storage initialized at: {self.base_path}")
    
    def _get_full_path(self, remote_path: str) -> str:
        """Get full local path"""
        return os.path.join(self.base_path, remote_path.lstrip('/'))
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def upload_file(self, local_path: str, remote_path: str, metadata: Optional[Dict[str, Any]] = None) -> FileMetadata:
        """Upload (copy) file to local storage"""
        try:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file not found: {local_path}")
            
            full_path = self._get_full_path(remote_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Copy file
            shutil.copy2(local_path, full_path)
            
            # Get file info
            stat = os.stat(full_path)
            file_size = stat.st_size
            created_date = datetime.fromtimestamp(stat.st_ctime)
            modified_date = datetime.fromtimestamp(stat.st_mtime)
            checksum = self._calculate_checksum(full_path)
            
            # Save metadata if provided
            if metadata:
                metadata_path = full_path + '.metadata'
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f)
            
            mime_type, _ = mimetypes.guess_type(full_path)
            
            file_meta = FileMetadata(
                file_id=remote_path,
                name=os.path.basename(remote_path),
                path=remote_path,
                size=file_size,
                mime_type=mime_type or 'application/octet-stream',
                created_date=created_date,
                modified_date=modified_date,
                checksum=checksum,
                storage_provider='local',
                storage_path=full_path
            )
            
            logger.info(f"File uploaded to local storage: {full_path}")
            return file_meta
            
        except Exception as e:
            logger.error(f"Failed to upload file to local storage: {e}")
            raise
    
    async def download_file(self, remote_path: str, local_path: str) -> str:
        """Download (copy) file from local storage"""
        try:
            full_path = self._get_full_path(remote_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found in local storage: {full_path}")
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            shutil.copy2(full_path, local_path)
            
            logger.info(f"File downloaded from local storage: {full_path} -> {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download file from local storage: {e}")
            raise
    
    async def delete_file(self, remote_path: str) -> bool:
        """Delete file from local storage"""
        try:
            full_path = self._get_full_path(remote_path)
            
            if not os.path.exists(full_path):
                logger.warning(f"File not found for deletion: {full_path}")
                return False
            
            os.remove(full_path)
            
            # Remove metadata file if exists
            metadata_path = full_path + '.metadata'
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            logger.info(f"File deleted from local storage: {full_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file from local storage: {e}")
            return False
    
    async def list_files(self, folder_path: str = "", recursive: bool = False) -> List[FileMetadata]:
        """List files in local storage"""
        try:
            search_path = self._get_full_path(folder_path)
            file_list = []
            
            if recursive:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.endswith('.metadata'):
                            continue
                        
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, self.base_path)
                        
                        file_meta = await self._get_file_metadata_from_path(full_path, relative_path)
                        if file_meta:
                            file_list.append(file_meta)
            else:
                if os.path.exists(search_path):
                    for item in os.listdir(search_path):
                        if item.endswith('.metadata'):
                            continue
                        
                        full_path = os.path.join(search_path, item)
                        if os.path.isfile(full_path):
                            relative_path = os.path.relpath(full_path, self.base_path)
                            file_meta = await self._get_file_metadata_from_path(full_path, relative_path)
                            if file_meta:
                                file_list.append(file_meta)
            
            return file_list
            
        except Exception as e:
            logger.error(f"Failed to list files from local storage: {e}")
            return []
    
    async def _get_file_metadata_from_path(self, full_path: str, relative_path: str) -> Optional[FileMetadata]:
        """Get file metadata from file path"""
        try:
            stat = os.stat(full_path)
            file_size = stat.st_size
            created_date = datetime.fromtimestamp(stat.st_ctime)
            modified_date = datetime.fromtimestamp(stat.st_mtime)
            checksum = self._calculate_checksum(full_path)
            mime_type, _ = mimetypes.guess_type(full_path)
            
            return FileMetadata(
                file_id=relative_path,
                name=os.path.basename(relative_path),
                path=relative_path,
                size=file_size,
                mime_type=mime_type or 'application/octet-stream',
                created_date=created_date,
                modified_date=modified_date,
                checksum=checksum,
                storage_provider='local',
                storage_path=full_path
            )
            
        except Exception as e:
            logger.error(f"Failed to get file metadata: {e}")
            return None
    
    async def get_file_metadata(self, remote_path: str) -> Optional[FileMetadata]:
        """Get file metadata from local storage"""
        try:
            full_path = self._get_full_path(remote_path)
            
            if not os.path.exists(full_path):
                return None
            
            return await self._get_file_metadata_from_path(full_path, remote_path)
            
        except Exception as e:
            logger.error(f"Failed to get file metadata from local storage: {e}")
            return None
    
    def get_provider_name(self) -> str:
        return "Local Storage"

class StorageManagementModule:
    """Main Storage Management Module - Orchestrates all storage providers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize storage providers
        self.providers = {}
        self.primary_provider = None
        self.backup_providers = []
        
        # Initialize providers based on configuration
        self._initialize_providers()
        
        # Operation tracking
        self.operations = {}
        self.operation_lock = threading.Lock()
        
        # File monitoring
        self.file_monitor = None
        if WATCHDOG_AVAILABLE and self.config.get('enable_file_monitoring', False):
            self._setup_file_monitoring()
        
        # Configuration
        self.enable_versioning = self.config.get('enable_versioning', True)
        self.enable_backup = self.config.get('enable_backup', True)
        self.enable_encryption = self.config.get('enable_encryption', False)
        self.max_concurrent_operations = self.config.get('max_concurrent_operations', 5)
        
        logger.info(f"Storage Management Module initialized with {len(self.providers)} providers")
        logger.info(f"Primary provider: {self.primary_provider.get_provider_name() if self.primary_provider else 'None'}")
    
    def _initialize_providers(self):
        """Initialize storage providers based on configuration"""
        provider_configs = self.config.get('providers', [])
        
        for provider_config in provider_configs:
            try:
                storage_config = StorageConfig(**provider_config)
                provider = self._create_provider(storage_config)
                
                if provider:
                    self.providers[storage_config.provider] = provider
                    
                    # Set primary provider
                    if provider_config.get('primary', False) or not self.primary_provider:
                        self.primary_provider = provider
                    
                    # Add to backup providers
                    if provider_config.get('backup', False):
                        self.backup_providers.append(provider)
                
            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_config.get('provider', 'unknown')}: {e}")
        
        # Fallback to local storage if no providers configured
        if not self.providers:
            local_config = StorageConfig(
                provider='local',
                credentials={},
                folder_path=self.config.get('local_storage_path', '/tmp/rfp_storage')
            )
            local_provider = LocalStorageProvider(local_config)
            self.providers['local'] = local_provider
            self.primary_provider = local_provider
    
    def _create_provider(self, config: StorageConfig) -> Optional[StorageProviderInterface]:
        """Create storage provider instance"""
        try:
            if config.provider == 'google_drive':
                return GoogleDriveProvider(config)
            elif config.provider == 'google_cloud_storage':
                return GoogleCloudStorageProvider(config)
            elif config.provider == 'local':
                return LocalStorageProvider(config)
            elif config.provider == 'aws_s3' and AWS_AVAILABLE:
                # Would implement AWS S3 provider here
                logger.warning("AWS S3 provider not implemented yet")
                return None
            else:
                logger.error(f"Unknown storage provider: {config.provider}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create provider {config.provider}: {e}")
            return None
    
    def _setup_file_monitoring(self):
        """Setup file system monitoring"""
        try:
            class FileChangeHandler(FileSystemEventHandler):
                def __init__(self, storage_module):
                    self.storage_module = storage_module
                
                def on_modified(self, event):
                    if not event.is_directory:
                        logger.info(f"File modified: {event.src_path}")
                        # Could trigger automatic backup or sync
                
                def on_created(self, event):
                    if not event.is_directory:
                        logger.info(f"File created: {event.src_path}")
                
                def on_deleted(self, event):
                    if not event.is_directory:
                        logger.info(f"File deleted: {event.src_path}")
            
            self.file_monitor = Observer()
            handler = FileChangeHandler(self)
            
            # Monitor local storage directory
            if 'local' in self.providers:
                local_provider = self.providers['local']
                self.file_monitor.schedule(handler, local_provider.base_path, recursive=True)
            
            self.file_monitor.start()
            logger.info("File monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to setup file monitoring: {e}")
    
    async def upload_file(self, local_path: str, remote_path: str, 
                         provider_name: Optional[str] = None, 
                         metadata: Optional[Dict[str, Any]] = None,
                         enable_backup: bool = None) -> Dict[str, Any]:
        """Upload file with optional backup to multiple providers"""
        operation_id = hashlib.md5(f"{local_path}_{remote_path}_{datetime.now()}".encode()).hexdigest()[:8]
        
        # Create operation tracking
        operation = StorageOperation(
            operation_id=operation_id,
            operation_type='upload',
            file_path=local_path,
            storage_provider=provider_name or self.primary_provider.get_provider_name(),
            start_time=datetime.now()
        )
        
        with self.operation_lock:
            self.operations[operation_id] = operation
        
        try:
            # Select provider
            provider = self.providers.get(provider_name) if provider_name else self.primary_provider
            if not provider:
                raise ValueError(f"Provider not available: {provider_name}")
            
            operation.status = 'in_progress'
            operation.progress = 0.1
            
            # Upload to primary provider
            file_metadata = await provider.upload_file(local_path, remote_path, metadata)
            operation.progress = 0.7
            
            results = {
                'primary': {
                    'provider': provider.get_provider_name(),
                    'success': True,
                    'metadata': file_metadata
                },
                'backups': []
            }
            
            # Upload to backup providers if enabled
            if (enable_backup if enable_backup is not None else self.enable_backup) and self.backup_providers:
                backup_tasks = []
                
                for backup_provider in self.backup_providers:
                    if backup_provider != provider:  # Don't backup to same provider
                        backup_tasks.append(self._backup_upload(backup_provider, local_path, remote_path, metadata))
                
                if backup_tasks:
                    backup_results = await asyncio.gather(*backup_tasks, return_exceptions=True)
                    
                    for i, result in enumerate(backup_results):
                        if isinstance(result, Exception):
                            results['backups'].append({
                                'provider': self.backup_providers[i].get_provider_name(),
                                'success': False,
                                'error': str(result)
                            })
                        else:
                            results['backups'].append({
                                'provider': self.backup_providers[i].get_provider_name(),
                                'success': True,
                                'metadata': result
                            })
            
            operation.status = 'completed'
            operation.progress = 1.0
            operation.end_time = datetime.now()
            
            logger.info(f"File upload completed: {remote_path} (Operation: {operation_id})")
            return {
                'operation_id': operation_id,
                'success': True,
                'results': results
            }
            
        except Exception as e:
            operation.status = 'failed'
            operation.error_message = str(e)
            operation.end_time = datetime.now()
            
            logger.error(f"File upload failed: {e} (Operation: {operation_id})")
            return {
                'operation_id': operation_id,
                'success': False,
                'error': str(e)
            }
    
    async def _backup_upload(self, provider: StorageProviderInterface, local_path: str, 
                           remote_path: str, metadata: Optional[Dict[str, Any]] = None) -> FileMetadata:
        """Upload file to backup provider"""
        try:
            return await provider.upload_file(local_path, remote_path, metadata)
        except Exception as e:
            logger.warning(f"Backup upload failed to {provider.get_provider_name()}: {e}")
            raise
    
    async def download_file(self, remote_path: str, local_path: str, 
                          provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Download file from storage"""
        operation_id = hashlib.md5(f"{remote_path}_{local_path}_{datetime.now()}".encode()).hexdigest()[:8]
        
        operation = StorageOperation(
            operation_id=operation_id,
            operation_type='download',
            file_path=remote_path,
            storage_provider=provider_name or self.primary_provider.get_provider_name(),
            start_time=datetime.now()
        )
        
        with self.operation_lock:
            self.operations[operation_id] = operation
        
        try:
            # Select provider
            provider = self.providers.get(provider_name) if provider_name else self.primary_provider
            if not provider:
                raise ValueError(f"Provider not available: {provider_name}")
            
            operation.status = 'in_progress'
            operation.progress = 0.1
            
            # Download file
            result_path = await provider.download_file(remote_path, local_path)
            
            operation.status = 'completed'
            operation.progress = 1.0
            operation.end_time = datetime.now()
            
            logger.info(f"File download completed: {remote_path} -> {local_path} (Operation: {operation_id})")
            return {
                'operation_id': operation_id,
                'success': True,
                'local_path': result_path,
                'provider': provider.get_provider_name()
            }
            
        except Exception as e:
            operation.status = 'failed'
            operation.error_message = str(e)
            operation.end_time = datetime.now()
            
            logger.error(f"File download failed: {e} (Operation: {operation_id})")
            return {
                'operation_id': operation_id,
                'success': False,
                'error': str(e)
            }
    
    async def delete_file(self, remote_path: str, provider_name: Optional[str] = None, 
                         delete_from_all: bool = False) -> Dict[str, Any]:
        """Delete file from storage"""
        operation_id = hashlib.md5(f"delete_{remote_path}_{datetime.now()}".encode()).hexdigest()[:8]
        
        operation = StorageOperation(
            operation_id=operation_id,
            operation_type='delete',
            file_path=remote_path,
            storage_provider=provider_name or 'all' if delete_from_all else self.primary_provider.get_provider_name(),
            start_time=datetime.now()
        )
        
        with self.operation_lock:
            self.operations[operation_id] = operation
        
        try:
            operation.status = 'in_progress'
            operation.progress = 0.1
            
            results = {}
            
            if delete_from_all:
                # Delete from all providers
                for name, provider in self.providers.items():
                    try:
                        success = await provider.delete_file(remote_path)
                        results[name] = {'success': success}
                    except Exception as e:
                        results[name] = {'success': False, 'error': str(e)}
            else:
                # Delete from specific provider
                provider = self.providers.get(provider_name) if provider_name else self.primary_provider
                if not provider:
                    raise ValueError(f"Provider not available: {provider_name}")
                
                success = await provider.delete_file(remote_path)
                results[provider.get_provider_name()] = {'success': success}
            
            operation.status = 'completed'
            operation.progress = 1.0
            operation.end_time = datetime.now()
            
            logger.info(f"File deletion completed: {remote_path} (Operation: {operation_id})")
            return {
                'operation_id': operation_id,
                'success': True,
                'results': results
            }
            
        except Exception as e:
            operation.status = 'failed'
            operation.error_message = str(e)
            operation.end_time = datetime.now()
            
            logger.error(f"File deletion failed: {e} (Operation: {operation_id})")
            return {
                'operation_id': operation_id,
                'success': False,
                'error': str(e)
            }
    
    async def list_files(self, folder_path: str = "", provider_name: Optional[str] = None, 
                        recursive: bool = False) -> List[FileMetadata]:
        """List files from storage"""
        try:
            provider = self.providers.get(provider_name) if provider_name else self.primary_provider
            if not provider:
                raise ValueError(f"Provider not available: {provider_name}")
            
            files = await provider.list_files(folder_path, recursive)
            logger.info(f"Listed {len(files)} files from {provider.get_provider_name()}")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    async def get_file_metadata(self, remote_path: str, provider_name: Optional[str] = None) -> Optional[FileMetadata]:
        """Get file metadata"""
        try:
            provider = self.providers.get(provider_name) if provider_name else self.primary_provider
            if not provider:
                raise ValueError(f"Provider not available: {provider_name}")
            
            metadata = await provider.get_file_metadata(remote_path)
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get file metadata: {e}")
            return None
    
    async def sync_files(self, source_provider: str, target_provider: str, 
                        folder_path: str = "") -> Dict[str, Any]:
        """Synchronize files between providers"""
        try:
            source = self.providers.get(source_provider)
            target = self.providers.get(target_provider)
            
            if not source or not target:
                raise ValueError("Source or target provider not available")
            
            # Get file lists
            source_files = await source.list_files(folder_path, recursive=True)
            target_files = await target.list_files(folder_path, recursive=True)
            
            # Create lookup for target files
            target_lookup = {f.path: f for f in target_files}
            
            sync_results = {
                'uploaded': [],
                'skipped': [],
                'errors': []
            }
            
            for source_file in source_files:
                try:
                    target_file = target_lookup.get(source_file.path)
                    
                    # Check if file needs to be synced
                    needs_sync = (
                        not target_file or
                        source_file.modified_date > target_file.modified_date or
                        source_file.checksum != target_file.checksum
                    )
                    
                    if needs_sync:
                        # Download from source and upload to target
                        with tempfile.NamedTemporaryFile() as temp_file:
                            await source.download_file(source_file.path, temp_file.name)
                            await target.upload_file(temp_file.name, source_file.path)
                        
                        sync_results['uploaded'].append(source_file.path)
                    else:
                        sync_results['skipped'].append(source_file.path)
                
                except Exception as e:
                    sync_results['errors'].append({
                        'file': source_file.path,
                        'error': str(e)
                    })
            
            logger.info(f"Sync completed: {len(sync_results['uploaded'])} uploaded, "
                       f"{len(sync_results['skipped'])} skipped, {len(sync_results['errors'])} errors")
            
            return sync_results
            
        except Exception as e:
            logger.error(f"File sync failed: {e}")
            return {'error': str(e)}
    
    async def create_backup(self, folder_path: str = "", backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create backup archive of files"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get files from primary provider
            files = await self.primary_provider.list_files(folder_path, recursive=True)
            
            if not files:
                return {'success': False, 'error': 'No files to backup'}
            
            # Create temporary directory for backup
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_dir = os.path.join(temp_dir, backup_name)
                os.makedirs(backup_dir, exist_ok=True)
                
                # Download all files
                downloaded_files = []
                for file_meta in files:
                    try:
                        local_path = os.path.join(backup_dir, file_meta.path)
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        
                        await self.primary_provider.download_file(file_meta.path, local_path)
                        downloaded_files.append(local_path)
                        
                    except Exception as e:
                        logger.warning(f"Failed to download file for backup: {file_meta.path}: {e}")
                
                # Create archive
                archive_path = os.path.join(temp_dir, f"{backup_name}.tar.gz")
                with tarfile.open(archive_path, 'w:gz') as tar:
                    tar.add(backup_dir, arcname=backup_name)
                
                # Upload archive to backup providers
                backup_results = []
                for backup_provider in self.backup_providers:
                    try:
                        archive_remote_path = f"backups/{backup_name}.tar.gz"
                        metadata = await backup_provider.upload_file(archive_path, archive_remote_path)
                        backup_results.append({
                            'provider': backup_provider.get_provider_name(),
                            'success': True,
                            'path': archive_remote_path,
                            'size': metadata.size
                        })
                    except Exception as e:
                        backup_results.append({
                            'provider': backup_provider.get_provider_name(),
                            'success': False,
                            'error': str(e)
                        })
                
                logger.info(f"Backup created: {backup_name} ({len(downloaded_files)} files)")
                return {
                    'success': True,
                    'backup_name': backup_name,
                    'files_count': len(downloaded_files),
                    'backup_results': backup_results
                }
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_operation_status(self, operation_id: str) -> Optional[StorageOperation]:
        """Get status of storage operation"""
        with self.operation_lock:
            return self.operations.get(operation_id)
    
    def get_all_operations(self) -> List[StorageOperation]:
        """Get all storage operations"""
        with self.operation_lock:
            return list(self.operations.values())
    
    def cleanup_completed_operations(self, older_than_hours: int = 24):
        """Clean up completed operations older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        with self.operation_lock:
            to_remove = []
            for op_id, operation in self.operations.items():
                if (operation.status in ['completed', 'failed'] and 
                    operation.end_time and operation.end_time < cutoff_time):
                    to_remove.append(op_id)
            
            for op_id in to_remove:
                del self.operations[op_id]
            
            logger.info(f"Cleaned up {len(to_remove)} completed operations")
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Get comprehensive storage status"""
        status = {
            'providers': {},
            'operations': {
                'total': len(self.operations),
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'failed': 0
            },
            'configuration': {
                'primary_provider': self.primary_provider.get_provider_name() if self.primary_provider else None,
                'backup_providers': [p.get_provider_name() for p in self.backup_providers],
                'versioning_enabled': self.enable_versioning,
                'backup_enabled': self.enable_backup,
                'encryption_enabled': self.enable_encryption,
                'file_monitoring_enabled': self.file_monitor is not None
            }
        }
        
        # Provider status
        for name, provider in self.providers.items():
            status['providers'][name] = {
                'name': provider.get_provider_name(),
                'available': True  # Could add health checks here
            }
        
        # Operation statistics
        with self.operation_lock:
            for operation in self.operations.values():
                status['operations'][operation.status] += 1
        
        return status
    
    async def test_providers(self) -> Dict[str, Any]:
        """Test all storage providers"""
        test_results = {}
        test_file_content = "This is a test file for storage provider validation."
        
        for name, provider in self.providers.items():
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Create test file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                    temp_file.write(test_file_content)
                    temp_file_path = temp_file.name
                
                try:
                    # Test upload
                    test_remote_path = f"test/storage_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    upload_metadata = await provider.upload_file(temp_file_path, test_remote_path)
                    
                    # Test download
                    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as download_file:
                        download_path = download_file.name
                    
                    await provider.download_file(test_remote_path, download_path)
                    
                    # Verify content
                    with open(download_path, 'r') as f:
                        downloaded_content = f.read()
                    
                    content_match = downloaded_content == test_file_content
                    
                    # Test metadata
                    metadata = await provider.get_file_metadata(test_remote_path)
                    
                    # Test list files
                    files = await provider.list_files("test/")
                    
                    # Test delete
                    delete_success = await provider.delete_file(test_remote_path)
                    
                    end_time = asyncio.get_event_loop().time()
                    
                    test_results[name] = {
                        'status': 'success',
                        'provider_name': provider.get_provider_name(),
                        'upload_success': True,
                        'download_success': True,
                        'content_match': content_match,
                        'metadata_available': metadata is not None,
                        'list_files_count': len(files),
                        'delete_success': delete_success,
                        'processing_time': end_time - start_time
                    }
                    
                finally:
                    # Cleanup
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                    if os.path.exists(download_path):
                        os.unlink(download_path)
                
            except Exception as e:
                test_results[name] = {
                    'status': 'failed',
                    'provider_name': provider.get_provider_name(),
                    'error': str(e)
                }
        
        return test_results
    
    def shutdown(self):
        """Shutdown storage module"""
        try:
            # Stop file monitoring
            if self.file_monitor:
                self.file_monitor.stop()
                self.file_monitor.join()
            
            # Clean up operations
            self.cleanup_completed_operations(0)  # Clean all
            
            logger.info("Storage Management Module shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Example usage and testing
async def main():
    """Example usage of Storage Management Module"""
    
    # Initialize module with multiple providers
    config = {
        'providers': [
            {
                'provider': 'local',
                'credentials': {},
                'folder_path': '/tmp/rfp_storage_test',
                'primary': True,
                'backup': False
            },
            # Uncomment and configure for Google Drive
            # {
            #     'provider': 'google_drive',
            #     'credentials': {
            #         'service_account_file': 'path/to/service-account.json'
            #     },
            #     'folder_path': 'RFP_Automation',
            #     'primary': False,
            #     'backup': True
            # },
            # Uncomment and configure for Google Cloud Storage
            # {
            #     'provider': 'google_cloud_storage',
            #     'credentials': {
            #         'service_account_file': 'path/to/service-account.json'
            #     },
            #     'bucket_name': 'rfp-automation-storage',
            #     'folder_path': 'documents',
            #     'primary': False,
            #     'backup': True
            # }
        ],
        'enable_versioning': True,
        'enable_backup': True,
        'enable_encryption': False,
        'enable_file_monitoring': False,
        'max_concurrent_operations': 5
    }
    
    storage_module = StorageManagementModule(config)
    
    # Show storage status
    print("Storage Status:")
    status = storage_module.get_storage_status()
    print(json.dumps(status, indent=2, default=str))
    
    # Test all providers
    print("\nTesting storage providers...")
    test_results = await storage_module.test_providers()
    print(json.dumps(test_results, indent=2, default=str))
    
    # Example file operations
    print("\nPerforming file operations...")
    
    # Create a test file
    test_content = """
    RFP Analysis Report
    ===================
    
    Organization: UNICEF
    Qualification Score: 92/100
    Recommendation: High Priority
    
    This is a sample RFP analysis report for testing storage functionality.
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(test_content)
        test_file_path = temp_file.name
    
    try:
        # Upload file
        print("Uploading test file...")
        upload_result = await storage_module.upload_file(
            test_file_path,
            'reports/test_rfp_analysis.txt',
            metadata={'type': 'rfp_analysis', 'organization': 'UNICEF'}
        )
        print(f"Upload result: {upload_result['success']}")
        
        if upload_result['success']:
            # List files
            print("Listing files...")
            files = await storage_module.list_files('reports/')
            print(f"Found {len(files)} files in reports/ folder")
            
            for file_meta in files:
                print(f"- {file_meta.name} ({file_meta.size} bytes, {file_meta.storage_provider})")
            
            # Get file metadata
            print("Getting file metadata...")
            metadata = await storage_module.get_file_metadata('reports/test_rfp_analysis.txt')
            if metadata:
                print(f"File metadata: {metadata.name}, {metadata.size} bytes, created {metadata.created_date}")
            
            # Download file
            print("Downloading file...")
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as download_file:
                download_path = download_file.name
            
            download_result = await storage_module.download_file(
                'reports/test_rfp_analysis.txt',
                download_path
            )
            
            if download_result['success']:
                with open(download_path, 'r') as f:
                    downloaded_content = f.read()
                print(f"Downloaded content length: {len(downloaded_content)} characters")
                print("Content matches:", downloaded_content.strip() == test_content.strip())
                os.unlink(download_path)
            
            # Create backup
            print("Creating backup...")
            backup_result = await storage_module.create_backup('reports/')
            print(f"Backup result: {backup_result.get('success', False)}")
            
            # Delete file
            print("Deleting test file...")
            delete_result = await storage_module.delete_file('reports/test_rfp_analysis.txt')
            print(f"Delete result: {delete_result['success']}")
    
    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
    
    # Show final operations status
    print("\nFinal operations status:")
    operations = storage_module.get_all_operations()
    for op in operations:
        print(f"- {op.operation_type} {op.file_path}: {op.status} ({op.progress:.1%})")
    
    # Shutdown
    storage_module.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
