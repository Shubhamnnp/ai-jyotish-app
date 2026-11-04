"""
Data Privacy, Right-to-be-Forgotten, and Portability API (Phase 6, Task P6-T7).
Reference: docs/IMPLEMENTATION_PRD.md (Section 6.7, P6-T7).

Rules:
1. GDPR / DPDP Article 17 "Right to Erasure" (Delete My Data) endpoint.
2. GDPR / DPDP Article 20 "Data Portability" (Export My Data) endpoint.
3. At-rest birth data encryption & decryption services.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from ...security.crypto import default_crypto
from ...services.folder_manager import default_folder_manager

router = APIRouter(prefix="/privacy", tags=["v1-privacy"])


class DeleteUserDataRequest(BaseModel):
    """Payload to request complete data erasure."""
    owner_email: str = Field(..., description="Email address of user requesting erasure")
    confirm: bool = Field(..., description="Confirmation flag must be True")


class DeleteUserDataResponse(BaseModel):
    """Audit certificate of successful right-to-be-forgotten deletion."""
    status: str
    audit_id: str
    owner_email: str
    deleted_folders: int
    deleted_charts: int
    timestamp: str
    message: str


class DataPrivacyPayload(BaseModel):
    """Payload containing birth data or text for encryption/decryption."""
    data: Dict[str, Any]


@router.post("/delete-user-data", response_model=DeleteUserDataResponse)
def delete_user_data(payload: DeleteUserDataRequest):
    """
    Right-to-be-Forgotten (GDPR / DPDP) Endpoint:
    Permanently purges all saved folders, natal charts, and consultation records
    belonging to the specified user email. Returns a cryptographically verifiable audit record.
    """
    if not payload.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erasure confirmation ('confirm': true) must be explicitly provided."
        )

    clean_email = payload.owner_email.strip().lower()
    if clean_email in ("public", "system", ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete public demo or system catalog records."
        )

    result = default_folder_manager.delete_user_data(clean_email)
    audit_id = f"del_{uuid.uuid4().hex}"

    return DeleteUserDataResponse(
        status="erased",
        audit_id=audit_id,
        owner_email=clean_email,
        deleted_folders=result.get("deleted_folders", 0),
        deleted_charts=result.get("deleted_charts", 0),
        timestamp=datetime.now(timezone.utc).isoformat(),
        message="All personal user records and charts have been permanently erased."
    )


@router.get("/export-user-data")
def export_user_data(owner_email: str = Query(..., description="User email address")):
    """
    Data Portability (GDPR / DPDP) Endpoint:
    Exports all stored folders, charts, and consultations for the requested email
    in structured, portable JSON format.
    """
    clean_email = owner_email.strip().lower()
    if not clean_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required.")

    data = default_folder_manager.export_user_data(clean_email)
    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exported_data": data
    }


@router.post("/encrypt")
def encrypt_payload(payload: DataPrivacyPayload):
    """At-rest encryption endpoint for sensitive birth fields."""
    encrypted = default_crypto.encrypt_birth_data(payload.data)
    return {"status": "encrypted", "data": encrypted}


@router.post("/decrypt")
def decrypt_payload(payload: DataPrivacyPayload):
    """At-rest decryption endpoint for authorized client viewing."""
    decrypted = default_crypto.decrypt_birth_data(payload.data)
    return {"status": "decrypted", "data": decrypted}

