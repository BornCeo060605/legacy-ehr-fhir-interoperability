"""
Healthcare Knowledge Resources Monitoring Service.
Inspects local caches, checksums, and availability of clinical terminologies and FHIR R4 specs.
"""

from typing import List, Dict, Any
from resources.resource_manager import ResourceManager
from app.schemas.api_schemas import KnowledgeResourceItem


class ResourceService:

    @staticmethod
    def get_resource_statuses() -> List[KnowledgeResourceItem]:
        manager = ResourceManager()
        manifests = manager.get_all_manifests()
        items = []

        for res_id, manifest in manifests.items():
            status_mapped = "AVAILABLE" if manifest.availability in ["AVAILABLE", "CONFIGURED", "AVAILABLE (RAW ONLY)"] else "DEGRADED" if "AUTH" in manifest.availability else "UNAVAILABLE"
            items.append(
                KnowledgeResourceItem(
                    resource_id=res_id,
                    name=manifest.name,
                    version=manifest.version,
                    category=manifest.resource_type,
                    status=status_mapped,
                    description=manifest.details or manifest.source_url,
                    record_count=manifest.record_count,
                    checksum_sha256=manifest.checksum_sha256[:12] + "..." if manifest.checksum_sha256 else None,
                    local_path=manifest.local_path,
                    details={"source_url": manifest.source_url, "details": manifest.details, "availability": manifest.availability},
                )
            )

        return items
