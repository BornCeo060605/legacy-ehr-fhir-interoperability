# Phase 1 HL7 FHIR R4 Interoperability & Mapping Audit Report

- **Run ID:** `PHASE1_RUN_20260926_105744_ad4a5a`
- **Target Database:** `hospital_c.db`
- **SHA256 Fingerprint:** `44c818064d884d13b42842a573f4c0fe3cfbd30efed198f7a17203474c40fe2b`
- **Timestamp:** `2026-09-26T11:21:20.601686`
- **LLM Provider / Model:** `openrouter` / `meta-llama/llama-3.3-70b-instruct`
- **Accepted Mappings:** 27 | **Review:** 2 | **Unsupported:** 1

## Summary Table

| Legacy Field             | Semantic Meaning                                   | FHIR Candidate                              |   Confidence | Evidence   | Decision        | Rule                        |
|--------------------------|----------------------------------------------------|---------------------------------------------|--------------|------------|-----------------|-----------------------------|
| CLINICAL_EVENT.EVT_ID    | Unique identifier for a clinical event             | Observation.identifier                      |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| CLINICAL_EVENT.P_ID      | Foreign key referencing a patient identifier       | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| CLINICAL_EVENT.EVT_START | Clinical Event Start Date                          | Observation.effectiveDateTime               |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| CLINICAL_EVENT.EVT_END   | Clinical event end date                            | Observation.effectiveDateTime               |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| CLINICAL_EVENT.EVT_TYPE  | Clinical Event Type                                | Encounter.type                              |         0.65 | WEAK       | **REVIEW**      | `R3_MANUAL_REVIEW_REQUIRED` |
| CLINICAL_EVENT.EVT_RSN   | Completely unpopulated legacy field 'EVT_RSN'      | CLINICAL_EVENT.EVT_RSN                      |         0.1  | NONE       | **UNSUPPORTED** | `R0_UNPOPULATED_FIELD`      |
| DRUG_ORDERS.ORD_ID       | Unique identifier for a drug order                 | MedicationRequest.identifier                |         0.91 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| DRUG_ORDERS.P_ID         | Patient Identifier Reference                       | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| DRUG_ORDERS.ORD_CD       | RxNorm medication code                             | MedicationRequest.medicationCodeableConcept |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| DRUG_ORDERS.ORD_DESC     | Medication Order Description                       | MedicationRequest.note                      |         0.68 | WEAK       | **REVIEW**      | `R3_MANUAL_REVIEW_REQUIRED` |
| DRUG_ORDERS.ORD_STAT     | Order status of a drug                             | MedicationRequest.status                    |         0.8  | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| DRUG_ORDERS.ORD_DT       | Date and time a drug order was recorded            | MedicationRequest.authoredOn                |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| MEASUREMENTS.MSR_ID      | Unique Measurement Identifier                      | Observation.identifier                      |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| MEASUREMENTS.P_ID        | Patient Identifier Reference                       | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| MEASUREMENTS.MSR_CD      | LOINC code for clinical measurement or observation | Observation.code                            |         0.99 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| MEASUREMENTS.MSR_DESC    | Clinical Observation Concept Description           | Observation.code                            |         0.85 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| MEASUREMENTS.MSR_VAL     | Quantitative measurement value                     | Observation.valueQuantity.value             |         0.8  | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| MEASUREMENTS.MSR_UNIT    | Unit of measurement for a quantitative measurement | Observation.valueQuantity.unit              |         0.99 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| MEASUREMENTS.MSR_DT      | Date and time of measurement                       | Observation.effectiveDateTime               |         0.8  | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| PATIENT.P_ID             | Patient Identifier                                 | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| PATIENT.BRTH_DT          | Patient birth date                                 | Patient.birthDate                           |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| PATIENT.GNDR             | Patient Gender                                     | Patient.gender                              |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| PATIENT.SURNAME          | Patient's family name                              | Patient.name                                |         0.95 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| PATIENT.FORENAME         | Patient's forename                                 | Patient.name                                |         0.93 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| PROBLEM_LIST.PRB_ID      | Unique Problem Identifier                          | Observation.identifier                      |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| PROBLEM_LIST.P_ID        | Unique Patient Identifier                          | Patient.identifier                          |         0.92 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| PROBLEM_LIST.PRB_CD      | Condition or Problem Code                          | Condition.code                              |         0.86 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| PROBLEM_LIST.PRB_DESC    | Clinical condition or problem description          | Condition.code                              |         0.85 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| PROBLEM_LIST.PRB_ONSET   | Date of problem onset                              | Condition.onsetDateTime                     |         0.78 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| PROBLEM_LIST.PRB_STAT    | Problem status code                                | Condition.clinicalStatus                    |         0.81 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |

## Detailed Field Evidence & Provenance

### Field: `CLINICAL_EVENT.EVT_ID`

- **Semantic Meaning:** Unique identifier for a clinical event
- **FHIR Candidate:** `Observation.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 22612 distinct values across 22612 non-null rows (0.0% null)
- 100% unique non-null values (candidate identifier)
- Sample values resemble UUIDs (e.g., '8d1edfd0-df60-b5c8-5690-bf999dafd26d')

#### Inferred Facts
- The field is likely used as a primary identifier for clinical events due to its uniqueness and format
- The field's values are consistent with FHIR R4's Observation.identifier element

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `CLINICAL_EVENT.P_ID`

- **Semantic Meaning:** Foreign key referencing a patient identifier
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 354 distinct values across 22612 non-null rows
- 100.0% overlap between CLINICAL_EVENT.P_ID and MEASUREMENTS.P_ID, PATIENT.P_ID, and PROBLEM_LIST.P_ID

#### Inferred Facts
- CLINICAL_EVENT.P_ID acts as a foreign reference to MEASUREMENTS.P_ID, PATIENT.P_ID, and PROBLEM_LIST.P_ID
- Values in CLINICAL_EVENT.P_ID are consistent with a foreign-key patient reference

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `CLINICAL_EVENT.EVT_START`

- **Semantic Meaning:** Clinical Event Start Date
- **FHIR Candidate:** `Observation.effectiveDateTime`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with 9235 distinct values across 22612 non-null rows
- Samples of values are in the format 'DD-MMM-YYYY', suggesting a date format
- Strong value containment with PROBLEM_LIST.PRB_ONSET, MEASUREMENTS.MSR_DT, and DRUG_ORDERS.ORD_DT suggests a reference to a clinical event or measurement timestamp

#### Inferred Facts
- The field likely represents a timestamp for a clinical event, given the overlap with other tables containing clinical event or measurement data
- The use of a date format in the samples suggests that the field is intended to capture a specific point in time

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest.eventHistory' (Reference, 0..*): A list of events of interest in the lifecycle
- FHIR R4 element 'Condition.clinicalStatus' (CodeableConcept, 0..1): active | recurrence | relapse | inactive | remission | resolved
- FHIR R4 element 'Observation.partOf' (Reference, 0..*): Part of referenced event

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.effectiveDateTime)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `CLINICAL_EVENT.EVT_END`

- **Semantic Meaning:** Clinical event end date
- **FHIR Candidate:** `Observation.effectiveDateTime`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with 9212 distinct values
- 0.0% null values across 22612 non-null rows
- Samples: ['13-Mar-1962', '24-Jan-1984', '21-Apr-1985']
- Strong value containment with MEASUREMENTS.MSR_DT, PROBLEM_LIST.PRB_ONSET, and DRUG_ORDERS.ORD_DT

#### Inferred Facts
- CLINICAL_EVENT.EVT_END likely represents a timestamp for the end of a clinical event
- The field is related to other timestamp fields in the database, such as MEASUREMENTS.MSR_DT, PROBLEM_LIST.PRB_ONSET, and DRUG_ORDERS.ORD_DT

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest.eventHistory' (Reference, 0..*): A list of events of interest in the lifecycle
- FHIR R4 element 'Patient.gender' (code, 0..1): male | female | other | unknown
- FHIR R4 element 'Patient.contact.gender' (code, 0..1): male | female | other | unknown

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.effectiveDateTime)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `CLINICAL_EVENT.EVT_TYPE`

- **Semantic Meaning:** Clinical Event Type
- **FHIR Candidate:** `Encounter.type`
- **Decision:** **REVIEW** (Rule: `R3_MANUAL_REVIEW_REQUIRED`)
- **Decision Reason:** Candidate mapping proposed but requires clinical expert review (Confidence: 0.65, Strength: WEAK).
- **Mapping Confidence:** `0.65` (Evidence Strength: `WEAK`)

#### Observed Facts
- Observed type is 'TEXT'
- 5 distinct values across 22612 non-null rows
- Samples: ['AMB', 'IMP', 'EMER', 'VR', 'HH']

#### Inferred Facts
- FHIR R4 element 'Encounter.type' is a possible match
- FHIR R4 element 'Encounter.serviceType' is a possible match

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest.eventHistory' (Reference, 0..*): A list of events of interest in the lifecycle
- FHIR R4 element 'Encounter.type' (CodeableConcept, 0..*): Specific type of encounter
- FHIR R4 element 'Encounter.serviceType' (CodeableConcept, 0..1): Specific type of service

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.type)
- Deterministic Decision Engine (R3_MANUAL_REVIEW_REQUIRED)

---

### Field: `CLINICAL_EVENT.EVT_RSN`

- **Semantic Meaning:** Completely unpopulated legacy field 'EVT_RSN'
- **FHIR Candidate:** `CLINICAL_EVENT.EVT_RSN`
- **Decision:** **UNSUPPORTED** (Rule: `R0_UNPOPULATED_FIELD`)
- **Decision Reason:** Column 'EVT_RSN' contains 100% missing values; clinical semantics unobservable.
- **Mapping Confidence:** `0.10` (Evidence Strength: `NONE`)

#### Observed Facts
- Column has 0 non-null values across 22612 rows.

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest.eventHistory' (Reference, 0..*): A list of events of interest in the lifecycle
- FHIR R4 element 'Condition.clinicalStatus' (CodeableConcept, 0..1): active | recurrence | relapse | inactive | remission | resolved
- FHIR R4 element 'Observation.partOf' (Reference, 0..*): Part of referenced event

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (CLINICAL_EVENT.EVT_RSN)
- Deterministic Decision Engine (R0_UNPOPULATED_FIELD)

---

### Field: `DRUG_ORDERS.ORD_ID`

- **Semantic Meaning:** Unique identifier for a drug order
- **FHIR Candidate:** `MedicationRequest.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.91) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.91` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 21625 distinct values across 21625 non-null rows (0.0% null)
- 100% unique non-null values (candidate identifier)

#### Inferred Facts
- The field is likely a primary identifier due to its uniqueness and lack of null values
- The field's format resembles a UUID, which is commonly used as an identifier in FHIR resources

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `DRUG_ORDERS.P_ID`

- **Semantic Meaning:** Patient Identifier Reference
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- DRUG_ORDERS.P_ID has 347 distinct TEXT values
- 0.0% null values in DRUG_ORDERS.P_ID
- Strong value containment between DRUG_ORDERS.P_ID and PATIENT.P_ID
- Strong value containment between DRUG_ORDERS.P_ID and CLINICAL_EVENT.P_ID
- Strong value containment between DRUG_ORDERS.P_ID and MEASUREMENTS.P_ID

#### Inferred Facts
- DRUG_ORDERS.P_ID acts as a foreign reference to PATIENT.P_ID
- DRUG_ORDERS.P_ID is likely a patient identifier

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `DRUG_ORDERS.ORD_CD`

- **Semantic Meaning:** RxNorm medication code
- **FHIR Candidate:** `MedicationRequest.medicationCodeableConcept`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 140 distinct values across 12804 non-null rows
- 40.8% null values
- Samples match RxNorm concepts (e.g., '309362' -> 'clopidogrel 75 MG Oral Tablet')

#### Inferred Facts
- The field likely represents a medication code based on the samples provided and the match with RxNorm concepts
- The use of RxNorm codes suggests a standardized representation of medication orders

#### Retrieved Authoritative Evidence
- Official NLM RxNorm concept RxCUI 309362: 'clopidogrel 75 MG Oral Tablet' (Term Type: SCD)
- Official NLM RxNorm concept RxCUI 312961: 'simvastatin 20 MG Oral Tablet' (Term Type: SCD)
- Official NLM RxNorm concept RxCUI 866412: '24 HR metoprolol succinate 100 MG Extended Release Oral Tablet' (Term Type: SCD)
- Official NLM RxNorm concept RxCUI 705129: 'nitroglycerin 0.4 MG/ACTUAT Mucosal Spray' (Term Type: SCD)

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (RxNorm, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.medicationCodeableConcept)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `DRUG_ORDERS.ORD_DESC`

- **Semantic Meaning:** Medication Order Description
- **FHIR Candidate:** `MedicationRequest.note`
- **Decision:** **REVIEW** (Rule: `R3_MANUAL_REVIEW_REQUIRED`)
- **Decision Reason:** Candidate mapping proposed but requires clinical expert review (Confidence: 0.68, Strength: WEAK).
- **Mapping Confidence:** `0.68` (Evidence Strength: `WEAK`)

#### Observed Facts
- Observed type is 'TEXT'
- 145 distinct values across 12804 non-null rows
- 40.8% null values
- Sample values contain medication names, strengths, and forms (e.g., 'Clopidogrel 75 MG Oral Tablet')

#### Inferred Facts
- The field likely contains free-text descriptions of medication orders
- The presence of medication names, strengths, and forms suggests a relationship to medication ordering

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Condition.recordedDate' (dateTime, 0..1): Date record was first recorded
- FHIR R4 element 'Condition.recorder' (Reference, 0..1): Who recorded the condition
- FHIR R4 element 'MedicationRequest.recorder' (Reference, 0..1): Person who entered the request

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.note)
- Deterministic Decision Engine (R3_MANUAL_REVIEW_REQUIRED)

---

### Field: `DRUG_ORDERS.ORD_STAT`

- **Semantic Meaning:** Order status of a drug
- **FHIR Candidate:** `MedicationRequest.status`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.80) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.80` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'TEXT'
- 2 distinct values: 'completed' and 'active'
- 0.0% null values across 21625 non-null rows

#### Inferred Facts
- The values 'completed' and 'active' suggest a status or state of a drug order
- The field is likely used to track the progress or state of a drug order

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.maritalStatus' (CodeableConcept, 0..1): Marital (civil) status of a patient
- FHIR R4 element 'Condition.recordedDate' (dateTime, 0..1): Date record was first recorded
- FHIR R4 element 'Condition.recorder' (Reference, 0..1): Who recorded the condition

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.status)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `DRUG_ORDERS.ORD_DT`

- **Semantic Meaning:** Date and time a drug order was recorded
- **FHIR Candidate:** `MedicationRequest.authoredOn`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with 7330 distinct values across 21625 non-null rows
- Strong value containment with CLINICAL_EVENT.EVT_END and CLINICAL_EVENT.EVT_START
- Strong value containment with MEASUREMENTS.MSR_DT

#### Inferred Facts
- DRUG_ORDERS.ORD_DT likely represents a timestamp for when a drug order was recorded
- The field's relationship with CLINICAL_EVENT.EVT_END and CLINICAL_EVENT.EVT_START suggests it may be related to the timing of clinical events

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Condition.recordedDate' (dateTime, 0..1): Date record was first recorded
- FHIR R4 element 'Condition.recorder' (Reference, 0..1): Who recorded the condition
- FHIR R4 element 'MedicationRequest.recorder' (Reference, 0..1): Person who entered the request

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.authoredOn)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `MEASUREMENTS.MSR_ID`

- **Semantic Meaning:** Unique Measurement Identifier
- **FHIR Candidate:** `Observation.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- TEXT type with 100% unique non-null values
- 0.0% null values across 49902 rows
- Samples resemble UUIDs (Universally Unique Identifiers)

#### Inferred Facts
- MEASUREMENTS.MSR_ID likely serves as a primary identifier for measurement records
- Alignment with FHIR R4 Observation.identifier suggests a standardized approach to identifying observations

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `MEASUREMENTS.P_ID`

- **Semantic Meaning:** Patient Identifier Reference
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 354 distinct values across 49902 non-null rows
- Strong value containment (100.0%) between MEASUREMENTS.P_ID and PATIENT.P_ID
- Strong value containment (100.0%) between MEASUREMENTS.P_ID and CLINICAL_EVENT.P_ID

#### Inferred Facts
- MEASUREMENTS.P_ID acts as a foreign reference to PATIENT.P_ID
- MEASUREMENTS.P_ID acts as a foreign reference to CLINICAL_EVENT.P_ID

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `MEASUREMENTS.MSR_CD`

- **Semantic Meaning:** LOINC code for clinical measurement or observation
- **FHIR Candidate:** `Observation.code`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.99) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.99` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type is 'TEXT'
- 20 distinct values across 49902 non-null rows
- Sample values match known LOINC codes (e.g., '8302-2', '72514-3', '29463-7')
- External evidence confirms LOINC codes for various clinical measurements

#### Inferred Facts
- The field likely represents a standardized terminology code for clinical observations
- The use of LOINC codes suggests a focus on quantitative measurements and vital signs

#### Retrieved Authoritative Evidence
- Official LOINC concept 8302-2: 'Body height'. Component: Body height, System: ^Patient, Class: BDYHGT.ATOM, Recommended UCUM units: '[in_us];cm;m'
- Official LOINC concept 72514-3: 'Pain severity - 0-10 verbal numeric rating [Score] - Reported'. Component: Pain severity - 0-10 verbal numeric rating, System: ^Patient, Class: H&P.HX, Recommended UCUM units: '{score}'
- Official LOINC concept 29463-7: 'Body weight'. Component: Body weight, System: ^Patient, Class: BDYWGT.ATOM, Recommended UCUM units: '[lb_av];kg'
- Official LOINC concept 39156-5: 'Body mass index (BMI) [Ratio]'. Component: Body mass index, System: ^Patient, Class: BDYWGT.ATOM, Recommended UCUM units: 'kg/m2'

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (LOINC, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.code)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `MEASUREMENTS.MSR_DESC`

- **Semantic Meaning:** Clinical Observation Concept Description
- **FHIR Candidate:** `Observation.code`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.85) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.85` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'TEXT'
- 21 distinct values across 49902 non-null rows
- Sample values include 'Body Height', 'Pain severity - 0-10 verbal numeric rating [Score] - Reported', 'Body Weight'
- FHIR R4 'Observation.code' element is a CodeableConcept with a binding example

#### Inferred Facts
- The field likely represents a human-readable description of a clinical observation or measurement concept
- The use of LOINC terminology is inferred based on the sample values and the exclusion of other terminology systems

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.code' (CodeableConcept, Cardinality: 1..1). Description: Type of observation (code / type) [Binding: example]

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (LOINC, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.code)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `MEASUREMENTS.MSR_VAL`

- **Semantic Meaning:** Quantitative measurement value
- **FHIR Candidate:** `Observation.valueQuantity.value`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.80) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.80` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'REAL'
- 9026 distinct values across 44463 non-null rows
- 10.9% null values
- Sample values include decimal numbers (e.g., '75.35', '30.33')

#### Inferred Facts
- The field likely represents a quantitative measurement
- FHIR R4 structural definitions suggest a relationship with 'Observation.value[x]' or 'Observation.component.value[x]'

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Observation.value[x]' (Quantity, 0..1): Actual result
- FHIR R4 element 'Observation.component.value[x]' (Quantity, 0..1): Actual component result
- FHIR R4 element 'MedicationRequest.dispenseRequest.dispenseInterval' (Duration, 0..1): Minimum period of time between dispenses

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.valueQuantity.value)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `MEASUREMENTS.MSR_UNIT`

- **Semantic Meaning:** Unit of measurement for a quantitative measurement
- **FHIR Candidate:** `Observation.valueQuantity.unit`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.99) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.99` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 9 distinct values across 44463 non-null rows
- 10.9% null rate
- Sample values include 'cm', '{score}', 'kg', 'kg/m2', '/min'

#### Inferred Facts
- The field represents a variety of physical measurement units
- The presence of '{score}' suggests that the field may also include arbitrary clinical score units

#### Retrieved Authoritative Evidence
- Standard clinical UCUM unit 'cm': Centimeter (Length)
- Standard clinical UCUM unit '{score}': Arbitrary clinical score unit
- Standard clinical UCUM unit 'kg': Kilogram (Mass)
- Standard clinical UCUM unit '/min': Per minute (Frequency)

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (UCUM, FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.valueQuantity.unit)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `MEASUREMENTS.MSR_DT`

- **Semantic Meaning:** Date and time of measurement
- **FHIR Candidate:** `Observation.effectiveDateTime`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.80) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.80` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with 6517 distinct values across 49902 non-null rows
- Samples of values are in the format 'DD-MMM-YYYY'
- Strong value containment with CLINICAL_EVENT.EVT_END, CLINICAL_EVENT.EVT_START, and DRUG_ORDERS.ORD_DT suggests a foreign reference relationship

#### Inferred Facts
- MEASUREMENTS.MSR_DT likely represents a timestamp for a measurement or observation
- The field's relationship with other tables suggests it may be used to link measurements to specific events or orders

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Observation' (Element, 0..*): Measurements and simple assertions
- FHIR R4 element 'Observation.derivedFrom' (Reference, 0..*): Related measurements the observation is made from

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.effectiveDateTime)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `PATIENT.P_ID`

- **Semantic Meaning:** Patient Identifier
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- 100% unique non-null values across 354 rows
- Observed type 'TEXT' with UUID-like samples
- Full containment of values in CLINICAL_EVENT.P_ID and MEASUREMENTS.P_ID

#### Inferred Facts
- PATIENT.P_ID acts as a foreign reference to other tables
- Values in PATIENT.P_ID are consistent with a patient identifier

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PATIENT.BRTH_DT`

- **Semantic Meaning:** Patient birth date
- **FHIR Candidate:** `Patient.birthDate`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with 296 distinct values across 354 non-null rows
- Samples of values are in the format 'DD-Mmm-YYYY', indicating a date
- Moderate value overlap with DRUG_ORDERS.ORD_DT and MEASUREMENTS.MSR_DT, suggesting shared domain or concept pool

#### Inferred Facts
- The field is likely representing a date of birth, given the format and range of values
- The overlap with other date fields suggests a common data type, but not necessarily the same concept

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use
- FHIR R4 element 'Patient.name' (HumanName, 0..*): A name associated with the patient

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.birthDate)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `PATIENT.GNDR`

- **Semantic Meaning:** Patient Gender
- **FHIR Candidate:** `Patient.gender`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT'
- 2 distinct values across 354 non-null rows
- Samples: ['M', 'F']

#### Inferred Facts
- Values 'M' and 'F' likely represent male and female respectively

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use
- FHIR R4 element 'Patient.name' (HumanName, 0..*): A name associated with the patient

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.gender)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `PATIENT.SURNAME`

- **Semantic Meaning:** Patient's family name
- **FHIR Candidate:** `Patient.name`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.95) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.95` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 265 distinct values across 354 non-null rows
- 0.0% null values

#### Inferred Facts
- The field likely represents a patient's surname due to the presence of distinct text values
- The values appear to be a combination of surname and a numeric suffix, possibly an identifier

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use
- FHIR R4 element 'Patient.name' (HumanName, 0..*): A name associated with the patient

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.name)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PATIENT.FORENAME`

- **Semantic Meaning:** Patient's forename
- **FHIR Candidate:** `Patient.name`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.93) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.93` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 354 distinct values across 354 non-null rows (0.0% null)
- 100% unique non-null values (candidate identifier)

#### Inferred Facts
- The field likely represents a part of the patient's name
- FHIR R4 element 'Patient.name' (HumanName, 0..*) is a possible match

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use
- FHIR R4 element 'Patient.name' (HumanName, 0..*): A name associated with the patient

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.name)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PROBLEM_LIST.PRB_ID`

- **Semantic Meaning:** Unique Problem Identifier
- **FHIR Candidate:** `Observation.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 13953 distinct values across 13953 non-null rows (0.0% null)
- 100% unique non-null values (candidate identifier)
- Sample values resemble UUIDs (e.g., '8d1edfd0-df60-b5c8-8167-81bc5f27c8d7')

#### Inferred Facts
- The field likely serves as a primary identifier for problems in the problem list
- The use of UUID-like values suggests a unique identifier for each problem

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PROBLEM_LIST.P_ID`

- **Semantic Meaning:** Unique Patient Identifier
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.92) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.92` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 354 distinct values across 13953 non-null rows
- Strong value containment (100.0%) with CLINICAL_EVENT.P_ID, MEASUREMENTS.P_ID, and PATIENT.P_ID
- Samples of values are in UUID format

#### Inferred Facts
- PROBLEM_LIST.P_ID acts as a primary identifier for patient records
- The identifier is likely used for referencing patient data across different tables

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PROBLEM_LIST.PRB_CD`

- **Semantic Meaning:** Condition or Problem Code
- **FHIR Candidate:** `Condition.code`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.86) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.86` (Evidence Strength: `MODERATE`)

#### Observed Facts
- TEXT type
- 236 distinct values
- 0.0% null
- Sample values resemble SNOMED_CT codes

#### Inferred Facts
- Condition.code FHIR R4 element binding is consistent with SNOMED_CT terminology

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Condition.code' (CodeableConcept, Cardinality: 0..1). Description: Identification of the condition, problem or diagnosis [Binding: example]

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (SNOMED_CT, OHDSI, FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.code)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `PROBLEM_LIST.PRB_DESC`

- **Semantic Meaning:** Clinical condition or problem description
- **FHIR Candidate:** `Condition.code`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.85) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.85` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Text type with 236 distinct values
- 0.0% null values across 13953 non-null rows
- Sample values contain SNOMED_CT-like descriptions (e.g., 'Osteoarthritis of knee (disorder)')

#### Inferred Facts
- The field likely represents a concept display for a clinical condition or problem
- The use of SNOMED_CT terminology is inferred based on the sample values and the exclusion of other terminology sources

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Condition.code' (CodeableConcept, Cardinality: 0..1). Description: Identification of the condition, problem or diagnosis [Binding: example]

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (SNOMED_CT, OHDSI, FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.code)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `PROBLEM_LIST.PRB_ONSET`

- **Semantic Meaning:** Date of problem onset
- **FHIR Candidate:** `Condition.onsetDateTime`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.78) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.78` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with 5647 distinct values
- Strong value containment (99.0%) with CLINICAL_EVENT.EVT_START
- Strong value containment (98.3%) with CLINICAL_EVENT.EVT_END
- Moderate value overlap (73.2%) with DRUG_ORDERS.ORD_DT

#### Inferred Facts
- PROBLEM_LIST.PRB_ONSET likely represents a date or timestamp related to a patient's condition or problem
- The field's values are likely used to track the onset or start of a condition or problem

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Condition.category' (CodeableConcept, 0..*): problem-list-item | encounter-diagnosis
- FHIR R4 element 'Condition.onset[x]' (dateTime, 0..1): Estimated or actual date,  date-time, or age
- FHIR R4 element 'Condition' (Element, 0..*): Detailed information about conditions, problems or diagnoses

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.onsetDateTime)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `PROBLEM_LIST.PRB_STAT`

- **Semantic Meaning:** Problem status code
- **FHIR Candidate:** `Condition.clinicalStatus`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.81) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.81` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'TEXT'
- 2 distinct values across 13953 non-null rows
- Sample values are 'active' and 'resolved'

#### Inferred Facts
- The field likely represents a status or state related to a problem or condition
- The values 'active' and 'resolved' suggest a binary status indicator

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.statusHistory' (BackboneElement, 0..*): List of past encounter statuses
- FHIR R4 element 'Patient.maritalStatus' (CodeableConcept, 0..1): Marital (civil) status of a patient
- FHIR R4 element 'MedicationRequest.statusReason' (CodeableConcept, 0..1): Reason for current status

#### Provenance & Audit Trail
- Database Checksum: 44c818064d88...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.clinicalStatus)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

