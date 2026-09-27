# Phase 1 HL7 FHIR R4 Interoperability & Mapping Audit Report

- **Run ID:** `PHASE1_RUN_20260927_034746_ac4d9e`
- **Target Database:** `hospital_a.db`
- **SHA256 Fingerprint:** `380fbfc747c2b43909ba3e9eb43c3881bb5cb7d5b094cb761c41ba839928ecd4`
- **Timestamp:** `2026-09-27T04:18:33.124224`
- **LLM Provider / Model:** `openrouter` / `meta-llama/llama-3.3-70b-instruct`
- **Accepted Mappings:** 29 | **Review:** 0 | **Unsupported:** 1

## Summary Table

| Legacy Field                  | Semantic Meaning                                                 | FHIR Candidate                              |   Confidence | Evidence   | Decision        | Rule                   |
|-------------------------------|------------------------------------------------------------------|---------------------------------------------|--------------|------------|-----------------|------------------------|
| DIAGNOSIS.DIAGNOSIS_ID        | Unique identifier for a diagnosis                                | Condition.identifier                        |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| DIAGNOSIS.PATIENT_ID          | Foreign key referencing a patient's identifier                   | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| DIAGNOSIS.SNOMED_CODE         | SNOMED CT code for diagnosis                                     | Condition.code                              |         0.8  | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED` |
| DIAGNOSIS.DIAGNOSIS_NAME      | Clinical diagnosis or finding name                               | Condition.code                              |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| DIAGNOSIS.ONSET_DATE          | Date and time when a diagnosis was first identified or suspected | Condition.onset                             |         0.97 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| DIAGNOSIS.STATUS              | Diagnosis status code                                            | Condition.clinicalStatus                    |         0.9  | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| ENCOUNTER.ENCOUNTER_ID        | Unique Encounter Identifier                                      | Encounter.identifier                        |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| ENCOUNTER.PATIENT_ID          | Reference to a patient's unique identifier                       | Encounter.subject                           |         0.88 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| ENCOUNTER.START_DATE          | Encounter start date and time                                    | Encounter.period.start                      |         0.92 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| ENCOUNTER.END_DATE            | End date and time of an encounter                                | Encounter.period.end                        |         0.92 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| ENCOUNTER.ENCOUNTER_TYPE      | Encounter type or classification                                 | Encounter.type                              |         0.85 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED` |
| ENCOUNTER.REASON              | Completely unpopulated legacy field 'REASON'                     | ENCOUNTER.REASON                            |         0.1  | NONE       | **UNSUPPORTED** | `R0_UNPOPULATED_FIELD` |
| MEDICATION.MEDICATION_ID      | Unique identifier for a medication                               | MedicationRequest.identifier                |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| MEDICATION.PATIENT_ID         | Foreign key referencing a patient's identifier                   | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| MEDICATION.RXNORM_CODE        | RxNorm medication code                                           | MedicationRequest.medicationCodeableConcept |         1    | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| MEDICATION.MEDICATION_NAME    | Medication Name                                                  | MedicationRequest.medicationCodeableConcept |         0.91 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| MEDICATION.STATUS             | Medication status code                                           | MedicationRequest.status                    |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| MEDICATION.PRESCRIBED_DATE    | Date and time when a medication was prescribed                   | MedicationRequest.authoredOn                |         0.92 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| PATIENT_MASTER.PATIENT_ID     | Unique patient identifier                                        | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| PATIENT_MASTER.DATE_OF_BIRTH  | Patient's date of birth                                          | Patient.birthDate                           |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| PATIENT_MASTER.GENDER         | Patient's gender                                                 | Patient.gender                              |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| PATIENT_MASTER.LAST_NAME      | Patient's last name                                              | Patient.name                                |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| PATIENT_MASTER.FIRST_NAME     | Patient's given name                                             | Patient.name                                |         0.95 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| VITAL_SIGNS.OBSERVATION_ID    | Unique identifier for a vital sign observation                   | Observation.identifier                      |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| VITAL_SIGNS.PATIENT_ID        | Patient Identifier                                               | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| VITAL_SIGNS.LOINC_CODE        | LOINC code for vital sign observations                           | Observation.code                            |         1    | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| VITAL_SIGNS.MEASUREMENT_NAME  | Type of vital sign measurement                                   | Observation.code                            |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| VITAL_SIGNS.MEASUREMENT_VALUE | Quantitative measurement value of a vital sign                   | Observation.valueQuantity.value             |         0.81 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED` |
| VITAL_SIGNS.MEASUREMENT_UNIT  | Unit of measurement for vital signs                              | Observation.valueQuantity.unit              |         0.99 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |
| VITAL_SIGNS.MEASUREMENT_DATE  | Date and time of vital sign measurement                          | Observation.effectiveDateTime               |         0.92 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`   |

## Detailed Field Evidence & Provenance

### Field: `DIAGNOSIS.DIAGNOSIS_ID`

- **Semantic Meaning:** Unique identifier for a diagnosis
- **FHIR Candidate:** `Condition.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- TEXT type with 13953 distinct values
- 0.0% null values
- 100% unique non-null values
- Sample values resemble UUIDs (e.g., '8d1edfd0-df60-b5c8-8167-81bc5f27c8d7')

#### Inferred Facts
- The field likely serves as a primary identifier for diagnoses due to its uniqueness and lack of null values
- The values are likely generated programmatically, given their UUID-like format

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Condition.identifier' (Identifier, Cardinality: 0..*). Description: External Ids for this condition

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `DIAGNOSIS.PATIENT_ID`

- **Semantic Meaning:** Foreign key referencing a patient's identifier
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 354 distinct values
- 0.0% null values across 13953 non-null rows
- Fully contained in ENCOUNTER.PATIENT_ID, PATIENT_MASTER.PATIENT_ID, and VITAL_SIGNS.PATIENT_ID

#### Inferred Facts
- Values in DIAGNOSIS.PATIENT_ID are consistent with a foreign-key patient reference
- FHIR R4 structural definitions support the use of identifiers for patient references

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `DIAGNOSIS.SNOMED_CODE`

- **Semantic Meaning:** SNOMED CT code for diagnosis
- **FHIR Candidate:** `Condition.code`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.80) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.80` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'TEXT'
- 236 distinct values across 13953 non-null rows
- Samples of values are in the format of SNOMED CT codes (e.g., '224299000', '162864005', '239873007')
- 0.0% null values

#### Inferred Facts
- The field is likely used to store standardized codes for diagnoses
- The use of SNOMED CT codes suggests a high level of standardization and interoperability

#### Retrieved Authoritative Evidence
- Official FHIR R4 choice element 'MedicationRequest.medicationCodeableConcept' (specialization of MedicationRequest.medication[x], Cardinality: 1..1). Description: Medication to be taken

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (RxNorm, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.code)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `DIAGNOSIS.DIAGNOSIS_NAME`

- **Semantic Meaning:** Clinical diagnosis or finding name
- **FHIR Candidate:** `Condition.code`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- Field type is TEXT
- 236 distinct values across 13953 non-null rows
- Sample values contain SNOMED_CT-like phrases (e.g., 'Osteoarthritis of knee (disorder)')
- FHIR R4 Condition.code element is a CodeableConcept with a binding example

#### Inferred Facts
- The field likely represents a coded concept from a terminology system
- SNOMED_CT is a suitable terminology system for condition and diagnosis concepts

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Condition.code' (CodeableConcept, Cardinality: 0..1). Description: Identification of the condition, problem or diagnosis [Binding: example]

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (SNOMED_CT, OHDSI, FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.code)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `DIAGNOSIS.ONSET_DATE`

- **Semantic Meaning:** Date and time when a diagnosis was first identified or suspected
- **FHIR Candidate:** `Condition.onset`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.97) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.97` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 11431 distinct values across 13953 non-null rows
- Sample values match ISO 8601 datetime format
- Moderate value overlap (48.0%) with ENCOUNTER.START_DATE and (30.7%) with ENCOUNTER.END_DATE

#### Inferred Facts
- DIAGNOSIS.ONSET_DATE likely represents a timestamp for a clinical event
- The field's values are likely related to the timing of a diagnosis or condition

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.birthDate' (date, 0..1): The date of birth for the individual
- FHIR R4 element 'Condition.onset[x]' (dateTime, 0..1): Estimated or actual date,  date-time, or age
- FHIR R4 element 'Condition.recordedDate' (dateTime, 0..1): Date record was first recorded

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.onset)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `DIAGNOSIS.STATUS`

- **Semantic Meaning:** Diagnosis status code
- **FHIR Candidate:** `Condition.clinicalStatus`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.90) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.90` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type is 'TEXT'
- 2 distinct values across 13953 non-null rows
- Samples: ['active', 'resolved']

#### Inferred Facts
- The field likely represents a status or state related to a diagnosis
- The values 'active' and 'resolved' suggest a binary status indicator

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.maritalStatus' (CodeableConcept, 0..1): Marital (civil) status of a patient
- FHIR R4 element 'MedicationRequest.statusReason' (CodeableConcept, 0..1): Reason for current status
- FHIR R4 element 'Encounter.statusHistory' (BackboneElement, 0..*): List of past encounter statuses

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.clinicalStatus)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `ENCOUNTER.ENCOUNTER_ID`

- **Semantic Meaning:** Unique Encounter Identifier
- **FHIR Candidate:** `Encounter.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 22612 distinct values across 22612 non-null rows (0.0% null)
- 100% unique non-null values (candidate identifier)

#### Inferred Facts
- The field ENCOUNTER.ENCOUNTER_ID is likely a primary identifier for encounters based on its uniqueness and data type
- The field's values resemble UUIDs (Universally Unique Identifiers), which are commonly used as identifiers in healthcare systems

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Encounter.identifier' (Identifier, Cardinality: 0..*). Description: Identifier(s) by which this encounter is known

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `ENCOUNTER.PATIENT_ID`

- **Semantic Meaning:** Reference to a patient's unique identifier
- **FHIR Candidate:** `Encounter.subject`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.88) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.88` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'; 354 distinct values across 22612 non-null rows (0.0% null); Samples: ['8d1edfd0-df60-b5c8-f51f-a2d2dc613dcc', 'e10377b0-54f0-cc84-20dd-4ff3854e371c', '1e961744-0913-72cf-6d66-fc33550d7e01']

#### Inferred Facts
- The column likely represents a foreign key referencing the patient's identifier in the PATIENT_MASTER table
- The UUID-like format of the values suggests a unique identifier for each patient

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.subject)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `ENCOUNTER.START_DATE`

- **Semantic Meaning:** Encounter start date and time
- **FHIR Candidate:** `Encounter.period.start`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.92) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.92` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 22107 distinct values
- Samples match ISO 8601 datetime format
- Moderate value overlap with VITAL_SIGNS.MEASUREMENT_DATE, DIAGNOSIS.ONSET_DATE, and MEDICATION.PRESCRIBED_DATE

#### Inferred Facts
- ENCOUNTER.START_DATE likely represents a timestamp for the start of an encounter
- The field's values are likely used to track and manage patient encounters

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.period' (Period, 0..1): The start and end time of the encounter
- FHIR R4 element 'Patient.birthDate' (date, 0..1): The date of birth for the individual
- FHIR R4 element 'Condition.encounter' (Reference, 0..1): Encounter created as part of

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.period.start)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `ENCOUNTER.END_DATE`

- **Semantic Meaning:** End date and time of an encounter
- **FHIR Candidate:** `Encounter.period.end`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.92) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.92` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 22585 distinct values across 22612 non-null rows
- Sample values match ISO 8601 datetime format
- Moderate value overlap with VITAL_SIGNS.MEASUREMENT_DATE, MEDICATION.PRESCRIBED_DATE, and DIAGNOSIS.ONSET_DATE

#### Inferred Facts
- ENCOUNTER.END_DATE likely represents a timestamp for the end of an encounter
- The field's values are likely used to track the duration or completion of an encounter

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.period' (Period, 0..1): The start and end time of the encounter
- FHIR R4 element 'Patient.birthDate' (date, 0..1): The date of birth for the individual
- FHIR R4 element 'Condition.encounter' (Reference, 0..1): Encounter created as part of

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.period.end)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `ENCOUNTER.ENCOUNTER_TYPE`

- **Semantic Meaning:** Encounter type or classification
- **FHIR Candidate:** `Encounter.type`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.85) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.85` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'TEXT'
- 5 distinct values across 22612 non-null rows
- Samples include 'AMB', 'IMP', 'EMER', 'VR', 'HH'

#### Inferred Facts
- Values may represent different types of encounters, such as ambulatory, inpatient, or emergency
- FHIR R4 elements Encounter.type and Encounter.serviceType are potential matches for this field

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.type' (CodeableConcept, 0..*): Specific type of encounter
- FHIR R4 element 'Encounter.participant.type' (CodeableConcept, 0..*): Role of participant in encounter
- FHIR R4 element 'Encounter.serviceType' (CodeableConcept, 0..1): Specific type of service

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.type)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `ENCOUNTER.REASON`

- **Semantic Meaning:** Completely unpopulated legacy field 'REASON'
- **FHIR Candidate:** `ENCOUNTER.REASON`
- **Decision:** **UNSUPPORTED** (Rule: `R0_UNPOPULATED_FIELD`)
- **Decision Reason:** Column 'REASON' contains 100% missing values; clinical semantics unobservable.
- **Mapping Confidence:** `0.10` (Evidence Strength: `NONE`)

#### Observed Facts
- Column has 0 non-null values across 22612 rows.

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.reasonCode' (CodeableConcept, 0..*): Coded reason the encounter takes place
- FHIR R4 element 'Encounter.reasonReference' (Reference, 0..*): Reason the encounter takes place (reference)
- FHIR R4 element 'Condition.encounter' (Reference, 0..1): Encounter created as part of

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (ENCOUNTER.REASON)
- Deterministic Decision Engine (R0_UNPOPULATED_FIELD)

---

### Field: `MEDICATION.MEDICATION_ID`

- **Semantic Meaning:** Unique identifier for a medication
- **FHIR Candidate:** `MedicationRequest.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 100% unique non-null values
- 21625 distinct values across 21625 non-null rows
- Samples resemble UUIDs (universally unique identifiers)

#### Inferred Facts
- The field likely serves as a primary identifier for medication entities
- The values are likely generated programmatically due to their UUID-like format

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'MedicationRequest.identifier' (Identifier, Cardinality: 0..*). Description: External ids for this request

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `MEDICATION.PATIENT_ID`

- **Semantic Meaning:** Foreign key referencing a patient's identifier
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- MEDICATION.PATIENT_ID has 347 distinct values across 21625 non-null rows
- Values in MEDICATION.PATIENT_ID are fully contained in DIAGNOSIS.PATIENT_ID, ENCOUNTER.PATIENT_ID, and PATIENT_MASTER.PATIENT_ID
- Sample values are in the format of UUIDs (e.g., '8d1edfd0-df60-b5c8-f51f-a2d2dc613dcc')
- FHIR R4 element 'Patient.identifier' matches the observed data type and purpose

#### Inferred Facts
- MEDICATION.PATIENT_ID is likely a foreign key referencing the patient's identifier in the PATIENT_MASTER table
- The relationship between MEDICATION.PATIENT_ID and other tables (DIAGNOSIS, ENCOUNTER) is consistent with a foreign-key patient reference

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `MEDICATION.RXNORM_CODE`

- **Semantic Meaning:** RxNorm medication code
- **FHIR Candidate:** `MedicationRequest.medicationCodeableConcept`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (1.00) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `1.00` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 140 distinct values across 12804 non-null rows
- 40.8% null values
- Samples match RxNorm concept RxCUIs

#### Inferred Facts
- MEDICATION.RXNORM_CODE represents a standardized medication identifier
- Values in MEDICATION.RXNORM_CODE are likely used for medication ordering or documentation

#### Retrieved Authoritative Evidence
- Official NLM RxNorm concept RxCUI 309362: 'clopidogrel 75 MG Oral Tablet' (Term Type: SCD)
- Official NLM RxNorm concept RxCUI 312961: 'simvastatin 20 MG Oral Tablet' (Term Type: SCD)
- Official NLM RxNorm concept RxCUI 866412: '24 HR metoprolol succinate 100 MG Extended Release Oral Tablet' (Term Type: SCD)
- Official NLM RxNorm concept RxCUI 705129: 'nitroglycerin 0.4 MG/ACTUAT Mucosal Spray' (Term Type: SCD)

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (RxNorm, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.medicationCodeableConcept)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `MEDICATION.MEDICATION_NAME`

- **Semantic Meaning:** Medication Name
- **FHIR Candidate:** `MedicationRequest.medicationCodeableConcept`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.91) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.91` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 145 distinct values across 12804 non-null rows
- 40.8% null values
- Samples include medication names with dosage and formulation information

#### Inferred Facts
- Medication names appear to follow a structured format, including medication name, dosage, and formulation
- FHIR R4 element 'MedicationRequest.medication[x]' is a likely match for this field

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest' (Element, 0..*): Ordering of medication for patient or group
- FHIR R4 element 'MedicationRequest.category' (CodeableConcept, 0..*): Type of medication usage
- FHIR R4 element 'MedicationRequest.medication[x]' (CodeableConcept, 1..1): Medication to be taken

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.medicationCodeableConcept)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `MEDICATION.STATUS`

- **Semantic Meaning:** Medication status code
- **FHIR Candidate:** `MedicationRequest.status`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 2 distinct values across 21625 non-null rows
- Samples: ['completed', 'active']

#### Inferred Facts
- FHIR R4 element 'MedicationRequest.status' matches the observed values
- The field likely represents the current status of a medication order

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest.statusReason' (CodeableConcept, 0..1): Reason for current status
- FHIR R4 element 'MedicationRequest.status' (code, 1..1): active | on-hold | cancelled | completed | entered-in-error | stopped | draft | unknown
- FHIR R4 element 'Patient.maritalStatus' (CodeableConcept, 0..1): Marital (civil) status of a patient

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.status)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `MEDICATION.PRESCRIBED_DATE`

- **Semantic Meaning:** Date and time when a medication was prescribed
- **FHIR Candidate:** `MedicationRequest.authoredOn`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.92) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.92` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 12904 distinct values across 21625 non-null rows
- Sample values match the format of a timestamp datetime (e.g., '2018-06-19T22:43:32+05:30')
- Moderate value overlap (68.6% and 60.2%) with VITAL_SIGNS.MEASUREMENT_DATE and ENCOUNTER.START_DATE indicates shared domain or concept pool

#### Inferred Facts
- The field is likely representing a datetime value due to the presence of date and time components in the sample values
- The overlap with VITAL_SIGNS.MEASUREMENT_DATE and ENCOUNTER.START_DATE suggests a relationship between medication prescription and other clinical events

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.birthDate' (date, 0..1): The date of birth for the individual
- FHIR R4 element 'Condition.recordedDate' (dateTime, 0..1): Date record was first recorded
- FHIR R4 element 'MedicationRequest' (Element, 0..*): Ordering of medication for patient or group

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.authoredOn)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PATIENT_MASTER.PATIENT_ID`

- **Semantic Meaning:** Unique patient identifier
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- 100% unique non-null values across 354 rows
- Observed type 'TEXT' with UUID-like format
- Full containment of values in related tables (DIAGNOSIS, ENCOUNTER)

#### Inferred Facts
- PATIENT_ID serves as a primary identifier for patients
- Values are consistent with a foreign-key patient reference

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Patient.identifier' (Identifier, Cardinality: 0..*). Description: An identifier for this patient

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PATIENT_MASTER.DATE_OF_BIRTH`

- **Semantic Meaning:** Patient's date of birth
- **FHIR Candidate:** `Patient.birthDate`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with date-like values
- 296 distinct values across 354 non-null rows
- Samples resemble date formats (e.g., '1944-01-18', '2003-02-03')

#### Inferred Facts
- The field likely represents a date of birth due to the format and range of values
- FHIR R4 element 'Patient.birthDate' provides a standard representation for this concept

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.birthDate' (date, 0..1): The date of birth for the individual
- FHIR R4 element 'Patient.multipleBirth[x]' (boolean, 0..1): Whether patient is part of a multiple birth
- FHIR R4 element 'Patient.maritalStatus' (CodeableConcept, 0..1): Marital (civil) status of a patient

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.birthDate)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PATIENT_MASTER.GENDER`

- **Semantic Meaning:** Patient's gender
- **FHIR Candidate:** `Patient.gender`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type is 'TEXT'
- 2 distinct values: 'male' and 'female'
- 0.0% null values across 354 non-null rows

#### Inferred Facts
- Values align with FHIR R4 Patient.gender element options
- FHIR R4 structure suggests a coded element, but values are not explicitly coded

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.gender' (code, 0..1): male | female | other | unknown
- FHIR R4 element 'Patient.contact.gender' (code, 0..1): male | female | other | unknown
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.gender)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PATIENT_MASTER.LAST_NAME`

- **Semantic Meaning:** Patient's last name
- **FHIR Candidate:** `Patient.name`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type is 'TEXT'
- 265 distinct values across 354 non-null rows
- 0.0% null values

#### Inferred Facts
- The field likely represents a part of the patient's name
- FHIR R4 element 'Patient.name' is a possible match

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.name' (HumanName, 0..*): A name associated with the patient
- FHIR R4 element 'Patient.contact.name' (HumanName, 0..1): A name associated with the contact person
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.name)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PATIENT_MASTER.FIRST_NAME`

- **Semantic Meaning:** Patient's given name
- **FHIR Candidate:** `Patient.name`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.95) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.95` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type is 'TEXT'
- 100% unique non-null values across 354 rows
- Samples contain multiple names separated by spaces

#### Inferred Facts
- The field likely contains full names or multiple names
- FHIR R4 'Patient.name' element is a close match for this field

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.name' (HumanName, 0..*): A name associated with the patient
- FHIR R4 element 'Patient.contact.name' (HumanName, 0..1): A name associated with the contact person
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.name)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `VITAL_SIGNS.OBSERVATION_ID`

- **Semantic Meaning:** Unique identifier for a vital sign observation
- **FHIR Candidate:** `Observation.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type is 'TEXT'
- 100% unique non-null values across 49902 rows
- 0.0% null values
- Samples resemble UUIDs (universally unique identifiers)

#### Inferred Facts
- The field likely serves as a primary identifier for vital sign observations
- The values are likely generated to ensure uniqueness

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `VITAL_SIGNS.PATIENT_ID`

- **Semantic Meaning:** Patient Identifier
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 354 distinct values
- 0.0% null values across 49902 non-null rows
- Samples of values resemble UUIDs
- Full containment overlap with DIAGNOSIS.PATIENT_ID, ENCOUNTER.PATIENT_ID, and PATIENT_MASTER.PATIENT_ID

#### Inferred Facts
- The field likely represents a foreign key referencing patient identifiers
- The values are consistent with FHIR R4 Patient.identifier (Identifier, 0..*)

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `VITAL_SIGNS.LOINC_CODE`

- **Semantic Meaning:** LOINC code for vital sign observations
- **FHIR Candidate:** `Observation.code`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (1.00) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `1.00` (Evidence Strength: `STRONG`)

#### Observed Facts
- Field type is TEXT
- 20 distinct LOINC codes across 49902 non-null rows
- Sample values include known LOINC codes (e.g., 8302-2, 72514-3, 29463-7)

#### Inferred Facts
- LOINC codes represent standardized vital sign measurements
- Field values are likely used for indexing or referencing specific vital sign observations

#### Retrieved Authoritative Evidence
- Official LOINC concept 8302-2: 'Body height'. Component: Body height, System: ^Patient, Class: BDYHGT.ATOM, Recommended UCUM units: '[in_us];cm;m'
- Official LOINC concept 72514-3: 'Pain severity - 0-10 verbal numeric rating [Score] - Reported'. Component: Pain severity - 0-10 verbal numeric rating, System: ^Patient, Class: H&P.HX, Recommended UCUM units: '{score}'
- Official LOINC concept 29463-7: 'Body weight'. Component: Body weight, System: ^Patient, Class: BDYWGT.ATOM, Recommended UCUM units: '[lb_av];kg'
- Official LOINC concept 39156-5: 'Body mass index (BMI) [Ratio]'. Component: Body mass index, System: ^Patient, Class: BDYWGT.ATOM, Recommended UCUM units: 'kg/m2'

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (LOINC, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.code)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `VITAL_SIGNS.MEASUREMENT_NAME`

- **Semantic Meaning:** Type of vital sign measurement
- **FHIR Candidate:** `Observation.code`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- Text type with 21 distinct values
- 0.0% null rate across 49902 non-null rows
- Sample values include 'Body Height', 'Pain severity - 0-10 verbal numeric rating [Score] - Reported', and 'Body Weight'

#### Inferred Facts
- Measurement names are standardized and correspond to LOINC codes
- FHIR R4 Observation.code element is relevant for vital sign measurements

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.code' (CodeableConcept, Cardinality: 1..1). Description: Type of observation (code / type) [Binding: example]

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (LOINC, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.code)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `VITAL_SIGNS.MEASUREMENT_VALUE`

- **Semantic Meaning:** Quantitative measurement value of a vital sign
- **FHIR Candidate:** `Observation.valueQuantity.value`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.81) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.81` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Field type is REAL
- 10.9% null values
- 8944 distinct values across 44463 non-null rows
- Sample values include decimal numbers (e.g., 191.4, 30.33)

#### Inferred Facts
- Measurement values are likely to represent various vital sign quantities (e.g., blood pressure, heart rate, temperature)
- FHIR R4 element 'Observation.value[x]' and 'Observation.component.value[x]' provide a structural framework for representing measurement values

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Observation.value[x]' (Quantity, 0..1): Actual result
- FHIR R4 element 'Observation.component.value[x]' (Quantity, 0..1): Actual component result
- FHIR R4 element 'Observation' (Element, 0..*): Measurements and simple assertions

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.valueQuantity.value)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `VITAL_SIGNS.MEASUREMENT_UNIT`

- **Semantic Meaning:** Unit of measurement for vital signs
- **FHIR Candidate:** `Observation.valueQuantity.unit`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.99) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.99` (Evidence Strength: `STRONG`)

#### Observed Facts
- Field type is TEXT
- 9 distinct values across 44463 non-null rows
- 10.9% null values
- Sample values include 'cm', '{score}', 'kg', 'kg/m2', '/min'

#### Inferred Facts
- Field represents a variety of physical measurement units
- Units are consistent with UCUM standard clinical units

#### Retrieved Authoritative Evidence
- Standard clinical UCUM unit 'cm': Centimeter (Length)
- Standard clinical UCUM unit '{score}': Arbitrary clinical score unit
- Standard clinical UCUM unit 'kg': Kilogram (Mass)
- Standard clinical UCUM unit '/min': Per minute (Frequency)

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (UCUM, FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.valueQuantity.unit)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `VITAL_SIGNS.MEASUREMENT_DATE`

- **Semantic Meaning:** Date and time of vital sign measurement
- **FHIR Candidate:** `Observation.effectiveDateTime`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.92) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.92` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 11336 distinct values
- Samples indicate ISO 8601 datetime format
- Moderate value overlap with MEDICATION.PRESCRIBED_DATE and ENCOUNTER.START_DATE

#### Inferred Facts
- MEASUREMENT_DATE likely represents a timestamp for vital sign measurements
- FHIR R4 structure suggests a primitive dateTime element for such measurements

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.birthDate' (date, 0..1): The date of birth for the individual
- FHIR R4 element 'Condition.recordedDate' (dateTime, 0..1): Date record was first recorded
- FHIR R4 element 'Observation' (Element, 0..*): Measurements and simple assertions

#### Provenance & Audit Trail
- Database Checksum: 380fbfc747c2...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.effectiveDateTime)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

