# PSQ-SCO v9.1 term and source reference

This index is generated from the bundled OWL. See [Ontology and data sources](ONTOLOGY_AND_SOURCES.md)
for the four modules, how the engine uses the ontology, and how to obtain or replace inputs.

The table lists named parents, domains and ranges; inspect the OWL for restrictions and anonymous expressions.
A blank entry means that the indexed annotation is not declared, not that the term has no semantics.

## Classes (74)

| Class | Label | Named parents | Meaning in the OWL |
| --- | --- | --- | --- |
| `prov:Entity` | — | — | — |
| `psq:ATTACKTechnique` | MITRE ATT&CK technique | `psq:ScenarioKnowledgeEntity` | Ontology class representing MITRE ATT&CK technique in the PersonaShield domain model. |
| `psq:AdvancedDifficultyBand` | Advanced scenario difficulty | `psq:DifficultyBand` | Leaf difficulty class for subtle cues, high ambiguity, reduced guidance, and justified decisions. Maps to engine code hard. |
| `psq:Age15To21Group` | Age 15 to 21 group | `psq:YoungerEngineAgeGroup` | Leaf class for the inclusive engine band from age 15 through age 21. |
| `psq:Age22To35Group` | Age 22 to 35 group | `psq:YoungerEngineAgeGroup` | Leaf class for the inclusive engine band from age 22 through age 35. |
| `psq:Age36To45Group` | Age 36 to 45 group | `psq:MiddleEngineAgeGroup` | Leaf class for the inclusive engine band from age 36 through age 45. |
| `psq:Age46To59Group` | Age 46 to 59 group | `psq:MiddleEngineAgeGroup` | Leaf class for the inclusive engine band from age 46 through age 59. |
| `psq:Age60To90Group` | Age 60 to 90 group | `psq:OlderEngineAgeGroup` | Leaf class for the inclusive engine band from age 60 through age 90. |
| `psq:AgeGroup` | Age group | `psq:LearnerKnowledgeEntity` | Engine adaptation category represented by inclusive age boundaries; it does not infer ability, vulnerability, or competence. |
| `psq:AttackType` | Attack type | `psq:ScenarioCharacteristic` | Controlled classification of malicious social engineering or legitimate comparison communication. |
| `psq:BusinessPersonaRole` | Business-function persona role | `psq:PersonaRole` | Intermediate role category for finance, human-resources, and management work contexts. |
| `psq:CAPECPattern` | CAPEC pattern | `psq:ScenarioKnowledgeEntity` | Ontology class representing CAPEC pattern in the PersonaShield domain model. |
| `psq:Channel` | Channel | `psq:ScenarioCharacteristic` | Communication medium through which a scenario is presented. |
| `psq:ConsistencyConstraint` | Consistency constraint | `psq:ContentQualityRule` | Rule checking channel, variant, persona, difficulty, and template consistency. |
| `psq:ConstraintViolation` | Constraint violation | `psq:ContentQualityKnowledgeEntity` | Detected violation of a scenario-control rule. |
| `psq:ContentQualityKnowledgeEntity` | Content quality knowledge entity | `psq:DomainEntity` | Scenario-control terms used to validate and score generated scenario candidates. |
| `psq:ContentQualityRule` | Content quality rule | `psq:ContentQualityKnowledgeEntity` | Acceptance or rejection rule applied to generated scenario candidates. |
| `psq:Dataset` | Dataset | `psq:SourceArtifact` | Ontology class representing Dataset in the PersonaShield domain model. |
| `psq:DevelopingDifficultyBand` | Developing scenario difficulty | `psq:DifficultyBand` | Leaf difficulty class for mixed cues, moderate ambiguity, and applied verification. Maps to engine code moderate. |
| `psq:DifficultyBand` | Scenario difficulty band | `psq:ScenarioCharacteristic` | Scenario-control challenge category with the canonical values introductory, developing, and advanced. Each value maps to a fixed engine code. |
| `psq:DomainEntity` | PersonaShield domain entity | — | Top class for entities represented in the PersonaShield ontology-based knowledge graph. |
| `psq:EmailChannel` | Email channel | `psq:TextBasedChannel` | Leaf class for asynchronous email communication. |
| `psq:ErrorType` | Error type | `psq:ContentQualityKnowledgeEntity` | Controlled error category used in scenario-control error analysis. |
| `psq:EvidenceCoverageConstraint` | Evidence coverage constraint | `psq:ContentQualityRule` | Rule checking that scenario claims have evidence and provenance. |
| `psq:EvidenceKnowledgeEntity` | Evidence knowledge entity | `psq:DomainEntity` | Entity that describes sources, datasets, evidence bundles, and provenance. |
| `psq:EvidencePack` | Evidence pack | `psq:EvidenceKnowledgeEntity` | Ontology class representing Evidence pack in the PersonaShield domain model. |
| `psq:GeneralPersonaRole` | General persona role | `psq:PersonaRole` | Intermediate role category used when a more specific organizational function is not supplied. |
| `psq:GeneratedScenario` | Generated scenario | `psq:ScenarioKnowledgeEntity` | A candidate or stored scenario created by the scenario engine and checked against ontology constraints. |
| `psq:IntroductoryDifficultyBand` | Introductory scenario difficulty | `psq:DifficultyBand` | Leaf difficulty class for explicit cues, lower ambiguity, high guidance, and foundational decisions. Maps to engine code easy. |
| `psq:LearnerKnowledgeEntity` | Learner knowledge entity | `psq:DomainEntity` | Entity that describes a learner, learner state, adaptation constraint, role, age band, stage, or retrieval context. |
| `psq:LearnerProfile` | Learner profile | `psq:LearnerKnowledgeEntity` | Ontology class representing Learner profile in the PersonaShield domain model. |
| `psq:LearnerStateSnapshot` | Learner state snapshot | `psq:LearnerKnowledgeEntity` | Ontology class representing Learner state snapshot in the PersonaShield domain model. |
| `psq:LearningStage` | Learning stage | `psq:LearnerKnowledgeEntity` | Exact or grouped position in the engine's nine-stage learning progression. |
| `psq:LegalConsequence` | Legal consequence | `psq:ScenarioCharacteristic` | Consequence or reporting implication associated with a scenario's action or attack structure. |
| `psq:LegitimateScenarioVariant` | Legitimate scenario variant | `psq:ScenarioVariant` | Variant representing a legitimate comparison communication. |
| `psq:MacroStage` | Macro learning stage | `psq:LearnerKnowledgeEntity` | Broad learner-proficiency dimension with the controlled values beginner, intermediate, and expert. |
| `psq:MaliciousScenarioVariant` | Malicious scenario variant | `psq:ScenarioVariant` | Variant representing a simulated malicious or fraudulent communication. |
| `psq:MessageBasedAttackType` | Message-based attack type | `psq:SocialEngineeringAttackType` | Social-engineering attack delivered primarily through written digital messages. |
| `psq:MicroStage` | Micro learning stage | `psq:LearnerKnowledgeEntity` | Within-level progression dimension with the controlled values introductory, developing, and advanced. |
| `psq:MiddleEngineAgeGroup` | Middle engine age-group category | `psq:AgeGroup` | Intermediate grouping for the engine's 36-59 age bands; it is an adaptation category, not a claim about ability. |
| `psq:MoodContext` | Mood context placeholder | `psq:LearnerKnowledgeEntity` | Optional runtime mood context. v9 records the placeholder but does not implement emotion inference. |
| `psq:NonAttackCommunicationType` | Non-attack communication type | `psq:AttackType` | Classification for a legitimate communication that is included for discrimination practice. |
| `psq:OlderEngineAgeGroup` | Older engine age-group category | `psq:AgeGroup` | Intermediate grouping for the engine's 60-90 age band; it is an adaptation category, not a claim about ability. |
| `psq:PerformanceState` | Performance state | `psq:LearnerKnowledgeEntity` | Runtime state summarizing learner performance for scenario selection. |
| `psq:PersonaFitConstraint` | Persona fit constraint | `psq:ContentQualityRule` | Rule checking whether generated content fits the learner profile and role. |
| `psq:PersonaRole` | Persona role | `psq:LearnerKnowledgeEntity` | Organizational work-context category used to select terminology and plausible tasks. |
| `psq:PersuasionCue` | Persuasion cue | `psq:ScenarioKnowledgeEntity` | Ontology class representing Persuasion cue in the PersonaShield domain model. |
| `psq:ProvenanceRecord` | Provenance record | `prov:Entity`, `psq:EvidenceKnowledgeEntity` | Ontology class representing Provenance record in the PersonaShield domain model. |
| `psq:RedFlag` | Red flag | `psq:ScenarioKnowledgeEntity` | Ontology class representing Red flag in the PersonaShield domain model. |
| `psq:RequiredConceptCoverageRule` | Required concept coverage rule | `psq:ContentQualityRule` | Rule requiring a scenario to include mandatory concepts for the selected template. |
| `psq:RetrievalMode` | Retrieval mode | `psq:LearnerKnowledgeEntity` | Ontology class representing Retrieval mode in the PersonaShield domain model. |
| `psq:SMSChatChannel` | SMS or chat channel | `psq:TextBasedChannel` | Leaf class for short-message or chat communication. |
| `psq:SafeIndicator` | Safe indicator | `psq:ScenarioKnowledgeEntity` | Ontology class representing Safe indicator in the PersonaShield domain model. |
| `psq:SafeResponseAction` | Safe response action | `psq:ScenarioKnowledgeEntity` | Ontology class representing Safe response action in the PersonaShield domain model. |
| `psq:SafetyConstraint` | Safety constraint | `psq:ContentQualityRule` | Rule rejecting unsafe instructions, harmful guidance, or contradictory safe responses. |
| `psq:ScenarioCharacteristic` | Scenario characteristic | `psq:ScenarioKnowledgeEntity` | Controlled characteristic used to classify or constrain a scenario template. |
| `psq:ScenarioKnowledgeEntity` | Scenario knowledge entity | `psq:DomainEntity` | Entity that describes scenario content, communication form, attack semantics, or safe response. |
| `psq:ScenarioQualityScore` | Scenario quality score | `psq:ContentQualityKnowledgeEntity` | Quality-score resource associated with a generated scenario candidate. |
| `psq:ScenarioStep` | Scenario step | `psq:ScenarioKnowledgeEntity` | A step or decision unit inside a scenario candidate or template. |
| `psq:ScenarioTemplate` | Scenario template | `psq:ScenarioKnowledgeEntity` | A reusable scenario control object whose relationships constrain one generated game-content slot. |
| `psq:ScenarioVariant` | Scenario variant | `psq:ScenarioCharacteristic` | Controlled distinction between simulated malicious and legitimate comparison content. |
| `psq:SemanticPacket` | Semantic packet | `psq:ScenarioKnowledgeEntity` | Selected ontology subgraph supplied to RAG and LLM scenario generation. |
| `psq:SocialEngineeringAttackType` | Social-engineering attack type | `psq:AttackType` | Attack classification that manipulates a person through a communication channel. |
| `psq:SourceArtifact` | Source artifact | `prov:Entity`, `psq:EvidenceKnowledgeEntity` | Ontology class representing Source artifact in the PersonaShield domain model. |
| `psq:TechnicalPersonaRole` | Technical persona role | `psq:PersonaRole` | Intermediate role category for learners whose primary work context is technical operations. |
| `psq:TextBasedChannel` | Text-based communication channel | `psq:Channel` | Communication channel in which the learner receives written or typed content. |
| `psq:TheorySource` | Theory source | `psq:SourceArtifact` | Ontology class representing Theory source in the PersonaShield domain model. |
| `psq:ThreatAction` | Threat action | `psq:ScenarioKnowledgeEntity` | Ontology class representing Threat action in the PersonaShield domain model. |
| `psq:TransitionConstraintProfile` | Transition constraint profile | `psq:LearnerKnowledgeEntity` | Ontology class representing Transition constraint profile in the PersonaShield domain model. |
| `psq:ValidationDecision` | Validation decision | `psq:ContentQualityKnowledgeEntity` | Accept, reject, or review decision for a generated scenario candidate. |
| `psq:VoiceBasedAttackType` | Voice-based attack type | `psq:SocialEngineeringAttackType` | Social-engineering attack delivered primarily through spoken communication. |
| `psq:VoiceBasedChannel` | Voice-based communication channel | `psq:Channel` | Communication channel in which spoken interaction is primary. |
| `psq:VoiceCallChannel` | Voice-call channel | `psq:VoiceBasedChannel` | Leaf class for telephone or voice-call communication. |
| `psq:YoungerEngineAgeGroup` | Younger engine age-group category | `psq:AgeGroup` | Intermediate grouping for the engine's 15-35 age bands; it is an adaptation category, not a claim about universal life stages. |

## Object properties (49)

| Property | Label | Declared domain | Declared range | Purpose |
| --- | --- | --- | --- | --- |
| `psq:atLearningStage` | at learning stage | `psq:LearnerStateSnapshot` | `psq:LearningStage` | Object property 'at learning stage' relating Learner state snapshot to Learning stage. |
| `psq:basedOnTemplate` | based on template | — | — | Links a generated scenario to the scenario template that controls it. |
| `psq:containsStep` | contains step | — | — | Links a scenario template or generated scenario to a scenario step. |
| `psq:derivedFromDataset` | derived from dataset | `psq:EvidencePack` | `psq:Dataset` | Object property 'derived from dataset' relating Evidence pack to Dataset. |
| `psq:evaluatesRule` | evaluates rule | — | — | Links a validation decision to the quality rule it evaluates. |
| `psq:hasAgeGroup` | has age group | `psq:LearnerProfile` | `psq:AgeGroup` | Object property 'has age group' relating Learner profile to Age group. |
| `psq:hasConstraintProfile` | has transition constraint profile | `psq:LearnerStateSnapshot` | `psq:TransitionConstraintProfile` | Object property 'has transition constraint profile' relating Learner state snapshot to Transition constraint profile. |
| `psq:hasCurrentState` | has current state | `psq:LearnerProfile` | `psq:LearnerStateSnapshot` | Object property 'has current state' relating Learner profile to Learner state snapshot. |
| `psq:hasDifficultyBand` | has difficulty band | `psq:DomainEntity` | `psq:DifficultyBand` | Object property 'has difficulty band' relating a permitted domain entity to Scenario difficulty band. |
| `psq:hasErrorType` | has error type | — | — | Links a constraint violation to its controlled error category. |
| `psq:hasEvidencePack` | has evidence pack | `psq:ScenarioTemplate` | `psq:EvidencePack` | Object property 'has evidence pack' relating Scenario template to Evidence pack. |
| `psq:hasLegalConsequence` | has legal consequence | — | — | Links a scenario template or response to a legal or organizational consequence. |
| `psq:hasMacroStage` | has macro stage | `psq:LearningStage` | `psq:MacroStage` | Links an exact engine learning-stage value to its broad proficiency value. |
| `psq:hasMicroStage` | has micro stage | `psq:LearningStage` | `psq:MicroStage` | Links an exact engine learning-stage value to its within-level progression value. |
| `psq:hasMoodContext` | has mood context | — | — | Links a learner profile to an optional mood-context placeholder. |
| `psq:hasPerformanceState` | has performance state | — | — | Links a learner profile to its runtime performance state. |
| `psq:hasPersonaRole` | has persona role | `psq:LearnerProfile` | `psq:PersonaRole` | Object property 'has persona role' relating Learner profile to Persona role. |
| `psq:hasProvenanceRecord` | has provenance record | `psq:ScenarioTemplate` | `psq:ProvenanceRecord` | Object property 'has provenance record' relating Scenario template to Provenance record. |
| `psq:hasQualityRule` | has quality rule | — | — | Links a template, candidate, or semantic packet to an applicable content-quality rule. |
| `psq:hasRedFlag` | has red flag | `psq:ScenarioTemplate` | `psq:RedFlag` | Object property 'has red flag' relating Scenario template to Red flag. |
| `psq:hasSafeIndicator` | has safe indicator | `psq:ScenarioTemplate` | `psq:SafeIndicator` | Object property 'has safe indicator' relating Scenario template to Safe indicator. |
| `psq:hasSafeResponse` | has safe response | `psq:ScenarioTemplate` | `psq:SafeResponseAction` | Object property 'has safe response' relating Scenario template to Safe response action. |
| `psq:hasScenarioQualityScore` | has scenario quality score | — | — | Links a generated scenario to its scenario-quality score resource. |
| `psq:hasThreatAction` | has threat action | `psq:ScenarioTemplate` | `psq:ThreatAction` | Object property 'has threat action' relating Scenario template to Threat action. |
| `psq:hasValidationDecision` | has validation decision | — | — | Links a generated scenario to its acceptance, rejection, or review decision. |
| `psq:hasVariant` | has variant | `psq:ScenarioTemplate` | `psq:ScenarioVariant` | Object property 'has variant' relating Scenario template to Scenario variant. |
| `psq:implementsTechnique` | implements ATT&CK technique | `psq:ScenarioTemplate` | `psq:ATTACKTechnique` | Object property 'implements ATT&CK technique' relating Scenario template to MITRE ATT&CK technique. |
| `psq:justifiesAttackClassification` | justifies attack classification | `psq:EvidencePack` | `psq:AttackType` | Object property 'justifies attack classification' relating Evidence pack to Attack type. |
| `psq:justifiesRedFlag` | justifies red flag | `psq:EvidencePack` | `psq:RedFlag` | Object property 'justifies red flag' relating Evidence pack to Red flag. |
| `psq:justifiesSafeIndicator` | justifies safe indicator | `psq:EvidencePack` | `psq:SafeIndicator` | Object property 'justifies safe indicator' relating Evidence pack to Safe indicator. |
| `psq:mapsToCAPEC` | maps to CAPEC pattern | `psq:ScenarioTemplate` | `psq:CAPECPattern` | Object property 'maps to CAPEC pattern' relating Scenario template to CAPEC pattern. |
| `psq:permitsAttackType` | permits attack type | `psq:TransitionConstraintProfile` | `psq:AttackType` | Object property 'permits attack type' relating Transition constraint profile to Attack type. |
| `psq:permitsChannel` | permits channel | `psq:TransitionConstraintProfile` | `psq:Channel` | Object property 'permits channel' relating Transition constraint profile to Channel. |
| `psq:permitsDifficultyBand` | permits difficulty band | `psq:TransitionConstraintProfile` | `psq:DifficultyBand` | Object property 'permits difficulty band' relating Transition constraint profile to Scenario difficulty band. |
| `psq:permitsVariant` | permits variant | `psq:TransitionConstraintProfile` | `psq:ScenarioVariant` | Object property 'permits variant' relating Transition constraint profile to Scenario variant. |
| `psq:recommendsSafeResponse` | recommends safe response | `psq:EvidencePack` | `psq:SafeResponseAction` | Object property 'recommends safe response' relating Evidence pack to Safe response action. |
| `psq:representsAttackType` | represents attack type | `psq:ScenarioTemplate` | `psq:AttackType` | Object property 'represents attack type' relating Scenario template to Attack type. |
| `psq:requiresChannel` | requires channel | — | — | Declares the required channel for template or candidate validation. |
| `psq:suitableForAgeGroup` | suitable for age group | `psq:ScenarioTemplate` | `psq:AgeGroup` | Object property 'suitable for age group' relating Scenario template to Age group. |
| `psq:suitableForRole` | suitable for role | `psq:ScenarioTemplate` | `psq:PersonaRole` | Object property 'suitable for role' relating Scenario template to Persona role. |
| `psq:suitableForStage` | suitable for stage | `psq:ScenarioTemplate` | `psq:LearningStage` | Object property 'suitable for stage' relating Scenario template to Learning stage. |
| `psq:supportedByEvidence` | supported by evidence | — | — | Links a scenario element or validation decision to an evidence pack. |
| `psq:supportedBySource` | supported by source | `psq:EvidencePack` | `psq:SourceArtifact` | Object property 'supported by source' relating Evidence pack to Source artifact. |
| `psq:targetsLearnerProfile` | targets learner profile | — | — | Links a scenario or semantic packet to the learner profile it targets. |
| `psq:targetsLearningStage` | targets learning stage | `psq:TransitionConstraintProfile` | `psq:LearningStage` | Object property 'targets learning stage' relating Transition constraint profile to Learning stage. |
| `psq:usesChannel` | uses channel | `psq:ScenarioTemplate` | `psq:Channel` | Object property 'uses channel' relating Scenario template to Channel. |
| `psq:usesPersuasionCue` | uses persuasion cue | `psq:ScenarioTemplate` | `psq:PersuasionCue` | Object property 'uses persuasion cue' relating Scenario template to Persuasion cue. |
| `psq:usesRetrievalMode` | uses retrieval mode | `psq:DomainEntity` | `psq:RetrievalMode` | Object property 'uses retrieval mode' relating a permitted domain entity to Retrieval mode. |
| `psq:violatesConstraint` | violates constraint | — | — | Links a generated scenario to a detected constraint violation. |

## Datatype properties (39)

| Property | Label | Declared domain | Declared range | Purpose |
| --- | --- | --- | --- | --- |
| `psq:acceptanceThreshold` | acceptance threshold | — | — | Threshold associated with a content-quality rule. |
| `psq:citationText` | citation text | `psq:SourceArtifact` | `xsd:string` | Datatype property 'citation text' recording a literal value for Source artifact. |
| `psq:confidenceScore` | confidence score | — | — | Decimal confidence score for a validation decision or quality score. |
| `psq:difficultyOrder` | difficulty order | `psq:DifficultyBand` | `xsd:positiveInteger` | Ordinal position of a scenario difficulty value: 1 introductory, 2 developing, 3 advanced. |
| `psq:difficultyValue` | difficulty value | — | — | Numerical or controlled difficulty value used for scenario-control scoring. |
| `psq:doi` | digital object identifier | `psq:SourceArtifact` | `xsd:string` | Datatype property 'digital object identifier' recording a literal value for Source artifact. |
| `psq:engineCode` | engine code | `psq:DomainEntity` | `xsd:string` | Literal required by the unchanged scenario engine for a controlled ontology value. |
| `psq:errorType` | error type literal | — | — | Literal form of an error category for export and logs. |
| `psq:evidenceCategory` | evidence category | `psq:SourceArtifact` | `xsd:string` | Controlled category describing how a source is used, such as standard, taxonomy, peer-reviewed theory, or empirical dataset. |
| `psq:expectedPerformanceEvidence` | expected performance evidence | — | `xsd:string` | Observable evidence used to determine whether the learner achieved the objective. |
| `psq:explanationText` | explanation text | — | — | Human-readable explanation for a rule, score, violation, or decision. |
| `psq:hintPolicyCode` | hint policy code | `psq:LearningStage` | `xsd:string` | Datatype property 'hint policy code' recording a literal value for Learning stage. |
| `psq:interactionPattern` | interaction pattern | `psq:LearningStage` | `xsd:string` | Datatype property 'interaction pattern' recording a literal value for Learning stage. |
| `psq:languageCode` | language code | `psq:ScenarioTemplate` | `xsd:language` | Datatype property 'language code' recording a literal value for Scenario template. |
| `psq:licenseStatus` | license status | `psq:SourceArtifact` | `xsd:string` | Operational statement describing whether redistribution is allowed, restricted, or requires review. |
| `psq:maximumAge` | maximum age | `psq:AgeGroup` | `xsd:nonNegativeInteger` | Inclusive upper age boundary for an engine age-band value. |
| `psq:minimumAge` | minimum age | `psq:AgeGroup` | `xsd:nonNegativeInteger` | Inclusive lower age boundary for an engine age-band value. |
| `psq:observableAction` | observable learner action | — | `xsd:string` | — |
| `psq:pressureLevelCode` | pressure level code | `psq:LearningStage` | `xsd:string` | Datatype property 'pressure level code' recording a literal value for Learning stage. |
| `psq:qualityRuleCategory` | quality rule category | — | — | Controlled category of a scenario-quality rule. |
| `psq:qualityScore` | quality score | — | — | Decimal score assigned to a generated scenario candidate. |
| `psq:redFlagsVisibleCode` | red flags visible code | `psq:LearningStage` | `xsd:string` | Datatype property 'red flags visible code' recording a literal value for Learning stage. |
| `psq:requiredForAcceptance` | required for acceptance | — | — | Boolean marker indicating that a rule is required for scenario acceptance. |
| `psq:retrievalDate` | retrieval date | `psq:SourceArtifact` | `xsd:date` | Date on which source metadata or the referenced source location was checked for this ontology release. |
| `psq:scenarioID` | scenario ID | — | — | v9 alias for engine scenario identifier terminology. |
| `psq:scenarioId` | scenario identifier | `psq:ScenarioTemplate` | `xsd:string` | Datatype property 'scenario identifier' recording a literal value for Scenario template. |
| `psq:scenarioTask` | scenario task | — | `xsd:string` | — |
| `psq:scenarioTitle` | scenario title | `psq:ScenarioTemplate` | `xsd:string` | Datatype property 'scenario title' recording a literal value for Scenario template. |
| `psq:sourceFile` | source file | `psq:ProvenanceRecord` | `xsd:string` | Datatype property 'source file' recording a literal value for Provenance record. |
| `psq:sourceRecordId` | source record identifier | `psq:ProvenanceRecord` | `xsd:string` | Datatype property 'source record identifier' recording a literal value for Provenance record. |
| `psq:sourceURL` | source URL | — | — | v9 alias matching reviewer document terminology; sourceUrl remains retained for compatibility. |
| `psq:sourceUrl` | source URL | `psq:SourceArtifact` | `xsd:anyURI` | Datatype property 'source URL' recording a literal value for Source artifact. |
| `psq:stageId` | stage identifier | `psq:LearningStage` | `xsd:string` | Datatype property 'stage identifier' recording a literal value for Learning stage. |
| `psq:stageIndex` | stage index | `psq:LearningStage` | `xsd:integer` | Datatype property 'stage index' recording a literal value for Learning stage. |
| `psq:statementText` | statement text | `psq:DomainEntity` | `xsd:string` | Datatype property 'statement text' recording a literal value for an ontology entity. |
| `psq:validationStatus` | validation status | — | — | Status assigned by the validation process. |
| `psq:verificationStatus` | verification status | `psq:SourceArtifact` | `xsd:string` | Current review status of source identity, content role, or metadata. |
| `psq:violationCode` | violation code | — | — | Machine-readable code for a detected constraint violation. |
| `psq:vocabularyBand` | vocabulary band | `psq:LearningStage` | `xsd:string` | Datatype property 'vocabulary band' recording a literal value for Learning stage. |

## Named individuals (133)

| Identifier | Label | Declared classes |
| --- | --- | --- |
| `psq:Action_ContinueApprovedWorkflow` | Continue through the approved workflow after verification | `psq:SafeResponseAction` |
| `psq:Action_DoNotClickOrReply` | Do not click or reply; verify independently | `psq:SafeResponseAction` |
| `psq:Action_EndCallAndVerify` | End the call and verify independently | `psq:SafeResponseAction` |
| `psq:Action_PauseAndVerify` | Pause and verify independently | `psq:SafeResponseAction` |
| `psq:Age_15_21` | Ages 15-21 | `psq:Age15To21Group` |
| `psq:Age_22_35` | Ages 22-35 | `psq:Age22To35Group` |
| `psq:Age_36_45` | Ages 36-45 | `psq:Age36To45Group` |
| `psq:Age_46_59` | Ages 46-59 | `psq:Age46To59Group` |
| `psq:Age_60_90` | Ages 60-90 | `psq:Age60To90Group` |
| `psq:BEGINNER_ADVANCED` | Beginner Advanced | `psq:LearningStage` |
| `psq:BEGINNER_DEVELOPING` | Beginner Developing | `psq:LearningStage` |
| `psq:BEGINNER_INTRODUCTORY` | Beginner Introductory | `psq:LearningStage` |
| `psq:CAPEC_164` | Mobile Phishing | `psq:CAPECPattern` |
| `psq:CAPEC_98` | Phishing | `psq:CAPECPattern` |
| `psq:Cue_Authority` | Authority | `psq:PersuasionCue` |
| `psq:Cue_Curiosity` | Curiosity | `psq:PersuasionCue` |
| `psq:Cue_Fear` | Fear | `psq:PersuasionCue` |
| `psq:Cue_Reciprocity` | Reciprocity | `psq:PersuasionCue` |
| `psq:Cue_Scarcity` | Scarcity | `psq:PersuasionCue` |
| `psq:Cue_SocialProof` | Social proof | `psq:PersuasionCue` |
| `psq:Cue_Urgency` | Urgency | `psq:PersuasionCue` |
| `psq:DS_AFNC` | Thailand Anti-Fake News Center open data | `psq:Dataset` |
| `psq:DS_CAPEC_XML` | CAPEC XML snapshot | `psq:Dataset` |
| `psq:DS_IRSCallTranscript` | IRS phone-scam transcript | `psq:Dataset` |
| `psq:DS_KnowledgeBaseJSONL` | PersonaShield normalized JSONL knowledge base | `psq:Dataset` |
| `psq:DS_MITRE_STIX_18_1` | MITRE ATT&CK Enterprise STIX 18.1 | `psq:Dataset` |
| `psq:DS_ThaiFraudSMS` | Thai fraud SMS collection | `psq:Dataset` |
| `psq:Decision_Accept` | Accept generated scenario | `psq:ValidationDecision` |
| `psq:Decision_Reject` | Reject generated scenario | `psq:ValidationDecision` |
| `psq:Decision_Review` | Review generated scenario | `psq:ValidationDecision` |
| `psq:Difficulty_Advanced` | Advanced difficulty | `psq:AdvancedDifficultyBand` |
| `psq:Difficulty_Developing` | Developing difficulty | `psq:DevelopingDifficultyBand` |
| `psq:Difficulty_Introductory` | Introductory difficulty | `psq:IntroductoryDifficultyBand` |
| `psq:ENGLISH_GLOBAL` | ENGLISH_GLOBAL | `psq:RetrievalMode` |
| `psq:EXPERT_ADVANCED` | Expert Advanced | `psq:LearningStage` |
| `psq:EXPERT_DEVELOPING` | Expert Developing | `psq:LearningStage` |
| `psq:EXPERT_INTRODUCTORY` | Expert Introductory | `psq:LearningStage` |
| `psq:Email` | Email | `psq:EmailChannel` |
| `psq:Error_ChannelMismatch` | Channel mismatch | `psq:ErrorType` |
| `psq:Evidence_Email_InvoiceChange_Developing` | Evidence for developing email invoice-change scenario | `psq:EvidencePack` |
| `psq:Evidence_Email_Legitimate_Developing` | Evidence for developing legitimate email scenario | `psq:EvidencePack` |
| `psq:Evidence_SMS_BankLink_Introductory` | Evidence for introductory SMS bank-link scenario | `psq:EvidencePack` |
| `psq:Evidence_SMS_Legitimate_Introductory` | Evidence for introductory legitimate SMS scenario | `psq:EvidencePack` |
| `psq:Evidence_Voice_ITSupport_Advanced` | Evidence for advanced voice IT-support scenario | `psq:EvidencePack` |
| `psq:Evidence_Voice_Legitimate_Advanced` | Evidence for advanced legitimate voice scenario | `psq:EvidencePack` |
| `psq:FakeVariant` | Fake scenario | `psq:MaliciousScenarioVariant` |
| `psq:Generated_SMS_BankLink_Candidate_v9` | Generated SMS bank-link candidate v9 | `psq:GeneratedScenario` |
| `psq:HYBRID_COMPARE` | HYBRID_COMPARE | `psq:RetrievalMode` |
| `psq:INTERMEDIATE_ADVANCED` | Intermediate Advanced | `psq:LearningStage` |
| `psq:INTERMEDIATE_DEVELOPING` | Intermediate Developing | `psq:LearningStage` |
| `psq:INTERMEDIATE_INTRODUCTORY` | Intermediate Introductory | `psq:LearningStage` |
| `psq:Learner_HR_Beginner` | Representative beginner HR learner | `psq:LearnerProfile` |
| `psq:LegalConsequence_ReportToITOrSecurity` | Report to IT or security | `psq:LegalConsequence` |
| `psq:LegitimateCommunication` | Legitimate communication | `psq:NonAttackCommunicationType` |
| `psq:Macro_Beginner` | Beginner macro stage | `psq:MacroStage` |
| `psq:Macro_Expert` | Expert macro stage | `psq:MacroStage` |
| `psq:Macro_Intermediate` | Intermediate macro stage | `psq:MacroStage` |
| `psq:Micro_Advanced` | Advanced micro stage | `psq:MicroStage` |
| `psq:Micro_Developing` | Developing micro stage | `psq:MicroStage` |
| `psq:Micro_Introductory` | Introductory micro stage | `psq:MicroStage` |
| `psq:Mood_NotModeledNeutral` | Mood context not modeled - neutral placeholder | `psq:MoodContext` |
| `psq:PROV_TPL_Email_InvoiceChange_Developing` | Provenance for developing email invoice-change scenario | `psq:ProvenanceRecord` |
| `psq:PROV_TPL_Email_Legitimate_Developing` | Provenance for developing legitimate email scenario | `psq:ProvenanceRecord` |
| `psq:PROV_TPL_SMS_BankLink_Introductory` | Provenance for introductory SMS bank-link scenario | `psq:ProvenanceRecord` |
| `psq:PROV_TPL_SMS_Legitimate_Introductory` | Provenance for introductory legitimate SMS scenario | `psq:ProvenanceRecord` |
| `psq:PROV_TPL_Voice_ITSupport_Advanced` | Provenance for advanced voice IT-support scenario | `psq:ProvenanceRecord` |
| `psq:PROV_TPL_Voice_Legitimate_Advanced` | Provenance for advanced legitimate voice scenario | `psq:ProvenanceRecord` |
| `psq:Performance_Stable` | Stable performance | `psq:PerformanceState` |
| `psq:Phishing` | Phishing | `psq:MessageBasedAttackType` |
| `psq:RF_CredentialRequest` | Credential request | `psq:RedFlag` |
| `psq:RF_OTPRequest` | One-time-password request | `psq:RedFlag` |
| `psq:RF_RemoteAccessRequest` | Remote-access request | `psq:RedFlag` |
| `psq:RF_SenderMismatch` | Sender or domain mismatch | `psq:RedFlag` |
| `psq:RF_SuspiciousLink` | Suspicious link | `psq:RedFlag` |
| `psq:RF_UnexpectedAttachment` | Unexpected attachment | `psq:RedFlag` |
| `psq:RF_UnusualPayment` | Unusual payment request | `psq:RedFlag` |
| `psq:RF_UnverifiedCaller` | Unverified caller | `psq:RedFlag` |
| `psq:RF_UrgencyPressure` | Urgency or time pressure | `psq:RedFlag` |
| `psq:RF_WorkflowBypass` | Request to bypass normal workflow | `psq:RedFlag` |
| `psq:RealVariant` | Real scenario | `psq:LegitimateScenarioVariant` |
| `psq:Role_FINANCE` | FINANCE | `psq:BusinessPersonaRole` |
| `psq:Role_HR` | HR | `psq:BusinessPersonaRole` |
| `psq:Role_IT` | IT | `psq:TechnicalPersonaRole` |
| `psq:Role_MANAGEMENT` | MANAGEMENT | `psq:BusinessPersonaRole` |
| `psq:Role_OTHER` | OTHER | `psq:GeneralPersonaRole` |
| `psq:Rule_ChannelConsistency` | Rule ChannelConsistency | `psq:ConsistencyConstraint` |
| `psq:Rule_EvidenceRequirement` | Rule EvidenceRequirement | `psq:EvidenceCoverageConstraint` |
| `psq:Rule_LegitimateScenarioSeparation` | Rule LegitimateScenarioSeparation | `psq:ConsistencyConstraint` |
| `psq:Rule_PersonaFit` | Rule PersonaFit | `psq:PersonaFitConstraint` |
| `psq:Rule_QualityAcceptance` | Rule QualityAcceptance | `psq:ContentQualityRule` |
| `psq:Rule_QualityRejection` | Rule QualityRejection | `psq:SafetyConstraint` |
| `psq:Rule_RequiredAttackStructure` | Rule RequiredAttackStructure | `psq:RequiredConceptCoverageRule` |
| `psq:Rule_TemplateEligibility` | Rule TemplateEligibility | `psq:ContentQualityRule` |
| `psq:SI_ExpectedWorkflow` | Expected workflow | `psq:SafeIndicator` |
| `psq:SI_IndependentVerification` | Independent verification is available | `psq:SafeIndicator` |
| `psq:SI_KnownSender` | Known sender | `psq:SafeIndicator` |
| `psq:SMSChat` | SMS or chat | `psq:SMSChatChannel` |
| `psq:Score_SMS_BankLink_Candidate` | SMS bank-link candidate score | `psq:ScenarioQualityScore` |
| `psq:SemanticPacket_SMS_BankLink_v9` | SMS bank-link semantic packet v9 | `psq:SemanticPacket` |
| `psq:Smishing` | Smishing | `psq:MessageBasedAttackType` |
| `psq:Source_CAPEC_164` | MITRE CAPEC-164 Mobile Phishing | `psq:SourceArtifact` |
| `psq:Source_HAISQ2014` | Determining employee awareness using HAIS-Q | `psq:TheorySource` |
| `psq:Source_KnowledgeGraphs2021` | Knowledge Graphs | `psq:SourceArtifact` |
| `psq:Source_MITRE_T1566` | MITRE ATT&CK T1566 Phishing | `psq:SourceArtifact` |
| `psq:Source_MITRE_T1566_004` | MITRE ATT&CK T1566.004 Spearphishing Voice | `psq:SourceArtifact` |
| `psq:Source_Ontology101` | Ontology Development 101 | `psq:SourceArtifact` |
| `psq:Source_PROVO` | PROV-O: The PROV Ontology | `psq:SourceArtifact` |
| `psq:Source_PhishingGameFramework2013` | A game design framework for avoiding phishing attacks | `psq:TheorySource` |
| `psq:Source_PhishingMindfulness2017` | Training to mitigate phishing attacks using mindfulness techniques | `psq:TheorySource` |
| `psq:Source_PhishingVulnerability2011` | Why do people get phished? | `psq:TheorySource` |
| `psq:Source_RAG2020` | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | `psq:SourceArtifact` |
| `psq:Source_SeriousGamesMeta2013` | A meta-analysis of the cognitive and motivational effects of serious games | `psq:TheorySource` |
| `psq:State_HR_BeginnerIntroductory` | HR learner at beginner introductory stage | `psq:LearnerStateSnapshot` |
| `psq:T1566` | Phishing | `psq:ATTACKTechnique` |
| `psq:T1566_001` | Spearphishing Attachment | `psq:ATTACKTechnique` |
| `psq:T1566_002` | Spearphishing Link | `psq:ATTACKTechnique` |
| `psq:T1566_003` | Spearphishing via Service | `psq:ATTACKTechnique` |
| `psq:T1566_004` | Spearphishing Voice | `psq:ATTACKTechnique` |
| `psq:TA_CredentialHarvesting` | Credential harvesting | `psq:ThreatAction` |
| `psq:TA_PaymentDiversion` | Payment diversion | `psq:ThreatAction` |
| `psq:TA_RemoteAccess` | Remote-access request | `psq:ThreatAction` |
| `psq:TA_WorkflowBypass` | Workflow bypass | `psq:ThreatAction` |
| `psq:THAI_LOCAL` | THAI_LOCAL | `psq:RetrievalMode` |
| `psq:TPL_Email_InvoiceChange_Developing` | Vendor bank detail change | `psq:ScenarioTemplate` |
| `psq:TPL_Email_Legitimate_Developing` | Expected approval-workflow notification | `psq:ScenarioTemplate` |
| `psq:TPL_SMS_BankLink_Introductory` | Urgent bank verification link | `psq:ScenarioTemplate` |
| `psq:TPL_SMS_Legitimate_Introductory` | Expected internal reminder | `psq:ScenarioTemplate` |
| `psq:TPL_Voice_ITSupport_Advanced` | False IT support remote-access call | `psq:ScenarioTemplate` |
| `psq:TPL_Voice_Legitimate_Advanced` | Verified high-priority service call | `psq:ScenarioTemplate` |
| `psq:Transition_BeginnerIntro_to_BeginnerDeveloping_SMS` | Advance to beginner developing with paired SMS scenarios | `psq:TransitionConstraintProfile` |
| `psq:Violation_ChannelMismatch` | Channel mismatch violation | `psq:ConstraintViolation` |
| `psq:Vishing` | Vishing | `psq:VoiceBasedAttackType` |
| `psq:VoiceCall` | Voice call | `psq:VoiceCallChannel` |

## Evidence sources and datasets (18)

URLs and verification statuses below are the ontology's metadata. A citation is not a claim
that the referenced work was ingested as a corpus or cleared for redistribution.

| ID | Title | Evidence role | Recorded publisher | Recorded URL | Status |
| --- | --- | --- | --- | --- | --- |
| `psq:DS_AFNC` | Thailand Anti-Fake News Center open data | official_local_reference_dataset | Thailand Anti-Fake News Center | — | metadata_and_role_verified |
| `psq:DS_CAPEC_XML` | CAPEC XML snapshot | authoritative_pattern_snapshot | MITRE Corporation | — | metadata_and_role_verified |
| `psq:DS_IRSCallTranscript` | IRS phone-scam transcript | external_empirical_transcript | — | — | identity_checked_license_and_redistribution_pending |
| `psq:DS_KnowledgeBaseJSONL` | PersonaShield normalized JSONL knowledge base | derived_runtime_dataset | PersonaShield Quest research project | — | metadata_and_role_verified |
| `psq:DS_MITRE_STIX_18_1` | MITRE ATT&CK Enterprise STIX 18.1 | authoritative_taxonomy_snapshot | MITRE Corporation | — | metadata_and_role_verified |
| `psq:DS_ThaiFraudSMS` | Thai fraud SMS collection | local_empirical_dataset | PersonaShield Quest local research collection | — | identity_checked_license_and_redistribution_pending |
| `psq:Source_CAPEC_164` | MITRE CAPEC-164 Mobile Phishing | authoritative_attack_pattern | MITRE Corporation | https://capec.mitre.org/data/definitions/164.html | metadata_and_role_verified |
| `psq:Source_HAISQ2014` | Determining employee awareness using HAIS-Q | peer_reviewed_awareness_measurement | Elsevier | https://doi.org/10.1016/j.cose.2013.12.003 | metadata_and_role_verified |
| `psq:Source_KnowledgeGraphs2021` | Knowledge Graphs | peer_reviewed_knowledge_graph_research | Association for Computing Machinery | https://doi.org/10.1145/3447772 | metadata_and_role_verified |
| `psq:Source_MITRE_T1566` | MITRE ATT&CK T1566 Phishing | authoritative_attack_taxonomy | MITRE Corporation | https://attack.mitre.org/techniques/T1566/ | metadata_and_role_verified |
| `psq:Source_MITRE_T1566_004` | MITRE ATT&CK T1566.004 Spearphishing Voice | authoritative_attack_taxonomy | MITRE Corporation | https://attack.mitre.org/techniques/T1566/004/ | metadata_and_role_verified |
| `psq:Source_Ontology101` | Ontology Development 101 | ontology_engineering_method | Stanford Knowledge Systems Laboratory | https://protege.stanford.edu/publications/ontology_development/ontology101.pdf | metadata_and_role_verified |
| `psq:Source_PROVO` | PROV-O: The PROV Ontology | formal_provenance_standard | World Wide Web Consortium | https://www.w3.org/TR/prov-o/ | metadata_and_role_verified |
| `psq:Source_PhishingGameFramework2013` | A game design framework for avoiding phishing attacks | peer_reviewed_game_design | Elsevier | https://doi.org/10.1016/j.chb.2012.12.018 | metadata_and_role_verified |
| `psq:Source_PhishingMindfulness2017` | Training to mitigate phishing attacks using mindfulness techniques | peer_reviewed_phishing_training | Taylor and Francis | https://doi.org/10.1080/07421222.2017.1334499 | metadata_and_role_verified |
| `psq:Source_PhishingVulnerability2011` | Why do people get phished? | peer_reviewed_human_factors | Elsevier | https://doi.org/10.1016/j.dss.2011.03.002 | metadata_and_role_verified |
| `psq:Source_RAG2020` | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | peer_reviewed_rag_research | Neural Information Processing Systems Foundation | https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html | metadata_and_role_verified |
| `psq:Source_SeriousGamesMeta2013` | A meta-analysis of the cognitive and motivational effects of serious games | peer_reviewed_meta_analysis | American Psychological Association | https://doi.org/10.1037/a0031311 | metadata_and_role_verified |
