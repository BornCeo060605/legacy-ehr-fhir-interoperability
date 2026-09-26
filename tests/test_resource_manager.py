"""
Unit tests for Healthcare Knowledge Resource Manager (Section 17).
Verifies detection of FHIR R4, UCUM, LOINC, RxNorm, and graceful fallback for SNOMED CT.
"""

import pytest
from resources.resource_manager import ResourceManager, KnowledgeResource


def test_resource_manager_manifests():
    mgr = ResourceManager()
    manifests = mgr.get_all_manifests()

    assert "FHIR_R4" in manifests
    assert "LOINC" in manifests
    assert "UCUM" in manifests
    assert "RxNorm" in manifests
    assert "SNOMED_CT" in manifests
    assert "OHDSI" in manifests

    # Check UCUM
    ucum = manifests["UCUM"]
    assert ucum.name == "UCUM"
    assert ucum.availability == "AVAILABLE"
    assert ucum.checksum_sha256 is not None

    # Check FHIR R4
    fhir = manifests["FHIR_R4"]
    assert fhir.name == "FHIR R4"
    assert fhir.version == "4.0.1"
    assert fhir.availability == "AVAILABLE"

    # Check SNOMED CT fallback
    snomed = manifests["SNOMED_CT"]
    assert snomed.availability in ["CONFIGURED", "NOT CONFIGURED"]
