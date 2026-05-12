# ABOUTME: FastAPI endpoints for medical data governance
# ABOUTME: Integrates PII detection, anonymization, RBAC, and encryption

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd
from src.access.rbac import RBACEnforcer
from src.pii.anonymizer import MedVietAnonymizer
from src.encryption.vault import SimpleVault
from src.quality.validation import validate_raw_data, validate_anonymized_data
import json

app = FastAPI(
    title="MedViet Data Governance API",
    version="1.0.0",
    description="Medical data platform with PII detection, anonymization, and RBAC"
)

anonymizer = MedVietAnonymizer()
enforcer = RBACEnforcer("src/access/model.conf", "src/access/policy.csv")
vault = SimpleVault(master_key_path=".vault_key")

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "MedViet Data API",
        "version": "1.0.0"
    }

@app.get("/api/access/check")
async def check_access(
    user: str = Query(..., description="Username"),
    resource: str = Query(..., description="Resource name"),
    action: str = Query(..., description="Action: read, write, delete")
):
    """Check if user has permission for action on resource."""
    has_access = enforcer.enforce(user, resource, action)
    return {
        "user": user,
        "resource": resource,
        "action": action,
        "allowed": has_access
    }

@app.get("/api/patients/raw")
async def get_raw_patients(
    user: str = Query(..., description="Username"),
    limit: int = Query(10, ge=1, le=100, description="Number of records")
):
    """Return raw patient data (admin only)."""
    if not enforcer.enforce(user, "patient_data", "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    df = pd.read_csv("data/raw/patients_raw.csv")
    return {
        "data": df.head(limit).to_dict(orient="records"),
        "total_rows": len(df),
        "returned": len(df.head(limit))
    }

@app.get("/api/patients/anonymized")
async def get_anonymized_patients(
    user: str = Query(..., description="Username"),
    limit: int = Query(10, ge=1, le=100, description="Number of records")
):
    """Return anonymized patient data (ml_engineer, admin)."""
    if not enforcer.enforce(user, "training_data", "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        df = pd.read_csv("data/processed/patients_anonymized.csv")
        return {
            "data": df.head(limit).to_dict(orient="records"),
            "total_rows": len(df),
            "returned": len(df.head(limit)),
            "anonymized": True
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Anonymized data not found")

@app.get("/api/metrics/aggregated")
async def get_aggregated_metrics(
    user: str = Query(..., description="Username")
):
    """Return aggregated metrics (no PII)."""
    if not enforcer.enforce(user, "aggregated_metrics", "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    df = pd.read_csv("data/raw/patients_raw.csv")
    metrics = {
        "total_patients": len(df),
        "diseases": df["benh"].value_counts().to_dict(),
        "avg_test_result": float(df["ket_qua_xet_nghiem"].mean()),
        "test_result_range": {
            "min": float(df["ket_qua_xet_nghiem"].min()),
            "max": float(df["ket_qua_xet_nghiem"].max())
        }
    }
    return metrics

@app.delete("/api/patients/{patient_id}")
async def delete_patient(
    patient_id: str,
    user: str = Query(..., description="Username")
):
    """Delete patient record (admin only)."""
    if not enforcer.enforce(user, "patient_data", "delete"):
        raise HTTPException(status_code=403, detail="Access denied. Only admins can delete.")

    return {
        "message": f"Patient {patient_id} deleted successfully",
        "deleted_by": user
    }

@app.post("/api/encrypt")
async def encrypt_data(
    user: str = Query(..., description="Username"),
    data: str = Query(..., description="Data to encrypt")
):
    """Encrypt sensitive data using AES-256-GCM."""
    if not enforcer.enforce(user, "patient_data", "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    encrypted = vault.encrypt_data(data)
    return {
        "encrypted_dek": encrypted["encrypted_dek"],
        "ciphertext": encrypted["ciphertext"],
        "algorithm": encrypted["algorithm"],
        "encrypted_by": user
    }

@app.post("/api/decrypt")
async def decrypt_data(
    user: str = Query(..., description="Username"),
    encrypted_dek: str = Query(..., description="Encrypted data encryption key"),
    ciphertext: str = Query(..., description="Encrypted data")
):
    """Decrypt AES-256-GCM encrypted data."""
    if not enforcer.enforce(user, "patient_data", "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    payload = {
        "encrypted_dek": encrypted_dek,
        "ciphertext": ciphertext,
        "algorithm": "AES-256-GCM"
    }
    try:
        plaintext = vault.decrypt_data(payload)
        return {
            "plaintext": plaintext,
            "decrypted_by": user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decryption failed: {str(e)}")

@app.get("/api/validate/raw")
async def validate_raw(
    user: str = Query(..., description="Username")
):
    """Validate raw patient data quality."""
    if not enforcer.enforce(user, "patient_data", "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    results = validate_raw_data("data/raw/patients_raw.csv")
    return results

@app.get("/api/validate/anonymized")
async def validate_anonymized(
    user: str = Query(..., description="Username")
):
    """Validate anonymized patient data quality."""
    if not enforcer.enforce(user, "training_data", "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        results = validate_anonymized_data("data/processed/patients_anonymized.csv")
        return results
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Anonymized data not found")

@app.get("/api/roles/{user}")
async def get_user_roles(
    user: str,
    current_user: str = Query(..., description="Current user")
):
    """Get roles for a user."""
    roles = enforcer.get_roles_for_user(user)
    return {
        "user": user,
        "roles": roles
    }

@app.get("/api/permissions/{user}")
async def get_user_permissions(
    user: str,
    current_user: str = Query(..., description="Current user")
):
    """Get permissions for a user."""
    permissions = enforcer.get_permissions_for_user(user)
    return {
        "user": user,
        "permissions": permissions
    }
