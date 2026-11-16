# PSQ-SCO v9.1: ontology structure and data sources

PSQ-SCO is the **PersonaShield Quest Scenario Control Ontology** used for the IJCKG 2026 conference study. It describes the conditions a training scenario should satisfy. It does not contain the original messages, run the language model, or approve a scenario for learner use. This is the conference ontology, not the later journal extension.

Start with the [complete OWL term and source reference](ONTOLOGY_REFERENCE.md). It lists each declared class, object property, datatype property and named individual, including all dataset and source identifiers. The repository README identifies the OWL and the query folder for this copy.

## 1. What the ontology contains

| Module | Main classes and terms | What they do |
| --- | --- | --- |
| Learner and adaptation context | LearnerProfile, LearnerStateSnapshot, PersonaRole, AgeGroup, MacroStage, MicroStage, LearningStage, PerformanceState, TransitionConstraintProfile | Describe who the simulated learner is and which role, stage and difficulty apply. Age bands encode case categories, not inferences about ability. MoodContext is an optional placeholder; the conference experiment does not infer emotion. |
| Scenario and cybersecurity structure | ScenarioTemplate, GeneratedScenario, ScenarioStep, Channel, ScenarioVariant, DifficultyBand, AttackType, RedFlag, SafeIndicator, PersuasionCue, ThreatAction, SafeResponseAction, ATTACKTechnique, CAPECPattern | Describe the controlled design of a case. A template links a channel, malicious or legitimate variant, difficulty and role to the concepts and defensive decisions that the final scenario should contain. Legitimate scenarios are comparison cases. |
| Content quality and validation | ContentQualityRule, SafetyConstraint, ConsistencyConstraint, PersonaFitConstraint, EvidenceCoverageConstraint, RequiredConceptCoverageRule, ConstraintViolation, ScenarioQualityScore, ValidationDecision | Describe checks, their scope and the outcome of validation. The experiment enforces the generation-time checks in Python. The OWL is not a standalone validator. A pass allows further human review, not automatic deployment. |
| Evidence and provenance | EvidencePack, SourceArtifact, Dataset, TheorySource, ProvenanceRecord | Distinguish published references, dataset identities, and the records that explain where a template or claim came from. A dataset node is metadata, not a file or an instruction to read a file. |

An OWL **class** is a type of thing, such as ScenarioTemplate. A **named individual** is a specific graph record of a class, such as DS_ThaiFraudSMS, an individual of Dataset. An **object property** links records (for example, derivedFromDataset links evidence to a dataset). A **datatype property** records a value, such as a date, label or score. Stable identifiers make it possible to follow the same record across OWL, SPARQL, and JSON outputs.

### Competency questions

| Query | Practical question |
| --- | --- |
| CQ1: Scenario selection | Which template matches the case's learner context, channel, variant and difficulty? |
| CQ2: Cybersecurity structure | Which type, indicators, cues and safe responses belong in that template? |
| CQ3: Content quality | Which rules and acceptance or rejection conditions apply? |
| CQ4: Evidence and provenance | Which sources and dataset identifiers support the template, and is the provenance link present? |

The four SELECT queries show the recorded relationships. The eight ASK fixtures test one positive and one negative case per CQ. The [complete reference](ONTOLOGY_REFERENCE.md) also lists the individual templates, rules, evidence packs, and values used by these queries.

## 2. Data and evidence: where each item comes from

The source table in the [OWL reference](ONTOLOGY_REFERENCE.md#evidence-sources-and-datasets-18) contains the citations stored in the graph. MITRE ATT&CK and CAPEC provide classification references; research papers and W3C PROV-O support design, training, retrieval and attribution. A source citation is not a claim that its full text was copied into RAG. The records' retrieval dates are metadata dates, not proof of original collection dates or redistribution rights.

| Dataset individual | Origin and use | Where to find it / release status |
| --- | --- | --- |
| DS_ThaiFraudSMS | Project-held Thai fraud SMS workbook, recorded as smsfraud.xlsx. Used as Thai SMS reference material. The recorded ingestion reads message rows from the fraud sheet and converts them to normalized SMS JSONL. Original collector, sampling, collection dates and redistribution terms are not documented in the release evidence. | Dataset identity is in the OWL. The workbook and its message text are not distributed. There is no confirmed public download. It is not required for the released replay or smoke test. |
| DS_IRSCallTranscript | Project-held phone-scam transcript file; the project recorded it as external empirical voice reference material. The original public landing page and permission to redistribute this copy are not established by the supplied record. | Metadata only in OWL. The file named IRS_CompleteCall_Transcript.pdf is not included. |
| DS_AFNC | Reference data attributed to Thailand's Anti-Fake News Center. The Thai open-data portal offers [AFNC datasets](https://data.go.th/th/dataset/anti-fake-news-center), but the exact published resource corresponding to the project's saved export is not confirmed. It is not the Thai Fraud SMS workbook. | Metadata only in OWL. Use the official portal to identify a suitable authorized reference; the historical CSV is not included. |
| DS_MITRE_STIX_18_1 | MITRE's ATT&CK Enterprise STIX 18.1 snapshot, recorded for taxonomy alignment. | [MITRE ATT&CK STIX data](https://github.com/mitre-attack/attack-stix-data). The full STIX snapshot is not bundled. |
| DS_CAPEC_XML | MITRE's CAPEC XML catalog, recorded for attack-pattern alignment. | [MITRE CAPEC downloads](https://capec.mitre.org/data/downloads.html). The full catalog is not bundled; the moving “latest” download is not a pinned historical snapshot. |
| DS_KnowledgeBaseJSONL | Project-derived JSONL corpus normalized from source collections for retrieval. It depends on the sources and data preparation used for a particular run. | The complete historical corpus and vector index are not bundled. Only a small fictional fixture is included for portability tests. |

### What “collected” means for DS_ThaiFraudSMS

The project catalog describes an XLSX fraud sheet with a count cell followed by message rows. The old preparation code documents reading the first-column messages into the project's Thai SMS JSONL. It identifies a tokenized text copy as a duplicate, not a second independent collection. That information establishes **how the local copy was prepared**, not whether messages were scraped, donated, gathered by a government agency, or obtained from a third-party dataset. We do not assign an upstream collector or licence without evidence.

The dataset identifier remains in the released graph so evidence relationships stay traceable. The storage pointer to the unavailable workbook has been removed from the OWL metadata. A reader should not create that folder or try to obtain a copy to run the public tests. If permission is later established, the team should document custody, collection protocol, licence, a stable source link and an authorized version/hash before including it in a new release.

## 3. How the software uses the data

1. The case manifest supplies the same 120 cases for the four conference modes and three models.
2. The generation engine in ReaLearn uses those controls and, in the relevant modes, the OWL and authorized retrieval data. The structured mode uses a typed packet; the ontology-to-text mode uses verbalized records. The prompt-only baseline does not use RAG.
3. The Python application validator checks the generated JSON against the game schema and scenario controls. The technical evaluator can also score stored results without running Ollama.
4. The public experiment archive pairs the inputs and available settings with 1,440 evaluated output records. It omits full message and call text, contact details, third-party retrieval passages, and model weights. The synthetic four-mode example is separate from those live experiment records.

Use the [data availability notes](../DATA_AVAILABILITY.md) and [README](../README.md) to choose the workflow. **Replaying the archived technical results** does not require the original machine, Ollama or a private dataset. **Generating new outputs under the paper's full settings** also requires compatible model weights, authorized original-equivalent retrieval data, and the original settings that were recorded. The public archive does not provide byte-identical regeneration or full text-based rescoring of the private outputs.
