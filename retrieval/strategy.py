"""
Deterministic Retrieval Strategy Planner (Module 3).
Plans external evidence searches for each legacy field based on profiling and semantic role.
Strictly records included sources, excluded sources, and exclusion justifications.
Never invents sources or queries without evidence.
"""

from typing import List, Dict, Any, Optional
from models.schemas import (
    ColumnFact,
    SemanticRole,
    RetrievalPlan,
    RetrievalQuery,
)


class RetrievalStrategyPlanner:
    """
    Deterministic planner that constructs evidence retrieval plans.
    """

    ALL_SOURCES = ["FHIR_R4", "LOINC", "UCUM", "RxNorm", "SNOMED_CT", "OHDSI"]

    def plan_retrieval(
        self,
        column_fact: ColumnFact,
        role: SemanticRole,
    ) -> RetrievalPlan:
        """
        Produce a deterministic retrieval plan for a legacy column.
        """
        tbl = column_fact.table_name.upper()
        col = column_fact.column_name.upper()
        role_cat = role.role_category
        term = role.candidate_terminology

        included_sources = []
        excluded_sources = []
        exclusion_reasons = {}
        queries: List[RetrievalQuery] = []

        # 1. 100% NULL or UNKNOWN fields
        if role_cat == "unknown" or column_fact.null_count == column_fact.row_count:
            included_sources = ["FHIR_R4"]
            excluded_sources = ["LOINC", "UCUM", "RxNorm", "SNOMED_CT", "OHDSI"]
            for s in excluded_sources:
                exclusion_reasons[s] = "Field contains 100% missing values; terminology lookup inapplicable."
            
            queries.append(
                RetrievalQuery(
                    source="FHIR_R4",
                    query_type="STRUCTURAL_SEARCH",
                    query_string=f"{tbl} {col}",
                    priority=3,
                    reasoning=f"Search for potential optional element corresponding to column name '{col}'."
                )
            )
            return RetrievalPlan(
                table_name=column_fact.table_name,
                column_name=column_fact.column_name,
                included_sources=included_sources,
                excluded_sources=excluded_sources,
                exclusion_reasons=exclusion_reasons,
                queries=queries,
                justification="Minimal retrieval plan for unpopulated legacy attribute.",
            )

        # 2. Measurement Unit (UCUM)
        if role_cat == "measurement_unit" or term == "UCUM" or "UNIT" in col:
            included_sources = ["UCUM", "FHIR_R4"]
            excluded_sources = ["LOINC", "RxNorm", "SNOMED_CT", "OHDSI"]
            for s in excluded_sources:
                exclusion_reasons[s] = "Field represents physical measurement units; clinical concept vocabularies excluded."

            for sample_unit in column_fact.sample_values[:5]:
                if sample_unit and sample_unit.strip():
                    queries.append(
                        RetrievalQuery(
                            source="UCUM",
                            query_type="EXACT_UNIT",
                            query_string=sample_unit.strip(),
                            priority=1,
                            reasoning=f"Verify validity and canonical representation of unit token '{sample_unit}' in UCUM essence."
                        )
                    )

            queries.append(
                RetrievalQuery(
                    source="FHIR_R4",
                    query_type="STRUCTURAL_SEARCH",
                    query_string="Observation.valueQuantity.unit",
                    priority=2,
                    reasoning="Retrieve FHIR Quantity unit bindings and system requirements."
                )
            )
            return RetrievalPlan(
                table_name=column_fact.table_name,
                column_name=column_fact.column_name,
                included_sources=included_sources,
                excluded_sources=excluded_sources,
                exclusion_reasons=exclusion_reasons,
                queries=queries,
                justification="Unit validation plan combining deterministic UCUM essence checks with FHIR valueQuantity structural element.",
            )

        # 3. Lab / Vital Terminology Code (LOINC)
        if term == "LOINC" or (role_cat == "terminology_code" and any(k in tbl or k in col for k in ["VITAL", "OBS", "LAB", "LOINC"])):
            included_sources = ["LOINC", "FHIR_R4", "OHDSI"]
            excluded_sources = ["UCUM", "RxNorm", "SNOMED_CT"]
            exclusion_reasons["UCUM"] = "Observation codes represent test concepts, not units of measure."
            exclusion_reasons["RxNorm"] = "Medication vocabulary not applicable to clinical observations."
            exclusion_reasons["SNOMED_CT"] = "Primary coding system for quantitative lab and vital measurements is LOINC."

            for sample_code in column_fact.sample_values[:5]:
                if sample_code and sample_code.strip():
                    queries.append(
                        RetrievalQuery(
                            source="LOINC",
                            query_type="EXACT_CODE",
                            query_string=sample_code.strip(),
                            priority=1,
                            reasoning=f"Exact lookup for clinical observation code '{sample_code}' in official LOINC table."
                        )
                    )

            queries.append(
                RetrievalQuery(
                    source="FHIR_R4",
                    query_type="STRUCTURAL_SEARCH",
                    query_string="Observation.code",
                    priority=2,
                    reasoning="Retrieve Observation.code binding and CodeableConcept structure."
                )
            )
            queries.append(
                RetrievalQuery(
                    source="LOINC",
                    query_type="VECTOR_SEMANTIC",
                    query_string=f"{tbl} {col} observation vital sign",
                    priority=3,
                    reasoning="Vector semantic search for observation concept context in LOINC vector collection."
                )
            )
            return RetrievalPlan(
                table_name=column_fact.table_name,
                column_name=column_fact.column_name,
                included_sources=included_sources,
                excluded_sources=excluded_sources,
                exclusion_reasons=exclusion_reasons,
                queries=queries,
                justification="Hybrid retrieval plan for laboratory/vital sign observation codes via LOINC exact and FHIR structure.",
            )

        # 4. Medication Code (RxNorm)
        if term == "RxNorm" or (role_cat == "terminology_code" and any(k in tbl or k in col for k in ["MED", "DRUG", "RXNORM", "PRESCRIPTION"])):
            included_sources = ["RxNorm", "FHIR_R4", "OHDSI"]
            excluded_sources = ["UCUM", "LOINC", "SNOMED_CT"]
            exclusion_reasons["UCUM"] = "Medication codes represent drug entities, not units."
            exclusion_reasons["LOINC"] = "Observation vocabulary not applicable to medication orders."
            exclusion_reasons["SNOMED_CT"] = "RxNorm is the primary authoritative terminology for clinical drugs in US FHIR R4."

            for sample_code in column_fact.sample_values[:5]:
                if sample_code and sample_code.strip():
                    queries.append(
                        RetrievalQuery(
                            source="RxNorm",
                            query_type="API_LOOKUP",
                            query_string=sample_code.strip(),
                            priority=1,
                            reasoning=f"Query NLM RxNav REST API for RxCUI '{sample_code}' concept details."
                        )
                    )

            queries.append(
                RetrievalQuery(
                    source="FHIR_R4",
                    query_type="STRUCTURAL_SEARCH",
                    query_string="MedicationRequest.medicationCodeableConcept",
                    priority=2,
                    reasoning="Retrieve MedicationRequest drug coding requirements and elements."
                )
            )
            return RetrievalPlan(
                table_name=column_fact.table_name,
                column_name=column_fact.column_name,
                included_sources=included_sources,
                excluded_sources=excluded_sources,
                exclusion_reasons=exclusion_reasons,
                queries=queries,
                justification="Prescription medication retrieval plan combining official NLM RxNav lookup with FHIR MedicationRequest structure.",
            )

        # 5. Condition / Diagnosis Code (SNOMED CT)
        if term == "SNOMED_CT" or (role_cat in ["terminology_code", "concept_display"] and any(k in tbl or k in col for k in ["DIAG", "CONDITION", "PROBLEM", "SNOMED"])):
            included_sources = ["SNOMED_CT", "OHDSI", "FHIR_R4"]
            excluded_sources = ["UCUM", "RxNorm", "LOINC"]
            exclusion_reasons["UCUM"] = "Condition concepts do not represent units of measure."
            exclusion_reasons["RxNorm"] = "Medication vocabulary not applicable to diagnosis concepts."
            exclusion_reasons["LOINC"] = "LOINC is secondary to SNOMED CT for disorder and clinical finding identification."

            if column_fact.sample_values:
                rep_sample = column_fact.sample_values[0].strip()
                queries.append(
                    RetrievalQuery(
                        source="OHDSI",
                        query_type="VECTOR_SEMANTIC",
                        query_string=rep_sample,
                        priority=1,
                        reasoning=f"Search OHDSI OMOP concept repository for clinical concept matching representative sample '{rep_sample}'."
                    )
                )

            queries.append(
                RetrievalQuery(
                    source="FHIR_R4",
                    query_type="STRUCTURAL_SEARCH",
                    query_string="Condition.code",
                    priority=2,
                    reasoning="Retrieve Condition.code element definition and ValueSet binding."
                )
            )
            return RetrievalPlan(
                table_name=column_fact.table_name,
                column_name=column_fact.column_name,
                included_sources=included_sources,
                excluded_sources=excluded_sources,
                exclusion_reasons=exclusion_reasons,
                queries=queries,
                justification="Diagnosis retrieval plan leveraging OHDSI SNOMED mappings and FHIR Condition structure.",
            )

        # 6. Primary Identifiers & Foreign References
        if role_cat in ["primary_identifier", "foreign_reference"]:
            included_sources = ["FHIR_R4"]
            excluded_sources = ["LOINC", "UCUM", "RxNorm", "SNOMED_CT", "OHDSI"]
            for s in excluded_sources:
                exclusion_reasons[s] = "Identity and relational links map to FHIR structural identifiers/references, not clinical vocabularies."

            if role_cat == "primary_identifier":
                target_res = "Patient" if "PATIENT" in tbl else (
                    "Condition" if "DIAG" in tbl else (
                        "MedicationRequest" if "MED" in tbl else (
                            "Encounter" if "ENC" in tbl else "Observation"
                        )
                    )
                )
                queries.append(
                    RetrievalQuery(
                        source="FHIR_R4",
                        query_type="STRUCTURAL_SEARCH",
                        query_string=f"{target_res}.identifier",
                        priority=1,
                        reasoning=f"Retrieve {target_res}.identifier and {target_res}.id structural definitions."
                    )
                )
            else:
                queries.append(
                    RetrievalQuery(
                        source="FHIR_R4",
                        query_type="STRUCTURAL_SEARCH",
                        query_string="subject patient reference",
                        priority=1,
                        reasoning="Retrieve FHIR reference elements (e.g. Observation.subject, Condition.subject, Encounter.subject)."
                    )
                )

            return RetrievalPlan(
                table_name=column_fact.table_name,
                column_name=column_fact.column_name,
                included_sources=included_sources,
                excluded_sources=excluded_sources,
                exclusion_reasons=exclusion_reasons,
                queries=queries,
                justification="Relational identifier plan focusing exclusively on FHIR resource identity and reference specifications.",
            )

        # 7. Timestamps and Quantitative values (General Clinical Attributes)
        included_sources = ["FHIR_R4"]
        excluded_sources = ["LOINC", "UCUM", "RxNorm", "SNOMED_CT", "OHDSI"]
        for s in excluded_sources:
            exclusion_reasons[s] = "Standard clinical dates or administrative codes map to FHIR primitive elements, not terminology engines."

        queries.append(
            RetrievalQuery(
                source="FHIR_R4",
                query_type="STRUCTURAL_SEARCH",
                query_string=f"{tbl} {col}",
                priority=2,
                reasoning=f"Search FHIR R4 structure for appropriate element corresponding to attribute '{col}'."
            )
        )

        return RetrievalPlan(
            table_name=column_fact.table_name,
            column_name=column_fact.column_name,
            included_sources=included_sources,
            excluded_sources=excluded_sources,
            exclusion_reasons=exclusion_reasons,
            queries=queries,
            justification="General structural search plan for clinical or administrative attribute.",
        )
