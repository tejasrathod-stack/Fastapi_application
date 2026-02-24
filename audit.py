from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Create router
router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)

# ============================
# Model
# ============================

class AuditLog(BaseModel):
    id: int
    action: str
    entity: str
    timestamp: datetime


# ============================
# In-Memory Storage (Demo)
# ============================

audit_logs: List[AuditLog] = []
audit_id_counter = 1


# ============================
# Utility Function (Importable)
# ============================

def create_audit_log(action: str, entity: str) -> AuditLog:
    global audit_id_counter

    new_log = AuditLog(
        id=audit_id_counter,
        action=action,
        entity=entity,
        timestamp=datetime.utcnow()
    )

    audit_logs.append(new_log)
    audit_id_counter += 1

    return new_log


# ============================
# Endpoints
# ============================

@router.get("/", response_model=List[AuditLog])
async def get_audit_logs():
    return audit_logs


@router.delete("/clear", status_code=204)
async def clear_logs():
    global audit_id_counter

    audit_logs.clear()
    audit_id_counter = 1
