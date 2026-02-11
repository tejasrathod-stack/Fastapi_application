from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Create router instead of new FastAPI app
router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)

# Log model
class AuditLog(BaseModel):
    id: int
    action: str
    entity: str
    timestamp: datetime

# In-memory audit storage
audit_logs: List[AuditLog] = []
audit_id_counter = 1

# Function to create audit log (you can import and use this)
def create_audit_log(action: str, entity: str):
    global audit_id_counter
    new_log = AuditLog(
        id=audit_id_counter,
        action=action,
        entity=entity,
        timestamp=datetime.now()
    )
    audit_logs.append(new_log)
    audit_id_counter += 1


# Endpoint to get all audit logs
@router.get("/", response_model=List[AuditLog])
async def get_audit_logs():
    return audit_logs


# Endpoint to clear audit logs
@router.delete("/clear", status_code=204)
async def clear_logs():
    audit_logs.clear()
    global audit_id_counter
    audit_id_counter = 1
