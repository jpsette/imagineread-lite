"""
Transfer Service
Manages transfer metadata in database (Firestore or local JSON for dev).
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from loguru import logger

from app.config import ENVIRONMENT, TEMP_DIR, FREE_EXPIRY_HOURS


class Transfer:
    """Transfer model."""
    
    def __init__(
        self,
        code: str,
        original_name: str,
        file_type: str,
        file_size_bytes: int,
        storage_path: str,
        is_premium: bool = False,
        user_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        download_count: int = 0
    ):
        self.code = code
        self.original_name = original_name
        self.file_type = file_type
        self.file_size_bytes = file_size_bytes
        self.storage_path = storage_path
        self.is_premium = is_premium
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
        
        # Set expiry for free tier
        if expires_at is None and not is_premium:
            self.expires_at = self.created_at + timedelta(hours=FREE_EXPIRY_HOURS)
        else:
            self.expires_at = expires_at
        
        self.download_count = download_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "originalName": self.original_name,
            "fileType": self.file_type,
            "fileSizeBytes": self.file_size_bytes,
            "storagePath": self.storage_path,
            "isPremium": self.is_premium,
            "userId": self.user_id,
            "createdAt": self.created_at.isoformat(),
            "expiresAt": self.expires_at.isoformat() if self.expires_at else None,
            "downloadCount": self.download_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transfer":
        """Create from dictionary."""
        created_at = datetime.fromisoformat(data["createdAt"]) if data.get("createdAt") else None
        expires_at = datetime.fromisoformat(data["expiresAt"]) if data.get("expiresAt") else None
        
        return cls(
            code=data["code"],
            original_name=data["originalName"],
            file_type=data["fileType"],
            file_size_bytes=data["fileSizeBytes"],
            storage_path=data["storagePath"],
            is_premium=data.get("isPremium", False),
            user_id=data.get("userId"),
            created_at=created_at,
            expires_at=expires_at,
            download_count=data.get("downloadCount", 0)
        )
    
    def is_expired(self) -> bool:
        """Check if transfer is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class LocalTransferService:
    """Local JSON-based transfer service for development."""
    
    def __init__(self):
        self.db_path = TEMP_DIR / "transfers.json"
        self._ensure_db()
        logger.info(f"📁 LocalTransferService initialized: {self.db_path}")
    
    def _ensure_db(self):
        """Ensure database file exists."""
        if not self.db_path.exists():
            self.db_path.write_text("{}")
    
    def _load_db(self) -> Dict[str, Dict]:
        """Load database from file."""
        try:
            return json.loads(self.db_path.read_text())
        except json.JSONDecodeError:
            return {}
    
    def _save_db(self, data: Dict[str, Dict]):
        """Save database to file."""
        self.db_path.write_text(json.dumps(data, indent=2))
    
    def create(self, transfer: Transfer) -> Transfer:
        """Create a new transfer."""
        db = self._load_db()
        db[transfer.code] = transfer.to_dict()
        self._save_db(db)
        logger.info(f"📝 Created transfer: {transfer.code}")
        return transfer
    
    def get(self, code: str) -> Optional[Transfer]:
        """Get transfer by code."""
        db = self._load_db()
        data = db.get(code)
        
        if not data:
            return None
        
        return Transfer.from_dict(data)
    
    def exists(self, code: str) -> bool:
        """Check if code exists."""
        db = self._load_db()
        return code in db
    
    def increment_download_count(self, code: str) -> bool:
        """Increment download count."""
        db = self._load_db()
        
        if code not in db:
            return False
        
        db[code]["downloadCount"] = db[code].get("downloadCount", 0) + 1
        self._save_db(db)
        return True
    
    def delete(self, code: str) -> bool:
        """Delete transfer."""
        db = self._load_db()
        
        if code in db:
            del db[code]
            self._save_db(db)
            logger.info(f"🗑️ Deleted transfer: {code}")
            return True
        
        return False
    
    def get_expired(self) -> List[Transfer]:
        """Get all expired transfers."""
        db = self._load_db()
        expired = []
        
        for data in db.values():
            transfer = Transfer.from_dict(data)
            if transfer.is_expired():
                expired.append(transfer)
        
        return expired
    
    def get_all_codes(self) -> set:
        """Get all existing codes."""
        db = self._load_db()
        return set(db.keys())


class FirestoreTransferService:
    """Firestore-based transfer service for production."""
    
    def __init__(self):
        try:
            from google.cloud import firestore
            self.db = firestore.Client()
            self.collection = self.db.collection("transfers")
            logger.info("☁️ FirestoreTransferService initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firestore: {e}")
            raise
    
    def create(self, transfer: Transfer) -> Transfer:
        """Create a new transfer."""
        self.collection.document(transfer.code).set(transfer.to_dict())
        logger.info(f"☁️ Created transfer in Firestore: {transfer.code}")
        return transfer
    
    def get(self, code: str) -> Optional[Transfer]:
        """Get transfer by code."""
        doc = self.collection.document(code).get()
        
        if not doc.exists:
            return None
        
        return Transfer.from_dict(doc.to_dict())
    
    def exists(self, code: str) -> bool:
        """Check if code exists."""
        doc = self.collection.document(code).get()
        return doc.exists
    
    def increment_download_count(self, code: str) -> bool:
        """Increment download count."""
        from google.cloud import firestore
        
        doc_ref = self.collection.document(code)
        doc_ref.update({"downloadCount": firestore.Increment(1)})
        return True
    
    def delete(self, code: str) -> bool:
        """Delete transfer."""
        self.collection.document(code).delete()
        logger.info(f"☁️ Deleted transfer from Firestore: {code}")
        return True
    
    def get_expired(self) -> List[Transfer]:
        """Get all expired transfers."""
        now = datetime.utcnow()
        
        query = self.collection.where("expiresAt", "<=", now.isoformat())
        docs = query.stream()
        
        return [Transfer.from_dict(doc.to_dict()) for doc in docs]
    
    def get_all_codes(self) -> set:
        """Get all existing codes."""
        docs = self.collection.stream()
        return {doc.id for doc in docs}


def get_transfer_service():
    """Factory function to get transfer service."""
    if ENVIRONMENT == "development":
        return LocalTransferService()
    else:
        return FirestoreTransferService()


# Singleton instance
_transfer_service = None


def get_transfers():
    """Get singleton transfer service instance."""
    global _transfer_service
    if _transfer_service is None:
        _transfer_service = get_transfer_service()
    return _transfer_service
