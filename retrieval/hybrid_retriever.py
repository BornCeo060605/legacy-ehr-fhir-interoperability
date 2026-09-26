"""
Hybrid Evidence Retriever (Module 4).
Executes retrieval plans across exact terminology connectors,
authoritative FHIR R4 StructureDefinitions, and semantic vector stores.
Follows the evidence priority hierarchy: Exact > Structure > Vector.
"""

import logging
from typing import List, Dict, Any, Optional

from models.schemas import RetrievalPlan, RetrievalQuery, EvidenceItem
from terminology.ucum import UCUMValidator
from terminology.loinc import LOINCConnector
from terminology.rxnorm import RxNormConnector
from fhir.evidence_retriever import FHIREvidenceRetriever
from retrieval.vector_store import VectorSearchEngine

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Coordinates multi-source hybrid evidence retrieval for legacy EHR fields.
    """

    def __init__(
        self,
        ucum_validator: Optional[UCUMValidator] = None,
        loinc_connector: Optional[LOINCConnector] = None,
        rxnorm_connector: Optional[RxNormConnector] = None,
        fhir_retriever: Optional[FHIREvidenceRetriever] = None,
        vector_engine: Optional[VectorSearchEngine] = None,
    ):
        self.ucum = ucum_validator or UCUMValidator()
        self.loinc = loinc_connector or LOINCConnector()
        self.rxnorm = rxnorm_connector or RxNormConnector()
        self.fhir = fhir_retriever or FHIREvidenceRetriever()
        self.vector = vector_engine or VectorSearchEngine()

    def execute_plan(self, plan: RetrievalPlan) -> List[EvidenceItem]:
        """
        Execute all queries specified in the retrieval plan and return ranked evidence items.
        """
        evidence_list: List[EvidenceItem] = []
        seen_ids = set()

        for q in plan.queries:
            items: List[EvidenceItem] = []

            # 1. UCUM Exact Unit Queries
            if q.source == "UCUM" and q.query_type == "EXACT_UNIT":
                ev = self.ucum.validate_unit(q.query_string)
                if ev:
                    items.append(ev)

            # 2. LOINC Exact Code Queries
            elif q.source == "LOINC" and q.query_type == "EXACT_CODE":
                ev = self.loinc.lookup_code(q.query_string)
                if ev:
                    items.append(ev)

            # 3. RxNorm API Queries
            elif q.source == "RxNorm" and q.query_type == "API_LOOKUP":
                ev = self.rxnorm.lookup_rxcui(q.query_string)
                if ev:
                    items.append(ev)

            # 4. FHIR R4 Structural Searches
            elif q.source == "FHIR_R4" and q.query_type == "STRUCTURAL_SEARCH":
                # Check if exact path
                ev_exact = self.fhir.lookup_element(q.query_string)
                if ev_exact:
                    items.append(ev_exact)
                else:
                    # Keyword search
                    items.extend(self.fhir.search_elements(q.query_string, top_k=3))

            # 5. Semantic Vector Searches
            elif q.query_type == "VECTOR_SEMANTIC":
                col_name = "ohdsi_vectors" if q.source == "OHDSI" else (
                    "loinc_vectors" if q.source == "LOINC" else "fhir_r4_vectors"
                )
                items.extend(self.vector.search_collection(col_name, q.query_string, top_k=2))

            # Deduplicate by evidence_id
            for it in items:
                if it.evidence_id not in seen_ids:
                    seen_ids.add(it.evidence_id)
                    evidence_list.append(it)

        # Sort evidence by reliability hierarchy:
        # EXACT_LOOKUP & API_CALL (score 1.0) > FHIR_STRUCTURE (score 0.8-1.0) > VECTOR_SEARCH
        method_priority = {
            "EXACT_LOOKUP": 4,
            "API_CALL": 4,
            "FHIR_STRUCTURE": 3,
            "DIRECT_PROFILING": 2,
            "VECTOR_SEARCH": 1,
        }
        evidence_list.sort(
            key=lambda e: (method_priority.get(e.retrieval_method, 0), e.score),
            reverse=True,
        )

        return evidence_list
