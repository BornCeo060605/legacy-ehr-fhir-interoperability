from typing import List
from fastapi import APIRouter
from app.schemas.api_schemas import KnowledgeResourceItem
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/api/resources", tags=["Knowledge Resources"])


@router.get("", response_model=List[KnowledgeResourceItem])
def list_resources():
    return ResourceService.get_resource_statuses()
