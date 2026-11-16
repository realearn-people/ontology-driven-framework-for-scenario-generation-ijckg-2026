# PSQ-SCO Detailed Validation Metrics and CQ Query Results

Generated: 2026-07-01T04:57:45
Ontology: `ontology/ontology/personashield-psq-sco-v9.1.owl`
Version: `9.1.0`

## Executive Result

- Overall release validation: **PASS**
- HermiT consistency: **True**
- Unsatisfiable classes: **0**
- Bounded KG completeness: **4362 / 4362** checks passed; ratio **1.0**
- SPARQL ASK validation: **8 / 8** PASS
- SELECT rows: **CQ1=2; CQ2=13; CQ3=8; CQ4=12**

## All Numeric Metrics

| Metric | Value |
| --- | --- |
| OWL/RDF classes | 73 |
| Object properties | 49 |
| Data properties | 39 |
| Annotation properties | 17 |
| Individuals | 133 |
| Triple count | 3229 |
| Runtime records | 12425 |
| Runtime files | 20 |
| SPARQL load ms | 398.267 |
| HermiT duration seconds | 3.636 |
| HermiT command return code | 0 |
| Unsatisfiable class count | 0 |
| Required KG checks | 4362 |
| Passed KG checks | 4362 |
| Completeness ratio | 1 |
| Template count | 6 |
| Quality-control required rule count | 8 |
| Generated scenario count | 1 |
| Evidence pack count | 6 |
| Source count | 6 |
| Dataset count | 2 |
| Provenance record count | 6 |
| Graph nodes | 311 |
| Graph edges | 3164 |
| Dangling local references | 0 |
| Removed-scope forbidden term count | 25 |
| Removed-scope literal hits | 0 |
| Removed-scope graph hits | 0 |
| Malformed OWL restrictions | 0 |
| Release errors | 0 |
| Release warnings | 0 |

## Coverage by CQ

| CQ | Passed | Total | Coverage |
| --- | --- | --- | --- |
| CQ1 | 72 | 72 | 1 |
| CQ2 | 30 | 30 | 1 |
| CQ3 | 6 | 6 | 1 |
| CQ4 | 12 | 12 | 1 |

## Template Balance

### Variant counts

| Value | Count |
| --- | --- |
| FakeVariant | 3 |
| RealVariant | 3 |

### Channel counts

| Value | Count |
| --- | --- |
| Email | 2 |
| SMSChat | 2 |
| VoiceCall | 2 |

### Difficulty counts

| Value | Count |
| --- | --- |
| Difficulty_Advanced | 2 |
| Difficulty_Developing | 2 |
| Difficulty_Introductory | 2 |

## CQ SELECT Query Metrics

| CQ | Name | Query file | Parameters | Rows | Execution ms | Variables |
| --- | --- | --- | --- | --- | --- | --- |
| CQ1 | Scenario Selection | queries/v9_1/cq1-select-templates.rq | {"learner": "Learner_HR_Beginner", "template": null} | 2 | 884.896 | learner, performanceState, moodContext, currentStage, targetStage, template, templateTitle, channel, variant, attackType, difficulty, role, ageGroup, retrievalMode |
| CQ2 | Cybersecurity Structure | queries/v9_1/cq2-cybersecurity-structure.rq | {"learner": null, "template": "TPL_SMS_BankLink_Introductory"} | 13 | 116.299 | template, category, concept, conceptLabel |
| CQ3 | Content Quality Control | queries/v9_1/cq3-content-quality-control.rq | {"learner": null, "template": "TPL_SMS_BankLink_Introductory"} | 8 | 57.507 | template, rule, ruleLabel, category, threshold, required, ruleText, candidate, decision, qualityScore, confidenceScore, violation |
| CQ4 | Evidence and Provenance Grounding | queries/v9_1/cq4-evidence-provenance.rq | {"learner": null, "template": "TPL_Voice_ITSupport_Advanced"} | 12 | 97.452 | template, evidencePack, evidenceRole, supportedElement, elementLabel, source, sourceTitle, publisher, sourceUrl, retrievalDate, evidenceCategory, verificationStatus, licenseStatus, dataset, datasetLabel, provenance, sourceFile, sourceRecordId |

## CQ1 - Scenario Selection Full Results

Query file: `queries/v9_1/cq1-select-templates.rq`
Execution ms: `884.896`
Row count: `2`

| learner | performanceState | moodContext | currentStage | targetStage | template | templateTitle | channel | variant | attackType | difficulty | role | ageGroup | retrievalMode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| psq:Learner_HR_Beginner | psq:Performance_Stable | psq:Mood_NotModeledNeutral | psq:BEGINNER_INTRODUCTORY | psq:BEGINNER_DEVELOPING | psq:TPL_SMS_BankLink_Introductory | Urgent bank verification link | psq:SMSChat | psq:FakeVariant | psq:Smishing | psq:Difficulty_Introductory | psq:Role_HR | psq:Age_22_35 | psq:ENGLISH_GLOBAL |
| psq:Learner_HR_Beginner | psq:Performance_Stable | psq:Mood_NotModeledNeutral | psq:BEGINNER_INTRODUCTORY | psq:BEGINNER_DEVELOPING | psq:TPL_SMS_Legitimate_Introductory | Expected internal reminder | psq:SMSChat | psq:RealVariant | psq:LegitimateCommunication | psq:Difficulty_Introductory | psq:Role_HR | psq:Age_22_35 | psq:ENGLISH_GLOBAL |

### SPARQL Query

```sparql
PREFIX psq: <http://personashield.ait.ac.th/ontology/psq-sco#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>

# CQ1 - Scenario Selection
SELECT DISTINCT ?learner ?performanceState ?moodContext ?currentStage ?targetStage ?template ?templateTitle ?channel ?variant ?attackType ?difficulty ?role ?ageGroup ?retrievalMode
WHERE {
  VALUES ?learner { psq:Learner_HR_Beginner }
  ?learner psq:hasCurrentState ?state ;
           psq:hasPersonaRole ?role ;
           psq:hasAgeGroup ?ageGroup ;
           psq:usesRetrievalMode ?retrievalMode .
  OPTIONAL { ?learner psq:hasPerformanceState ?performanceState }
  OPTIONAL { ?learner psq:hasMoodContext ?moodContext }
  ?state psq:atLearningStage ?currentStage ;
         psq:hasConstraintProfile ?transition .
  ?transition psq:targetsLearningStage ?targetStage ;
              psq:permitsDifficultyBand ?difficulty ;
              psq:permitsChannel ?channel ;
              psq:permitsVariant ?variant ;
              psq:permitsAttackType ?attackType .
  ?template rdf:type psq:ScenarioTemplate ;
            psq:suitableForStage ?targetStage ;
            psq:suitableForRole ?role ;
            psq:suitableForAgeGroup ?ageGroup ;
            psq:usesRetrievalMode ?retrievalMode ;
            psq:hasDifficultyBand ?difficulty ;
            psq:usesChannel ?channel ;
            psq:hasVariant ?variant ;
            psq:representsAttackType ?attackType .
  OPTIONAL { ?template psq:scenarioTitle ?templateTitle }
}
ORDER BY ?template
```

## CQ2 - Cybersecurity Structure Full Results

Query file: `queries/v9_1/cq2-cybersecurity-structure.rq`
Execution ms: `116.299`
Row count: `13`

| template | category | concept | conceptLabel |
| --- | --- | --- | --- |
| psq:TPL_SMS_BankLink_Introductory | attack_technique | psq:T1566_003 | Spearphishing via Service |
| psq:TPL_SMS_BankLink_Introductory | attack_type | psq:Smishing | Smishing |
| psq:TPL_SMS_BankLink_Introductory | capec_pattern | psq:CAPEC_164 | Mobile Phishing |
| psq:TPL_SMS_BankLink_Introductory | channel | psq:SMSChat | SMS or chat |
| psq:TPL_SMS_BankLink_Introductory | legal_consequence | psq:LegalConsequence_ReportToITOrSecurity | Report to IT or security |
| psq:TPL_SMS_BankLink_Introductory | persuasion_cue | psq:Cue_Fear | Fear |
| psq:TPL_SMS_BankLink_Introductory | persuasion_cue | psq:Cue_Urgency | Urgency |
| psq:TPL_SMS_BankLink_Introductory | red_flag | psq:RF_CredentialRequest | Credential request |
| psq:TPL_SMS_BankLink_Introductory | red_flag | psq:RF_SuspiciousLink | Suspicious link |
| psq:TPL_SMS_BankLink_Introductory | red_flag | psq:RF_UrgencyPressure | Urgency or time pressure |
| psq:TPL_SMS_BankLink_Introductory | safe_response | psq:Action_DoNotClickOrReply | Do not click or reply; verify independently |
| psq:TPL_SMS_BankLink_Introductory | threat_action | psq:TA_CredentialHarvesting | Credential harvesting |
| psq:TPL_SMS_BankLink_Introductory | variant | psq:FakeVariant | Fake scenario |

### SPARQL Query

```sparql
PREFIX psq: <http://personashield.ait.ac.th/ontology/psq-sco#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>

# CQ2 - Cybersecurity Structure
SELECT DISTINCT ?template ?category ?concept ?conceptLabel
WHERE {
  VALUES ?template { psq:TPL_SMS_BankLink_Introductory }
  {
    ?template psq:usesChannel ?concept . BIND("channel" AS ?category)
  } UNION {
    ?template psq:hasVariant ?concept . BIND("variant" AS ?category)
  } UNION {
    ?template psq:representsAttackType ?concept . BIND("attack_type" AS ?category)
  } UNION {
    ?template psq:hasThreatAction ?concept . BIND("threat_action" AS ?category)
  } UNION {
    ?template psq:hasRedFlag ?concept . BIND("red_flag" AS ?category)
  } UNION {
    ?template psq:hasSafeIndicator ?concept . BIND("safe_indicator" AS ?category)
  } UNION {
    ?template psq:usesPersuasionCue ?concept . BIND("persuasion_cue" AS ?category)
  } UNION {
    ?template psq:implementsTechnique ?concept . BIND("attack_technique" AS ?category)
  } UNION {
    ?template psq:mapsToCAPEC ?concept . BIND("capec_pattern" AS ?category)
  } UNION {
    ?template psq:hasSafeResponse ?concept . BIND("safe_response" AS ?category)
  } UNION {
    ?template psq:hasLegalConsequence ?concept . BIND("legal_consequence" AS ?category)
  }
  OPTIONAL { ?concept rdfs:label ?conceptLabel }
}
ORDER BY ?category ?concept
```

## CQ3 - Content Quality Control Full Results

Query file: `queries/v9_1/cq3-content-quality-control.rq`
Execution ms: `57.507`
Row count: `8`

| template | rule | ruleLabel | category | threshold | required | ruleText | candidate | decision | qualityScore | confidenceScore | violation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| psq:TPL_SMS_BankLink_Introductory | psq:Rule_ChannelConsistency | Rule ChannelConsistency | channel_consistency | 1.0 | true | GeneratedScenario(s) based on template t must use the channel required by t. | psq:Generated_SMS_BankLink_Candidate_v9 | psq:Decision_Review | 0.92 | 0.88 |  |
| psq:TPL_SMS_BankLink_Introductory | psq:Rule_EvidenceRequirement | Rule EvidenceRequirement | evidence_requirement | 1.0 | true | AcceptableScenario(s) requires verified supporting evidence. | psq:Generated_SMS_BankLink_Candidate_v9 | psq:Decision_Review | 0.92 | 0.88 |  |
| psq:TPL_SMS_BankLink_Introductory | psq:Rule_LegitimateScenarioSeparation | Rule LegitimateScenarioSeparation | legitimate_scenario_separation | 1.0 | true | LegitimateScenario(s) must not import malicious attack technique or red flags and must include safe indicators. | psq:Generated_SMS_BankLink_Candidate_v9 | psq:Decision_Review | 0.92 | 0.88 |  |
| psq:TPL_SMS_BankLink_Introductory | psq:Rule_PersonaFit | Rule PersonaFit | persona_fit | 1.0 | true | GeneratedScenario(s) must fit the learner profile targeted by the selected template. | psq:Generated_SMS_BankLink_Candidate_v9 | psq:Decision_Review | 0.92 | 0.88 |  |
| psq:TPL_SMS_BankLink_Introductory | psq:Rule_QualityAcceptance | Rule QualityAcceptance | quality_acceptance | 0.80 | true | GeneratedScenario(s) with sufficient constraint coverage, evidence coverage, and zero violations may be accepted. | psq:Generated_SMS_BankLink_Candidate_v9 | psq:Decision_Review | 0.92 | 0.88 |  |
| psq:TPL_SMS_BankLink_Introductory | psq:Rule_QualityRejection | Rule QualityRejection | quality_rejection | 1.0 | true | GeneratedScenario(s) with missing required concepts, contradiction, or unsafe instruction must be rejected. | psq:Generated_SMS_BankLink_Candidate_v9 | psq:Decision_Review | 0.92 | 0.88 |  |
| psq:TPL_SMS_BankLink_Introductory | psq:Rule_RequiredAttackStructure | Rule RequiredAttackStructure | required_attack_structure | 1.0 | true | AttackScenario(s) and basedOnTemplate(s,t) -> requires attack type, channel, red flag, and safe response. | psq:Generated_SMS_BankLink_Candidate_v9 | psq:Decision_Review | 0.92 | 0.88 |  |
| psq:TPL_SMS_BankLink_Introductory | psq:Rule_TemplateEligibility | Rule TemplateEligibility | template_eligibility | 1.0 | true | LearnerProfile(l) and ScenarioTemplate(t) and compatibleRole(t,l) and compatibleStage(t,l) and compatibleChannel(t,l) -> EligibleTemplate(t,l). | psq:Generated_SMS_BankLink_Candidate_v9 | psq:Decision_Review | 0.92 | 0.88 |  |

### SPARQL Query

```sparql
PREFIX psq: <http://personashield.ait.ac.th/ontology/psq-sco#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>

# CQ3 - Content Quality Control
SELECT DISTINCT ?template ?rule ?ruleLabel ?category ?threshold ?required ?ruleText ?candidate ?decision ?qualityScore ?confidenceScore ?violation
WHERE {
  VALUES ?template { psq:TPL_SMS_BankLink_Introductory }
  ?template psq:hasQualityRule ?rule .
  OPTIONAL { ?rule rdfs:label ?ruleLabel }
  OPTIONAL { ?rule psq:qualityRuleCategory ?category }
  OPTIONAL { ?rule psq:acceptanceThreshold ?threshold }
  OPTIONAL { ?rule psq:requiredForAcceptance ?required }
  OPTIONAL { ?rule psq:ruleText ?ruleText }
  OPTIONAL {
    ?candidate psq:basedOnTemplate ?template ;
               psq:hasValidationDecision ?decision ;
               psq:hasScenarioQualityScore ?score .
    OPTIONAL { ?score psq:qualityScore ?qualityScore }
    OPTIONAL { ?score psq:confidenceScore ?confidenceScore }
    OPTIONAL { ?candidate psq:violatesConstraint ?violation }
  }
}
ORDER BY ?category ?rule
```

## CQ4 - Evidence and Provenance Grounding Full Results

Query file: `queries/v9_1/cq4-evidence-provenance.rq`
Execution ms: `97.452`
Row count: `12`

| template | evidencePack | evidenceRole | supportedElement | elementLabel | source | sourceTitle | publisher | sourceUrl | retrievalDate | evidenceCategory | verificationStatus | licenseStatus | dataset | datasetLabel | provenance | sourceFile | sourceRecordId |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | attack_classification | psq:Vishing | Vishing | psq:Source_CAPEC_164 | MITRE CAPEC-164 Mobile Phishing | MITRE Corporation | https://capec.mitre.org/data/definitions/164.html | 2026-06-22 | authoritative_attack_pattern | metadata_and_role_verified | public_reference_check_terms_before_redistribution | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | attack_classification | psq:Vishing | Vishing | psq:Source_MITRE_T1566_004 | MITRE ATT&CK T1566.004 Spearphishing Voice | MITRE Corporation | https://attack.mitre.org/techniques/T1566/004/ | 2026-06-22 | authoritative_attack_taxonomy | metadata_and_role_verified | public_reference_check_terms_before_redistribution | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | attack_classification | psq:Vishing | Vishing | psq:Source_PhishingMindfulness2017 | Training to mitigate phishing attacks using mindfulness techniques | Taylor and Francis | https://doi.org/10.1080/07421222.2017.1334499 | 2026-06-22 | peer_reviewed_phishing_training | metadata_and_role_verified | bibliographic_reference_only_or_license_review_required | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | recommended_response | psq:Action_EndCallAndVerify | End the call and verify independently | psq:Source_CAPEC_164 | MITRE CAPEC-164 Mobile Phishing | MITRE Corporation | https://capec.mitre.org/data/definitions/164.html | 2026-06-22 | authoritative_attack_pattern | metadata_and_role_verified | public_reference_check_terms_before_redistribution | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | recommended_response | psq:Action_EndCallAndVerify | End the call and verify independently | psq:Source_MITRE_T1566_004 | MITRE ATT&CK T1566.004 Spearphishing Voice | MITRE Corporation | https://attack.mitre.org/techniques/T1566/004/ | 2026-06-22 | authoritative_attack_taxonomy | metadata_and_role_verified | public_reference_check_terms_before_redistribution | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | recommended_response | psq:Action_EndCallAndVerify | End the call and verify independently | psq:Source_PhishingMindfulness2017 | Training to mitigate phishing attacks using mindfulness techniques | Taylor and Francis | https://doi.org/10.1080/07421222.2017.1334499 | 2026-06-22 | peer_reviewed_phishing_training | metadata_and_role_verified | bibliographic_reference_only_or_license_review_required | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | red_flag | psq:RF_RemoteAccessRequest | Remote-access request | psq:Source_CAPEC_164 | MITRE CAPEC-164 Mobile Phishing | MITRE Corporation | https://capec.mitre.org/data/definitions/164.html | 2026-06-22 | authoritative_attack_pattern | metadata_and_role_verified | public_reference_check_terms_before_redistribution | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | red_flag | psq:RF_RemoteAccessRequest | Remote-access request | psq:Source_MITRE_T1566_004 | MITRE ATT&CK T1566.004 Spearphishing Voice | MITRE Corporation | https://attack.mitre.org/techniques/T1566/004/ | 2026-06-22 | authoritative_attack_taxonomy | metadata_and_role_verified | public_reference_check_terms_before_redistribution | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | red_flag | psq:RF_RemoteAccessRequest | Remote-access request | psq:Source_PhishingMindfulness2017 | Training to mitigate phishing attacks using mindfulness techniques | Taylor and Francis | https://doi.org/10.1080/07421222.2017.1334499 | 2026-06-22 | peer_reviewed_phishing_training | metadata_and_role_verified | bibliographic_reference_only_or_license_review_required | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | red_flag | psq:RF_UnverifiedCaller | Unverified caller | psq:Source_CAPEC_164 | MITRE CAPEC-164 Mobile Phishing | MITRE Corporation | https://capec.mitre.org/data/definitions/164.html | 2026-06-22 | authoritative_attack_pattern | metadata_and_role_verified | public_reference_check_terms_before_redistribution | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | red_flag | psq:RF_UnverifiedCaller | Unverified caller | psq:Source_MITRE_T1566_004 | MITRE ATT&CK T1566.004 Spearphishing Voice | MITRE Corporation | https://attack.mitre.org/techniques/T1566/004/ | 2026-06-22 | authoritative_attack_taxonomy | metadata_and_role_verified | public_reference_check_terms_before_redistribution | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |
| psq:TPL_Voice_ITSupport_Advanced | psq:Evidence_Voice_ITSupport_Advanced | red_flag | psq:RF_UnverifiedCaller | Unverified caller | psq:Source_PhishingMindfulness2017 | Training to mitigate phishing attacks using mindfulness techniques | Taylor and Francis | https://doi.org/10.1080/07421222.2017.1334499 | 2026-06-22 | peer_reviewed_phishing_training | metadata_and_role_verified | bibliographic_reference_only_or_license_review_required | psq:DS_IRSCallTranscript | IRS phone-scam transcript | psq:PROV_TPL_Voice_ITSupport_Advanced | data/ontology_ready | TPL_VOICE_IT_SUPPORT_HARD |

### SPARQL Query

```sparql
PREFIX psq: <http://personashield.ait.ac.th/ontology/psq-sco#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>

# CQ4 - Evidence and Provenance Grounding
SELECT DISTINCT ?template ?evidencePack ?evidenceRole ?supportedElement ?elementLabel ?source ?sourceTitle ?publisher ?sourceUrl ?retrievalDate ?evidenceCategory ?verificationStatus ?licenseStatus ?dataset ?datasetLabel ?provenance ?sourceFile ?sourceRecordId
WHERE {
  VALUES ?template { psq:TPL_Voice_ITSupport_Advanced }
  ?template psq:hasEvidencePack ?evidencePack ;
            psq:hasProvenanceRecord ?provenance .
  ?evidencePack psq:supportedBySource ?source ;
                psq:derivedFromDataset ?dataset .
  {
    ?evidencePack psq:justifiesAttackClassification ?supportedElement . BIND("attack_classification" AS ?evidenceRole)
  } UNION {
    ?evidencePack psq:justifiesRedFlag ?supportedElement . BIND("red_flag" AS ?evidenceRole)
  } UNION {
    ?evidencePack psq:justifiesSafeIndicator ?supportedElement . BIND("safe_indicator" AS ?evidenceRole)
  } UNION {
    ?evidencePack psq:recommendsSafeResponse ?supportedElement . BIND("recommended_response" AS ?evidenceRole)
  }
  OPTIONAL { ?supportedElement rdfs:label ?elementLabel }
  OPTIONAL { ?source dcterms:title ?sourceTitle }
  OPTIONAL { ?source dcterms:publisher ?publisher }
  OPTIONAL { ?source psq:sourceUrl ?sourceUrl }
  OPTIONAL { ?source psq:retrievalDate ?retrievalDate }
  OPTIONAL { ?source psq:evidenceCategory ?evidenceCategory }
  OPTIONAL { ?source psq:verificationStatus ?verificationStatus }
  OPTIONAL { ?source psq:licenseStatus ?licenseStatus }
  OPTIONAL { ?dataset rdfs:label ?datasetLabel }
  OPTIONAL { ?provenance psq:sourceFile ?sourceFile }
  OPTIONAL { ?provenance psq:sourceRecordId ?sourceRecordId }
}
ORDER BY ?evidenceRole ?supportedElement ?source
```

## ASK Validation Cases

| Test ID | Query file | Expected | Actual | Passed | Execution ms |
| --- | --- | --- | --- | --- | --- |
| CQ1-NEG-001 | queries/v9_1/validation/CQ1-NEG-001.ask.rq | true | true | true | 853.139 |
| CQ1-POS-001 | queries/v9_1/validation/CQ1-POS-001.ask.rq | true | true | true | 10.650 |
| CQ2-NEG-001 | queries/v9_1/validation/CQ2-NEG-001.ask.rq | true | true | true | 10.599 |
| CQ2-POS-001 | queries/v9_1/validation/CQ2-POS-001.ask.rq | true | true | true | 7.551 |
| CQ3-NEG-001 | queries/v9_1/validation/CQ3-NEG-001.ask.rq | true | true | true | 9.041 |
| CQ3-POS-001 | queries/v9_1/validation/CQ3-POS-001.ask.rq | true | true | true | 15.193 |
| CQ4-NEG-001 | queries/v9_1/validation/CQ4-NEG-001.ask.rq | true | true | true | 12.241 |
| CQ4-POS-001 | queries/v9_1/validation/CQ4-POS-001.ask.rq | true | true | true | 13.139 |

## Interpretation

The ontology passed all configured checks for the bounded PSQ-SCO CQ1-CQ4 scenario-control scope. The result supports the claim that the ontology-based KG is complete for the declared competency questions and validated query patterns, while avoiding a universal completeness claim outside that scope.
