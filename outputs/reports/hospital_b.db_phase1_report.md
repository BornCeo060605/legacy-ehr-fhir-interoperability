# Phase 1 HL7 FHIR R4 Interoperability & Mapping Audit Report

- **Run ID:** `PHASE1_RUN_20260926_102913_4b8df4`
- **Target Database:** `hospital_b.db`
- **SHA256 Fingerprint:** `2608b54478426cc9d28d21d59a16e201116cf67a20ad7e2e25b550a35f6f97f1`
- **Timestamp:** `2026-09-26T10:55:02.315059`
- **LLM Provider / Model:** `openrouter` / `meta-llama/llama-3.3-70b-instruct`
- **Accepted Mappings:** 27 | **Review:** 2 | **Unsupported:** 1

## Summary Table

| Legacy Field        | Semantic Meaning                                         | FHIR Candidate                              |   Confidence | Evidence   | Decision        | Rule                        |
|---------------------|----------------------------------------------------------|---------------------------------------------|--------------|------------|-----------------|-----------------------------|
| DX_HISTORY.DX_ID    | Unique identifier for a diagnosis or observation         | Observation.identifier                      |         0.96 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| DX_HISTORY.PID      | Patient Identifier Reference                             | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| DX_HISTORY.DX_CD    | Condition or diagnosis code                              | Condition.code                              |         0.86 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| DX_HISTORY.DX_NM    | Clinical diagnosis or finding concept display name       | Condition.code                              |         0.85 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| DX_HISTORY.ONSET_DT | Date of onset for a medical condition or diagnosis       | Condition.onsetDateTime                     |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| DX_HISTORY.DX_STAT  | Diagnosis status in patient's medical history            | Condition.clinicalStatus                    |         0.69 | WEAK       | **REVIEW**      | `R3_MANUAL_REVIEW_REQUIRED` |
| OBS.OBS_ID          | Unique Observation Identifier                            | Observation.identifier                      |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| OBS.PID             | Patient Identifier Reference                             | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| OBS.OBS_CD          | LOINC code for clinical observation                      | Observation.code                            |         0.99 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| OBS.OBS_NM          | Display name of a clinical observation or measurement    | Observation.code                            |         0.83 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| OBS.OBS_VAL         | Quantitative measurement value                           | Observation.valueQuantity.value             |         0.78 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| OBS.OBS_UNIT        | Unit of measurement for an observation                   | Observation.valueQuantity.unit              |         0.99 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| OBS.OBS_DT          | Observation Date and Time                                | Observation.effectiveDateTime               |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| PT_MST.PID          | Patient Primary Identifier                               | Patient.identifier                          |         0.93 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| PT_MST.DOB          | Date of Birth                                            | Patient.birthDate                           |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| PT_MST.SEX_CD       | Patient Sex                                              | Patient.gender                              |         0.63 | WEAK       | **REVIEW**      | `R3_MANUAL_REVIEW_REQUIRED` |
| PT_MST.LNAME        | Patient Last Name                                        | Patient.name.family                         |         0.9  | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| PT_MST.FNAME        | Patient Full Name                                        | Patient.name                                |         0.86 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| RX.RX_ID            | Unique identifier for a prescription or medication order | MedicationRequest.identifier                |         0.91 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| RX.PID              | Patient Identifier Reference                             | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| RX.RX_CD            | RxNorm medication code                                   | MedicationRequest.medicationCodeableConcept |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| RX.RX_NM            | Medication Name                                          | MedicationRequest.medicationCodeableConcept |         0.86 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| RX.RX_STAT          | Medication request status                                | MedicationRequest.status                    |         0.85 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| RX.RX_DT            | Date of medication prescription or administration        | MedicationRequest.authoredOn                |         0.77 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| VISIT.VISIT_ID      | Unique identifier for a visit                            | Encounter.identifier                        |         0.91 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| VISIT.PID           | Patient Identifier                                       | Patient.identifier                          |         0.98 | STRONG     | **ACCEPTED**    | `R1_STRONG_ACCEPTED`        |
| VISIT.START_DT      | Visit start date                                         | Encounter.period.start                      |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| VISIT.END_DT        | Visit End Date                                           | Encounter.period.end                        |         0.82 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| VISIT.VISIT_TYPE    | Visit type code                                          | Encounter.type                              |         0.83 | MODERATE   | **ACCEPTED**    | `R2_MODERATE_ACCEPTED`      |
| VISIT.RSN_TXT       | Completely unpopulated legacy field 'RSN_TXT'            | VISIT.RSN_TXT                               |         0.1  | NONE       | **UNSUPPORTED** | `R0_UNPOPULATED_FIELD`      |

## Detailed Field Evidence & Provenance

### Field: `DX_HISTORY.DX_ID`

- **Semantic Meaning:** Unique identifier for a diagnosis or observation
- **FHIR Candidate:** `Observation.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.96) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.96` (Evidence Strength: `STRONG`)

#### Observed Facts
- TEXT type with 100% unique non-null values
- 13953 distinct values across 13953 non-null rows
- 0.0% null values

#### Inferred Facts
- Candidate identifier due to uniqueness and format
- Alignment with FHIR R4 Observation.identifier suggests a business identifier for an observation

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `DX_HISTORY.PID`

- **Semantic Meaning:** Patient Identifier Reference
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 354 distinct values
- 0.0% null values across 13953 non-null rows
- Values in DX_HISTORY.PID are fully contained in OBS.PID, PT_MST.PID, and VISIT.PID

#### Inferred Facts
- DX_HISTORY.PID is a foreign-key reference to patient identifiers
- The values in DX_HISTORY.PID are consistent with FHIR R4 Patient.identifier

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `DX_HISTORY.DX_CD`

- **Semantic Meaning:** Condition or diagnosis code
- **FHIR Candidate:** `Condition.code`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.86) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.86` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'TEXT'
- 236 distinct values across 13953 non-null rows
- Samples of values match SNOMED_CT code format (e.g., '224299000', '162864005')
- FHIR R4 'Condition.code' element is a CodeableConcept with a binding example

#### Inferred Facts
- The field likely represents a coded diagnosis or condition based on the sample values and FHIR R4 evidence
- SNOMED_CT is a comprehensive clinical terminology used for coding diagnoses and conditions

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Condition.code' (CodeableConcept, Cardinality: 0..1). Description: Identification of the condition, problem or diagnosis [Binding: example]

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (SNOMED_CT, OHDSI, FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.code)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `DX_HISTORY.DX_NM`

- **Semantic Meaning:** Clinical diagnosis or finding concept display name
- **FHIR Candidate:** `Condition.code`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.85) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.85` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Field type is TEXT
- 236 distinct values across 13953 non-null rows
- Sample values contain SNOMED_CT-like concepts (e.g., 'Osteoarthritis of knee (disorder)')
- FHIR R4 Condition.code element is a CodeableConcept, which aligns with the proposed semantic role

#### Inferred Facts
- The field likely represents a display name for a clinical concept, given the presence of descriptive text
- The use of SNOMED_CT terminology is inferred based on the sample values and the exclusion of other terminologies

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Condition.code' (CodeableConcept, Cardinality: 0..1). Description: Identification of the condition, problem or diagnosis [Binding: example]

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (SNOMED_CT, OHDSI, FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.code)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `DX_HISTORY.ONSET_DT`

- **Semantic Meaning:** Date of onset for a medical condition or diagnosis
- **FHIR Candidate:** `Condition.onsetDateTime`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with 5647 distinct values
- Strong value containment with VISIT.START_DT and VISIT.END_DT
- Moderate value overlap with RX.RX_DT

#### Inferred Facts
- DX_HISTORY.ONSET_DT likely represents a timestamp for a medical condition or diagnosis
- The field's values are likely dates in the format 'MM/DD/YYYY'

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Condition.onset[x]' (dateTime, 0..1): Estimated or actual date,  date-time, or age
- FHIR R4 element 'MedicationRequest.eventHistory' (Reference, 0..*): A list of events of interest in the lifecycle
- FHIR R4 element 'Encounter.statusHistory' (BackboneElement, 0..*): List of past encounter statuses

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.onsetDateTime)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `DX_HISTORY.DX_STAT`

- **Semantic Meaning:** Diagnosis status in patient's medical history
- **FHIR Candidate:** `Condition.clinicalStatus`
- **Decision:** **REVIEW** (Rule: `R3_MANUAL_REVIEW_REQUIRED`)
- **Decision Reason:** Candidate mapping proposed but requires clinical expert review (Confidence: 0.69, Strength: WEAK).
- **Mapping Confidence:** `0.69` (Evidence Strength: `WEAK`)

#### Observed Facts
- Observed type is 'TEXT'
- 2 distinct values: 'active' and 'resolved'
- 0.0% null values across 13953 non-null rows

#### Inferred Facts
- The field likely represents a status or state of a diagnosis in a patient's medical history
- The values 'active' and 'resolved' suggest a binary status indicator

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.statusHistory' (BackboneElement, 0..*): List of past encounter statuses
- FHIR R4 element 'Encounter.statusHistory.period' (Period, 1..1): The time that the episode was in the specified status
- FHIR R4 element 'Encounter.statusHistory.id' (http://hl7.org/fhirpath/System.String, 0..1): Unique id for inter-element referencing

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Condition.clinicalStatus)
- Deterministic Decision Engine (R3_MANUAL_REVIEW_REQUIRED)

---

### Field: `OBS.OBS_ID`

- **Semantic Meaning:** Unique Observation Identifier
- **FHIR Candidate:** `Observation.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- OBS.OBS_ID has 100% unique non-null values
- OBS.OBS_ID has a data type of TEXT
- OBS.OBS_ID has 0.0% null values
- Sample values resemble UUIDs (Universally Unique Identifiers)

#### Inferred Facts
- OBS.OBS_ID is likely a primary identifier for observations
- The values in OBS.OBS_ID are probably generated to ensure uniqueness

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `OBS.PID`

- **Semantic Meaning:** Patient Identifier Reference
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 354 distinct values across 49902 non-null rows
- 100.0% overlap between OBS.PID and DX_HISTORY.PID
- 100.0% overlap between OBS.PID and PT_MST.PID

#### Inferred Facts
- OBS.PID is a foreign-key reference to patient identifiers
- Values in OBS.PID are consistent with FHIR R4 Patient.identifier

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `OBS.OBS_CD`

- **Semantic Meaning:** LOINC code for clinical observation
- **FHIR Candidate:** `Observation.code`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.99) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.99` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type is 'TEXT'
- 20 distinct values across 49902 non-null rows
- Sample values match LOINC codes (e.g., 8302-2, 72514-3, 29463-7)

#### Inferred Facts
- The field likely represents a standardized code for clinical observations
- The codes are likely used to identify specific vital signs or measurements

#### Retrieved Authoritative Evidence
- Official LOINC concept 8302-2: 'Body height'. Component: Body height, System: ^Patient, Class: BDYHGT.ATOM, Recommended UCUM units: '[in_us];cm;m'
- Official LOINC concept 72514-3: 'Pain severity - 0-10 verbal numeric rating [Score] - Reported'. Component: Pain severity - 0-10 verbal numeric rating, System: ^Patient, Class: H&P.HX, Recommended UCUM units: '{score}'
- Official LOINC concept 29463-7: 'Body weight'. Component: Body weight, System: ^Patient, Class: BDYWGT.ATOM, Recommended UCUM units: '[lb_av];kg'
- Official LOINC concept 39156-5: 'Body mass index (BMI) [Ratio]'. Component: Body mass index, System: ^Patient, Class: BDYWGT.ATOM, Recommended UCUM units: 'kg/m2'

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (LOINC, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.code)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `OBS.OBS_NM`

- **Semantic Meaning:** Display name of a clinical observation or measurement
- **FHIR Candidate:** `Observation.code`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.83) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.83` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT'; 21 distinct values across 49902 non-null rows (0.0% null); Samples: ['Body Height', 'Pain severity - 0-10 verbal numeric rating [Score] - Reported', 'Body Weight']

#### Inferred Facts
- Format and content of values suggest a connection to LOINC terminology, which is commonly used for laboratory and clinical measurements
- Presence of other columns like 'OBS_CD' and 'OBS_UNIT' in the same table implies a structured observation or measurement data model

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.code' (CodeableConcept, Cardinality: 1..1). Description: Type of observation (code / type) [Binding: example]

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (LOINC, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.code)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `OBS.OBS_VAL`

- **Semantic Meaning:** Quantitative measurement value
- **FHIR Candidate:** `Observation.valueQuantity.value`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.78) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.78` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'REAL'
- 10.9% null values
- 8944 distinct values across 44463 non-null rows
- Sample values include decimal numbers (e.g., '191.4', '30.33')

#### Inferred Facts
- The field likely represents a numerical measurement
- The presence of decimal numbers suggests a continuous value

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Observation.identifier' (Identifier, 0..*): Business Identifier for observation
- FHIR R4 element 'Observation.category' (CodeableConcept, 0..*): Classification of  type of observation
- FHIR R4 element 'Observation.code' (CodeableConcept, 1..1): Type of observation (code / type)

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.valueQuantity.value)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `OBS.OBS_UNIT`

- **Semantic Meaning:** Unit of measurement for an observation
- **FHIR Candidate:** `Observation.valueQuantity.unit`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.99) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.99` (Evidence Strength: `STRONG`)

#### Observed Facts
- Field type is 'TEXT'
- 9 distinct values across 44463 non-null rows
- Samples include known UCUM units such as 'cm', 'kg', and '/min'

#### Inferred Facts
- The field is likely representing units of measurement for various observations
- The presence of '{score}' suggests that the field may also include arbitrary clinical score units

#### Retrieved Authoritative Evidence
- Standard clinical UCUM unit 'cm': Centimeter (Length)
- Standard clinical UCUM unit '{score}': Arbitrary clinical score unit
- Standard clinical UCUM unit 'kg': Kilogram (Mass)
- Standard clinical UCUM unit '/min': Per minute (Frequency)

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (UCUM, FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.valueQuantity.unit)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `OBS.OBS_DT`

- **Semantic Meaning:** Observation Date and Time
- **FHIR Candidate:** `Observation.effectiveDateTime`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- 6517 distinct values across 49902 non-null rows
- Samples: ['05/30/2017', '06/05/2018', '06/11/2019']
- Strong value containment with VISIT.END_DT, VISIT.START_DT, and RX.RX_DT

#### Inferred Facts
- OBS.OBS_DT likely represents a timestamp for an observation or event
- Foreign key relationships suggest OBS.OBS_DT is a reference to other tables' date fields

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Observation.identifier' (Identifier, 0..*): Business Identifier for observation
- FHIR R4 element 'Observation.category' (CodeableConcept, 0..*): Classification of  type of observation
- FHIR R4 element 'Observation.code' (CodeableConcept, 1..1): Type of observation (code / type)

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Observation.effectiveDateTime)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `PT_MST.PID`

- **Semantic Meaning:** Patient Primary Identifier
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.93) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.93` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT' with 354 distinct values across 354 non-null rows
- 100% unique non-null values, indicating a candidate identifier
- Relational linkage facts show full containment between PT_MST.PID and other tables (DX_HISTORY.PID, OBS.PID)
- Sample values resemble UUIDs, consistent with identifier format

#### Inferred Facts
- PT_MST.PID is likely a primary identifier for patients, given its uniqueness and relational links
- The identifier is used consistently across related tables, supporting its role as a primary identifier

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PT_MST.DOB`

- **Semantic Meaning:** Date of Birth
- **FHIR Candidate:** `Patient.birthDate`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT'
- 296 distinct values across 354 non-null rows
- Samples: ['01/18/1944', '02/03/2003', '02/07/1962']

#### Inferred Facts
- Values appear to be in the format of dates (MM/DD/YYYY)
- Field name 'DOB' is a common abbreviation for 'Date of Birth'

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest.priorPrescription' (Reference, 0..1): An order/prescription that is being replaced
- FHIR R4 element 'Condition.evidence.code' (CodeableConcept, 0..*): Manifestation/symptom
- FHIR R4 element 'MedicationRequest.intent' (code, 1..1): proposal | plan | order | original-order | reflex-order | filler-order | instance-order | option

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.birthDate)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `PT_MST.SEX_CD`

- **Semantic Meaning:** Patient Sex
- **FHIR Candidate:** `Patient.gender`
- **Decision:** **REVIEW** (Rule: `R3_MANUAL_REVIEW_REQUIRED`)
- **Decision Reason:** Candidate mapping proposed but requires clinical expert review (Confidence: 0.63, Strength: WEAK).
- **Mapping Confidence:** `0.63` (Evidence Strength: `WEAK`)

#### Observed Facts
- Observed type 'TEXT'
- 2 distinct values across 354 non-null rows
- Samples: ['1', '2']

#### Inferred Facts
- Values '1' and '2' likely represent male and female, respectively
- Field is not directly related to FHIR R4 elements provided in external evidence

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest.priorPrescription' (Reference, 0..1): An order/prescription that is being replaced
- FHIR R4 element 'Condition.evidence.code' (CodeableConcept, 0..*): Manifestation/symptom
- FHIR R4 element 'MedicationRequest.intent' (code, 1..1): proposal | plan | order | original-order | reflex-order | filler-order | instance-order | option

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.gender)
- Deterministic Decision Engine (R3_MANUAL_REVIEW_REQUIRED)

---

### Field: `PT_MST.LNAME`

- **Semantic Meaning:** Patient Last Name
- **FHIR Candidate:** `Patient.name.family`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.90) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.90` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type is 'TEXT'
- 265 distinct values across 354 non-null rows
- Sample values resemble last names with numeric suffixes

#### Inferred Facts
- The field likely contains patient last names due to the presence of common surname patterns
- The numeric suffixes may indicate a unique identifier or a specific formatting convention

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest.priorPrescription' (Reference, 0..1): An order/prescription that is being replaced
- FHIR R4 element 'Condition.evidence.code' (CodeableConcept, 0..*): Manifestation/symptom
- FHIR R4 element 'MedicationRequest.intent' (code, 1..1): proposal | plan | order | original-order | reflex-order | filler-order | instance-order | option

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.name.family)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `PT_MST.FNAME`

- **Semantic Meaning:** Patient Full Name
- **FHIR Candidate:** `Patient.name`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.86) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.86` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT'
- 354 distinct values across 354 non-null rows (0.0% null)
- 100% unique non-null values (candidate identifier)

#### Inferred Facts
- The field likely contains a combination of first and last names
- The values appear to be in a format that is not standardized, with numbers and letters mixed together

#### Retrieved Authoritative Evidence
- FHIR R4 element 'MedicationRequest.priorPrescription' (Reference, 0..1): An order/prescription that is being replaced
- FHIR R4 element 'Condition.evidence.code' (CodeableConcept, 0..*): Manifestation/symptom
- FHIR R4 element 'MedicationRequest.intent' (code, 1..1): proposal | plan | order | original-order | reflex-order | filler-order | instance-order | option

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.name)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `RX.RX_ID`

- **Semantic Meaning:** Unique identifier for a prescription or medication order
- **FHIR Candidate:** `MedicationRequest.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.91) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.91` (Evidence Strength: `STRONG`)

#### Observed Facts
- TEXT type with 100% unique non-null values
- 21625 distinct values across 21625 non-null rows (0.0% null)
- Samples resemble UUIDs (universally unique identifiers)

#### Inferred Facts
- The field likely serves as a primary key or identifier for prescription or medication order records
- The use of UUID-like values suggests a deliberate design choice for uniqueness and identifier stability

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `RX.PID`

- **Semantic Meaning:** Patient Identifier Reference
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- RX.PID has 347 distinct text values across 21625 non-null rows
- RX.PID values are fully contained in DX_HISTORY.PID, OBS.PID, and PT_MST.PID, indicating a foreign-key patient reference

#### Inferred Facts
- RX.PID is likely a reference to a patient identifier, given its overlap with other tables containing patient information
- The use of UUID-like values in RX.PID suggests a unique identifier for each patient

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `RX.RX_CD`

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
- RxNorm codes represent specific medication entities
- FHIR R4 MedicationRequest.medicationCodeableConcept aligns with RxNorm terminology

#### Retrieved Authoritative Evidence
- Official NLM RxNorm concept RxCUI 309362: 'clopidogrel 75 MG Oral Tablet' (Term Type: SCD)
- Official NLM RxNorm concept RxCUI 312961: 'simvastatin 20 MG Oral Tablet' (Term Type: SCD)
- Official NLM RxNorm concept RxCUI 866412: '24 HR metoprolol succinate 100 MG Extended Release Oral Tablet' (Term Type: SCD)
- Official NLM RxNorm concept RxCUI 705129: 'nitroglycerin 0.4 MG/ACTUAT Mucosal Spray' (Term Type: SCD)

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (RxNorm, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.medicationCodeableConcept)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `RX.RX_NM`

- **Semantic Meaning:** Medication Name
- **FHIR Candidate:** `MedicationRequest.medicationCodeableConcept`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.86) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.86` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'TEXT'
- 145 distinct values across 12804 non-null rows
- 40.8% null values
- Sample values resemble medication names with strengths and forms

#### Inferred Facts
- The field likely represents a medication concept display name
- RxNorm is the primary terminology for medication concepts in US healthcare

#### Retrieved Authoritative Evidence
- Official FHIR R4 choice element 'MedicationRequest.medicationCodeableConcept' (specialization of MedicationRequest.medication[x], Cardinality: 1..1). Description: Medication to be taken

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (RxNorm, FHIR_R4, OHDSI)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.medicationCodeableConcept)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `RX.RX_STAT`

- **Semantic Meaning:** Medication request status
- **FHIR Candidate:** `MedicationRequest.status`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.85) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.85` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT'
- 2 distinct values: 'completed' and 'active'
- 0.0% null values across 21625 non-null rows

#### Inferred Facts
- Potential relationship to MedicationRequest.statusReason in FHIR R4
- Possible alignment with Encounter.statusHistory in FHIR R4, but less likely given context

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.maritalStatus' (CodeableConcept, 0..1): Marital (civil) status of a patient
- FHIR R4 element 'MedicationRequest.statusReason' (CodeableConcept, 0..1): Reason for current status
- FHIR R4 element 'Encounter.statusHistory' (BackboneElement, 0..*): List of past encounter statuses

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.status)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `RX.RX_DT`

- **Semantic Meaning:** Date of medication prescription or administration
- **FHIR Candidate:** `MedicationRequest.authoredOn`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.77) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.77` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with distinct date-like values
- Strong value containment with VISIT.END_DT and VISIT.START_DT
- Strong value containment with OBS.OBS_DT

#### Inferred Facts
- RX.RX_DT likely represents a timestamp for medication-related events
- The field's relationship with VISIT.END_DT and VISIT.START_DT suggests a connection to patient visits

#### Retrieved Authoritative Evidence
- No external evidence retrieved (excluded or unpopulated)

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (MedicationRequest.authoredOn)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `VISIT.VISIT_ID`

- **Semantic Meaning:** Unique identifier for a visit
- **FHIR Candidate:** `Encounter.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.91) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.91` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 22612 distinct values across 22612 non-null rows
- 100% unique non-null values
- Sample values resemble UUIDs

#### Inferred Facts
- VISIT_ID is likely a primary identifier for visits due to its uniqueness and distribution
- The field's structure and sample values are consistent with FHIR identifier elements

#### Retrieved Authoritative Evidence
- Official FHIR R4 element 'Observation.identifier' (Identifier, Cardinality: 0..*). Description: Business Identifier for observation

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `VISIT.PID`

- **Semantic Meaning:** Patient Identifier
- **FHIR Candidate:** `Patient.identifier`
- **Decision:** **ACCEPTED** (Rule: `R1_STRONG_ACCEPTED`)
- **Decision Reason:** High mapping confidence (0.98) corroborated by strong terminology and FHIR structural evidence.
- **Mapping Confidence:** `0.98` (Evidence Strength: `STRONG`)

#### Observed Facts
- Observed type 'TEXT'
- 354 distinct values across 22612 non-null rows
- Values in DX_HISTORY.PID, OBS.PID, and PT_MST.PID are fully contained in VISIT.PID

#### Inferred Facts
- VISIT.PID is a foreign key referencing patient identifiers
- Values in VISIT.PID are consistent with FHIR R4 Identifier type

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.hospitalization.dietPreference' (CodeableConcept, 0..*): Diet preferences reported by the patient
- FHIR R4 element 'Patient.identifier' (Identifier, 0..*): An identifier for this patient
- FHIR R4 element 'Patient.active' (boolean, 0..1): Whether this patient's record is in active use

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Patient.identifier)
- Deterministic Decision Engine (R1_STRONG_ACCEPTED)

---

### Field: `VISIT.START_DT`

- **Semantic Meaning:** Visit start date
- **FHIR Candidate:** `Encounter.period.start`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with 9235 distinct values across 22612 non-null rows
- Samples of values are in the format 'MM/DD/YYYY'
- Strong value containment with DX_HISTORY.ONSET_DT, OBS.OBS_DT, and RX.RX_DT suggests a reference relationship

#### Inferred Facts
- VISIT.START_DT is likely a date field representing the start of a visit or encounter
- The field has a high degree of overlap with other date fields, indicating a potential foreign key relationship

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.period' (Period, 0..1): The start and end time of the encounter

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.period.start)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `VISIT.END_DT`

- **Semantic Meaning:** Visit End Date
- **FHIR Candidate:** `Encounter.period.end`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.82) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.82` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type 'TEXT' with 9212 distinct values across 22612 non-null rows
- Sample values are in the format 'MM/DD/YYYY'
- Strong value containment with OBS.OBS_DT, DX_HISTORY.ONSET_DT, and RX.RX_DT suggests a reference to a visit or encounter end date

#### Inferred Facts
- The field VISIT.END_DT likely represents the end date of a patient visit or encounter
- The field is likely used to track the duration of a visit or encounter

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Patient.gender' (code, 0..1): male | female | other | unknown
- FHIR R4 element 'Patient.contact.gender' (code, 0..1): male | female | other | unknown
- FHIR R4 element 'Patient.contact' (BackboneElement, 0..*): A contact party (e.g. guardian, partner, friend) for the patient

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.period.end)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `VISIT.VISIT_TYPE`

- **Semantic Meaning:** Visit type code
- **FHIR Candidate:** `Encounter.type`
- **Decision:** **ACCEPTED** (Rule: `R2_MODERATE_ACCEPTED`)
- **Decision Reason:** Sufficient mapping confidence (0.83) backed by MODERATE evidence strength.
- **Mapping Confidence:** `0.83` (Evidence Strength: `MODERATE`)

#### Observed Facts
- Observed type is 'TEXT'
- 5 distinct values across 22612 non-null rows
- Sample values include 'AMB', 'IMP', 'EMER', 'VR', 'HH'

#### Inferred Facts
- FHIR R4 Encounter.type and Encounter.serviceType are potential semantic matches
- The field likely represents a specific type of encounter or service

#### Retrieved Authoritative Evidence
- FHIR R4 element 'Encounter.type' (CodeableConcept, 0..*): Specific type of encounter
- FHIR R4 element 'Encounter.serviceType' (CodeableConcept, 0..1): Specific type of service
- FHIR R4 element 'Encounter.location.physicalType' (CodeableConcept, 0..1): The physical type of the location (usually the level in the location hierachy - bed room ward etc.)

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (Encounter.type)
- Deterministic Decision Engine (R2_MODERATE_ACCEPTED)

---

### Field: `VISIT.RSN_TXT`

- **Semantic Meaning:** Completely unpopulated legacy field 'RSN_TXT'
- **FHIR Candidate:** `VISIT.RSN_TXT`
- **Decision:** **UNSUPPORTED** (Rule: `R0_UNPOPULATED_FIELD`)
- **Decision Reason:** Column 'RSN_TXT' contains 100% missing values; clinical semantics unobservable.
- **Mapping Confidence:** `0.10` (Evidence Strength: `NONE`)

#### Observed Facts
- Column has 0 non-null values across 22612 rows.

#### Retrieved Authoritative Evidence
- No external evidence retrieved (excluded or unpopulated)

#### Provenance & Audit Trail
- Database Checksum: 2608b5447842...
- Deterministic Schema Profiler
- Schema Intelligence (openrouter)
- Hybrid Retrieval (FHIR_R4)
- Semantic Agent (meta-llama/llama-3.3-70b-instruct)
- FHIR Mapping Agent (VISIT.RSN_TXT)
- Deterministic Decision Engine (R0_UNPOPULATED_FIELD)

---

