from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD


ROOT = Path(__file__).resolve().parents[1]

SOURCE_OWL = ROOT / "ontology" / "personashield-odcgct-v8.2-reviewed.owl"
SOURCE_RUNTIME = ROOT / "data" / "ontology_runtime_v8_2"
SOURCE_VOCAB = ROOT / "data" / "ontology_bindings" / "controlled-vocabulary-v8.2.json"
SOURCE_MAPPING = ROOT / "data" / "ontology_bindings" / "field-mapping-specification-v8.2.json"
SOURCE_PACKET = ROOT / "data" / "ontology_bindings" / "semantic-packet-schema-v8.2.json"

ONTOLOGY_OUT = ROOT / "ontology" / "personashield-psq-sco-v9.owl"
TXT_OUT = ROOT / "ontology" / "personashield-psq-sco-v9.txt"
QUERY_ROOT = ROOT / "queries" / "v9"
QUERY_VALIDATION_ROOT = QUERY_ROOT / "validation"
KG_ROOT = ROOT / "knowledge_graph" / "v9"
TEST_ROOT = ROOT / "data" / "ontology_tests" / "v9"
REPORT_ROOT = ROOT / "outputs" / "v9"
RUNTIME_ROOT = ROOT / "data" / "ontology_runtime_v9"
BINDING_ROOT = ROOT / "data" / "ontology_bindings"
DOCS_OUT = ROOT / "docs" / "PSQ_SCO_v9_REVIEWER_ALIGNED_CHANGE_LOG.md"

GRAPH_JSON = KG_ROOT / "personashield-psq-sco-v9-graph.json"
NODES_JSONL = KG_ROOT / "personashield-psq-sco-v9-nodes.jsonl"
EDGES_JSONL = KG_ROOT / "personashield-psq-sco-v9-edges.jsonl"
EDGES_CSV = KG_ROOT / "personashield-psq-sco-v9-edges.csv"
TTL_OUT = KG_ROOT / "personashield-psq-sco-v9-named-graph.ttl"
CLASS_TREE_OUT = KG_ROOT / "class-hierarchy.txt"
INSTANCE_CATALOG_OUT = KG_ROOT / "instance-catalog.csv"

VOCAB_OUT = BINDING_ROOT / "controlled-vocabulary-v9.json"
MAPPING_OUT = BINDING_ROOT / "field-mapping-specification-v9.json"
PACKET_SCHEMA_OUT = BINDING_ROOT / "semantic-packet-schema-v9.json"
CQ_TESTS_OUT = TEST_ROOT / "cq-test-cases.json"
RULE_REGISTER_OUT = TEST_ROOT / "scenario-control-rule-register.csv"

OLD_BASE = "http://personashield.ait.ac.th/ontology/odcgct#"
OLD_ONTOLOGY = "http://personashield.ait.ac.th/ontology/odcgct"
OLD_VERSION = "http://personashield.ait.ac.th/ontology/odcgct/8.2.0"
NEW_BASE = "http://personashield.ait.ac.th/ontology/psq-sco#"
NEW_ONTOLOGY = "http://personashield.ait.ac.th/ontology/psq-sco"
NEW_VERSION = "http://personashield.ait.ac.th/ontology/psq-sco/9.0.0"
PSQ = Namespace(NEW_BASE)
PROV = Namespace("http://www.w3.org/ns/prov#")

VERSION = "9.0.0"


def psq(name: str) -> URIRef:
    return URIRef(NEW_BASE + name)


def remap_uri(uri: URIRef) -> URIRef:
    text = str(uri)
    if text.startswith(OLD_BASE):
        return URIRef(NEW_BASE + text[len(OLD_BASE) :])
    if text == OLD_ONTOLOGY:
        return URIRef(NEW_ONTOLOGY)
    return uri


def remap_graph(source: Graph) -> Graph:
    target = Graph()
    for prefix, namespace in source.namespaces():
        if prefix == "psq":
            continue
        target.bind(prefix, namespace)
    target.bind("psq", Namespace(NEW_BASE))
    target.bind("skos", SKOS)
    target.bind("dcterms", DCTERMS)
    target.bind("prov", PROV)
    for subject, predicate, obj in source:
        s2 = remap_uri(subject) if isinstance(subject, URIRef) else subject
        p2 = remap_uri(predicate) if isinstance(predicate, URIRef) else predicate
        o2 = remap_uri(obj) if isinstance(obj, URIRef) else obj
        target.add((s2, p2, o2))
    return target


def add_literal(g: Graph, subject: URIRef, predicate: URIRef, value: str, *, lang: str | None = None, datatype=None):
    if lang:
        g.add((subject, predicate, Literal(value, lang=lang)))
    elif datatype:
        g.add((subject, predicate, Literal(value, datatype=datatype)))
    else:
        g.add((subject, predicate, Literal(value)))


def add_label_comment(g: Graph, subject: URIRef, label: str, comment: str):
    add_literal(g, subject, RDFS.label, label, lang="en")
    add_literal(g, subject, RDFS.comment, comment, lang="en")
    add_literal(g, subject, SKOS.definition, comment, lang="en")


def add_governance(g: Graph, subject: URIRef, method: str = "reviewer_aligned_manual_modeling_v9"):
    add_literal(g, subject, PSQ.creationMethod, method)
    add_literal(
        g,
        subject,
        PSQ.reviewStatus,
        "automated_release_validation_required; domain_expert_review_pending",
    )
    add_literal(
        g,
        subject,
        PSQ.sourceDocument,
        "external-assets/PSQ_SCO_Reviewer_Aligned_Revision_v9.docx",
    )


def add_annotation_property(g: Graph, name: str, label: str, comment: str):
    subject = psq(name)
    g.add((subject, RDF.type, OWL.AnnotationProperty))
    add_label_comment(g, subject, label, comment)
    add_governance(g, subject)
    return subject


def add_class(g: Graph, name: str, label: str, comment: str, parent: str):
    subject = psq(name)
    g.add((subject, RDF.type, OWL.Class))
    g.add((subject, RDFS.subClassOf, psq(parent)))
    add_label_comment(g, subject, label, comment)
    add_governance(g, subject)
    return subject


def add_object_property(
    g: Graph,
    name: str,
    label: str,
    comment: str,
    domain: str,
    range_name: str,
    *,
    functional: bool = False,
):
    subject = psq(name)
    g.add((subject, RDF.type, OWL.ObjectProperty))
    if functional:
        g.add((subject, RDF.type, OWL.FunctionalProperty))
    add_label_comment(g, subject, label, comment)
    add_literal(g, subject, PSQ.intendedDomain, domain)
    add_literal(g, subject, PSQ.intendedRange, range_name)
    add_governance(g, subject)
    return subject


def add_data_property(
    g: Graph,
    name: str,
    label: str,
    comment: str,
    domain: str,
    range_uri: URIRef,
    *,
    functional: bool = False,
):
    subject = psq(name)
    g.add((subject, RDF.type, OWL.DatatypeProperty))
    if functional:
        g.add((subject, RDF.type, OWL.FunctionalProperty))
    add_label_comment(g, subject, label, comment)
    add_literal(g, subject, PSQ.intendedDomain, domain)
    add_literal(g, subject, PSQ.intendedRange, str(range_uri))
    add_governance(g, subject)
    return subject


def add_individual(g: Graph, name: str, class_name: str, label: str, comment: str):
    subject = psq(name)
    g.add((subject, RDF.type, OWL.NamedIndividual))
    g.add((subject, RDF.type, psq(class_name)))
    add_label_comment(g, subject, label, comment)
    add_governance(g, subject)
    return subject


def clear_values(g: Graph, subject: URIRef, predicate: URIRef):
    for triple in list(g.triples((subject, predicate, None))):
        g.remove(triple)


def update_ontology_header(g: Graph):
    ontology = URIRef(NEW_ONTOLOGY)
    g.add((ontology, RDF.type, OWL.Ontology))
    for predicate in (
        RDFS.label,
        RDFS.comment,
        OWL.versionInfo,
        OWL.versionIRI,
        OWL.priorVersion,
        DCTERMS.title,
        PSQ.competencyQuestion,
    ):
        clear_values(g, ontology, predicate)
    add_literal(
        g,
        ontology,
        RDFS.label,
        "PersonaShield Quest Scenario Control Ontology (PSQ-SCO) v9.0.0",
        lang="en",
    )
    add_literal(
        g,
        ontology,
        DCTERMS.title,
        "PersonaShield Quest Scenario Control Ontology (PSQ-SCO)",
        lang="en",
    )
    add_literal(g, ontology, OWL.versionInfo, VERSION)
    g.add((ontology, OWL.versionIRI, URIRef(NEW_VERSION)))
    g.add((ontology, OWL.priorVersion, URIRef(OLD_VERSION)))
    add_literal(
        g,
        ontology,
        RDFS.comment,
        (
            "PSQ-SCO v9 is a reviewer-aligned scenario-control ontology derived "
            "from ODCGCT v8.2. It keeps the four-CQ structure but reframes CQ3 "
            "from broad pedagogical alignment to generated-content quality "
            "control, while retaining minimal pedagogical constraints as imported "
            "scenario-control requirements. It does not generate prose and does "
            "not claim implemented emotion modeling."
        ),
        lang="en",
    )
    add_literal(g, ontology, PSQ.frameworkName, "Ontology-Driven Emotion-Aware Adaptive Cybersecurity Training Framework (ODEACT)")
    add_literal(g, ontology, PSQ.scopeBoundary, "scenario_control_not_general_cybersecurity_not_full_pedagogical_ontology")
    for cq in (
        "CQ1 - Scenario Selection: Which ScenarioTemplate individuals satisfy learner profile, performance state, mood-context placeholder, target transition, channel, difficulty, attack type, and retrieval-mode constraints?",
        "CQ2 - Cybersecurity Structure: Which attack or legitimate-communication concepts are explicitly linked to a selected ScenarioTemplate?",
        "CQ3 - Content Quality Control: Which ontology constraints and quality rules must a generated candidate scenario satisfy before acceptance into the scenario pool?",
        "CQ4 - Evidence and Provenance Grounding: Which trusted sources and provenance records justify scenario structure, red flags, safe indicators, recommended response, and validation decision?",
    ):
        add_literal(g, ontology, PSQ.competencyQuestion, cq, lang="en")


def add_v9_schema(g: Graph):
    for name, label, comment in (
        ("frameworkName", "framework name", "Names the wider research framework that uses this ontology."),
        ("scopeBoundary", "scope boundary", "Records the boundary between ontology, engine, pedagogy, and evaluation scope."),
        ("sourceDocument", "source document", "Identifies the reviewer-aligned document that motivated the v9 element."),
        ("ruleText", "rule text", "Human-readable scenario-control rule text."),
        ("ruleLanguage", "rule language", "Rule notation or execution layer, such as OWL, SPARQL, SHACL-style validation, or first-order predicate."),
        ("competencyQuestionRole", "competency question role", "Explains how an entity supports a competency question."),
        ("intendedDomain", "intended domain", "Documentation-only expected subject class for a property; not asserted as an OWL domain axiom."),
        ("intendedRange", "intended range", "Documentation-only expected object or literal type for a property; not asserted as an OWL range axiom."),
    ):
        add_annotation_property(g, name, label, comment)

    classes = [
        ("ContentQualityKnowledgeEntity", "Content quality knowledge entity", "Scenario-control terms used to validate and score generated scenario candidates.", "DomainEntity"),
        ("GeneratedScenario", "Generated scenario", "A candidate or stored scenario created by the scenario engine and checked against ontology constraints.", "ScenarioKnowledgeEntity"),
        ("ScenarioStep", "Scenario step", "A step or decision unit inside a scenario candidate or template.", "ScenarioKnowledgeEntity"),
        ("SemanticPacket", "Semantic packet", "Selected ontology subgraph supplied to RAG and LLM scenario generation.", "ScenarioKnowledgeEntity"),
        ("PerformanceState", "Performance state", "Runtime state summarizing learner performance for scenario selection.", "LearnerKnowledgeEntity"),
        ("MoodContext", "Mood context placeholder", "Optional runtime mood context. v9 records the placeholder but does not implement emotion inference.", "LearnerKnowledgeEntity"),
        ("LegalConsequence", "Legal consequence", "Consequence or reporting implication associated with a scenario's action or attack structure.", "ScenarioCharacteristic"),
        ("PedagogicalConstraint", "Pedagogical constraint", "Minimal imported learning-design constraint used only for scenario control.", "PedagogicalKnowledgeEntity"),
        ("CognitiveProcess", "Cognitive process", "Cognitive process required by an imported pedagogical constraint.", "PedagogicalKnowledgeEntity"),
        ("DataObject", "Data object", "Scenario object manipulated by the learner, such as a link, credential request, caller claim, QR code, or attachment.", "PedagogicalKnowledgeEntity"),
        ("SupportStrategy", "Support strategy", "Instructional support strategy used as a scenario-control constraint.", "PedagogicalKnowledgeEntity"),
        ("EvidenceOfLearning", "Evidence of learning", "Observable evidence expected from learner action in a scenario task.", "PedagogicalKnowledgeEntity"),
        ("ContentQualityRule", "Content quality rule", "Acceptance or rejection rule applied to generated scenario candidates.", "ContentQualityKnowledgeEntity"),
        ("RequiredConceptCoverageRule", "Required concept coverage rule", "Rule requiring a scenario to include mandatory concepts for the selected template.", "ContentQualityRule"),
        ("ConsistencyConstraint", "Consistency constraint", "Rule checking channel, variant, persona, difficulty, and template consistency.", "ContentQualityRule"),
        ("PersonaFitConstraint", "Persona fit constraint", "Rule checking whether generated content fits the learner profile and role.", "ContentQualityRule"),
        ("EvidenceCoverageConstraint", "Evidence coverage constraint", "Rule checking that scenario claims have evidence and provenance.", "ContentQualityRule"),
        ("SafetyConstraint", "Safety constraint", "Rule rejecting unsafe instructions, harmful guidance, or contradictory safe responses.", "ContentQualityRule"),
        ("ScenarioQualityScore", "Scenario quality score", "Quality-score resource associated with a generated scenario candidate.", "ContentQualityKnowledgeEntity"),
        ("ValidationDecision", "Validation decision", "Accept, reject, or review decision for a generated scenario candidate.", "ContentQualityKnowledgeEntity"),
        ("ConstraintViolation", "Constraint violation", "Detected violation of a scenario-control rule.", "ContentQualityKnowledgeEntity"),
        ("ErrorType", "Error type", "Controlled error category used in scenario-control error analysis.", "ContentQualityKnowledgeEntity"),
    ]
    for item in classes:
        add_class(g, *item)

    object_properties = [
        ("targetsLearnerProfile", "targets learner profile", "Links a scenario or semantic packet to the learner profile it targets.", "DomainEntity", "LearnerProfile"),
        ("containsStep", "contains step", "Links a scenario template or generated scenario to a scenario step.", "DomainEntity", "ScenarioStep"),
        ("supportedByEvidence", "supported by evidence", "Links a scenario element or validation decision to an evidence pack.", "DomainEntity", "EvidencePack"),
        ("importsPedagogicalConstraint", "imports pedagogical constraint", "Links PSQ-SCO elements to minimal external pedagogical constraints.", "DomainEntity", "PedagogicalConstraint"),
        ("hasQualityRule", "has quality rule", "Links a template, candidate, or semantic packet to an applicable content-quality rule.", "DomainEntity", "ContentQualityRule"),
        ("violatesConstraint", "violates constraint", "Links a generated scenario to a detected constraint violation.", "GeneratedScenario", "ConstraintViolation"),
        ("hasValidationDecision", "has validation decision", "Links a generated scenario to its acceptance, rejection, or review decision.", "GeneratedScenario", "ValidationDecision", True),
        ("hasScenarioQualityScore", "has scenario quality score", "Links a generated scenario to its scenario-quality score resource.", "GeneratedScenario", "ScenarioQualityScore", True),
        ("basedOnTemplate", "based on template", "Links a generated scenario to the scenario template that controls it.", "GeneratedScenario", "ScenarioTemplate", True),
        ("requiresChannel", "requires channel", "Declares the required channel for template or candidate validation.", "DomainEntity", "Channel"),
        ("hasLegalConsequence", "has legal consequence", "Links a scenario template or response to a legal or organizational consequence.", "DomainEntity", "LegalConsequence"),
        ("hasErrorType", "has error type", "Links a constraint violation to its controlled error category.", "ConstraintViolation", "ErrorType"),
        ("evaluatesRule", "evaluates rule", "Links a validation decision to the quality rule it evaluates.", "ValidationDecision", "ContentQualityRule"),
        ("manipulatesDataObject", "manipulates data object", "Links a scenario task or pedagogical constraint to the data object manipulated by the learner.", "DomainEntity", "DataObject"),
        ("producesPerformanceEvidence", "produces performance evidence", "Links a scenario task to observable evidence of learning.", "DomainEntity", "EvidenceOfLearning"),
        ("requiresCognitiveProcess", "requires cognitive process", "Links a scenario task or pedagogical constraint to a cognitive process.", "DomainEntity", "CognitiveProcess"),
        ("hasPerformanceState", "has performance state", "Links a learner profile to its runtime performance state.", "LearnerProfile", "PerformanceState", True),
        ("hasMoodContext", "has mood context", "Links a learner profile to an optional mood-context placeholder.", "LearnerProfile", "MoodContext", True),
    ]
    for item in object_properties:
        add_object_property(g, *item[:-1], functional=item[-1]) if isinstance(item[-1], bool) else add_object_property(g, *item)

    data_properties = [
        ("scenarioID", "scenario ID", "v9 alias for engine scenario identifier terminology.", "DomainEntity", XSD.string),
        ("difficultyValue", "difficulty value", "Numerical or controlled difficulty value used for scenario-control scoring.", "DomainEntity", XSD.string),
        ("qualityScore", "quality score", "Decimal score assigned to a generated scenario candidate.", "ScenarioQualityScore", XSD.decimal),
        ("confidenceScore", "confidence score", "Decimal confidence score for a validation decision or quality score.", "DomainEntity", XSD.decimal),
        ("validationStatus", "validation status", "Status assigned by the validation process.", "DomainEntity", XSD.string),
        ("violationCode", "violation code", "Machine-readable code for a detected constraint violation.", "ConstraintViolation", XSD.string),
        ("errorType", "error type literal", "Literal form of an error category for export and logs.", "ConstraintViolation", XSD.string),
        ("explanationText", "explanation text", "Human-readable explanation for a rule, score, violation, or decision.", "DomainEntity", XSD.string),
        ("qualityRuleCategory", "quality rule category", "Controlled category of a scenario-quality rule.", "ContentQualityRule", XSD.string),
        ("acceptanceThreshold", "acceptance threshold", "Threshold associated with a content-quality rule.", "ContentQualityRule", XSD.decimal),
        ("requiredForAcceptance", "required for acceptance", "Boolean marker indicating that a rule is required for scenario acceptance.", "ContentQualityRule", XSD.boolean),
        ("sourceURL", "source URL", "v9 alias matching reviewer document terminology; sourceUrl remains retained for compatibility.", "SourceArtifact", XSD.anyURI),
    ]
    for item in data_properties:
        add_data_property(g, *item)


def add_v9_individuals_and_links(g: Graph):
    # Learner runtime placeholders.
    performance = add_individual(g, "Performance_Stable", "PerformanceState", "Stable performance", "Learner is stable enough for standard scenario progression.")
    mood = add_individual(g, "Mood_NotModeledNeutral", "MoodContext", "Mood context not modeled - neutral placeholder", "Placeholder used to keep the ODEACT framework boundary explicit without claiming implemented emotion inference.")
    learner = psq("Learner_HR_Beginner")
    g.add((learner, PSQ.hasPerformanceState, performance))
    g.add((learner, PSQ.hasMoodContext, mood))

    legal = add_individual(g, "LegalConsequence_ReportToITOrSecurity", "LegalConsequence", "Report to IT or security", "Organizational reporting consequence for suspicious social-engineering attempts.")
    data_link = add_individual(g, "DataObject_SuspiciousLink", "DataObject", "Suspicious link", "Learner-manipulated scenario object representing a suspicious link or URL.")
    evidence_learning = add_individual(g, "Evidence_SelectedIndicatorsAndSafeAction", "EvidenceOfLearning", "Selected indicators and safe action", "Observable learner evidence: correct indicators selected and safe action chosen.")
    cognitive = add_individual(g, "CognitiveProcess_DiscriminateAndJustify", "CognitiveProcess", "Discriminate and justify", "Cognitive process requiring the learner to distinguish fake from legitimate cues and justify the decision.")
    support = add_individual(g, "SupportStrategy_CuePromptThenExplanation", "SupportStrategy", "Cue prompt then explanation", "Support strategy that gives cue prompts before explanatory feedback.")
    ped_constraint = add_individual(g, "PedagogicalConstraint_MinimalScenarioControl", "PedagogicalConstraint", "Minimal scenario-control pedagogy import", "Minimal pedagogical constraint retained inside PSQ-SCO for scenario validation and scoring.")
    for target in (data_link, evidence_learning, cognitive, support):
        g.add((ped_constraint, PSQ.supportedByEvidence, psq("Evidence_SMS_BankLink_Introductory")))
    g.add((ped_constraint, PSQ.manipulatesDataObject, data_link))
    g.add((ped_constraint, PSQ.producesPerformanceEvidence, evidence_learning))
    g.add((ped_constraint, PSQ.requiresCognitiveProcess, cognitive))

    rule_defs = [
        ("Rule_TemplateEligibility", "ContentQualityRule", "template_eligibility", "LearnerProfile(l) and ScenarioTemplate(t) and compatibleRole(t,l) and compatibleStage(t,l) and compatibleChannel(t,l) -> EligibleTemplate(t,l).", "1.0"),
        ("Rule_RequiredAttackStructure", "RequiredConceptCoverageRule", "required_attack_structure", "AttackScenario(s) and basedOnTemplate(s,t) -> requires attack type, channel, red flag, and safe response.", "1.0"),
        ("Rule_LegitimateScenarioSeparation", "ConsistencyConstraint", "legitimate_scenario_separation", "LegitimateScenario(s) must not import malicious attack technique or red flags and must include safe indicators.", "1.0"),
        ("Rule_ChannelConsistency", "ConsistencyConstraint", "channel_consistency", "GeneratedScenario(s) based on template t must use the channel required by t.", "1.0"),
        ("Rule_PersonaFit", "PersonaFitConstraint", "persona_fit", "GeneratedScenario(s) must fit the learner profile targeted by the selected template.", "1.0"),
        ("Rule_EvidenceRequirement", "EvidenceCoverageConstraint", "evidence_requirement", "AcceptableScenario(s) requires verified supporting evidence.", "1.0"),
        ("Rule_QualityAcceptance", "ContentQualityRule", "quality_acceptance", "GeneratedScenario(s) with sufficient constraint coverage, evidence coverage, and zero violations may be accepted.", "0.80"),
        ("Rule_QualityRejection", "SafetyConstraint", "quality_rejection", "GeneratedScenario(s) with missing required concepts, contradiction, or unsafe instruction must be rejected.", "1.0"),
    ]
    rules = []
    for name, cls, category, text, threshold in rule_defs:
        rule = add_individual(g, name, cls, name.replace("_", " "), text)
        add_literal(g, rule, PSQ.qualityRuleCategory, category)
        add_literal(g, rule, PSQ.ruleText, text, lang="en")
        add_literal(g, rule, PSQ.ruleLanguage, "first_order_predicate_plus_sparql_validation")
        add_literal(g, rule, PSQ.acceptanceThreshold, threshold, datatype=XSD.decimal)
        add_literal(g, rule, PSQ.requiredForAcceptance, "true", datatype=XSD.boolean)
        rules.append(rule)

    accept = add_individual(g, "Decision_Accept", "ValidationDecision", "Accept generated scenario", "Decision indicating that a generated scenario satisfies required scenario-control constraints.")
    reject = add_individual(g, "Decision_Reject", "ValidationDecision", "Reject generated scenario", "Decision indicating that a generated scenario violates a blocking quality or safety constraint.")
    review = add_individual(g, "Decision_Review", "ValidationDecision", "Review generated scenario", "Decision indicating that a generated scenario needs human or expert review before use.")
    for decision in (accept, reject, review):
        for rule in rules:
            g.add((decision, PSQ.evaluatesRule, rule))

    score = add_individual(g, "Score_SMS_BankLink_Candidate", "ScenarioQualityScore", "SMS bank-link candidate score", "Demonstration score resource for CQ3 content-quality-control validation.")
    add_literal(g, score, PSQ.qualityScore, "0.92", datatype=XSD.decimal)
    add_literal(g, score, PSQ.confidenceScore, "0.88", datatype=XSD.decimal)
    add_literal(g, score, PSQ.validationStatus, "passes_automated_demo_rules")

    candidate = add_individual(g, "Generated_SMS_BankLink_Candidate_v9", "GeneratedScenario", "Generated SMS bank-link candidate v9", "Demonstration generated scenario candidate used to show PSQ-SCO content-quality-control checks.")
    g.add((candidate, PSQ.basedOnTemplate, psq("TPL_SMS_BankLink_Introductory")))
    g.add((candidate, PSQ.targetsLearnerProfile, learner))
    g.add((candidate, PSQ.usesChannel, psq("SMSChat")))
    g.add((candidate, PSQ.hasVariant, psq("FakeVariant")))
    g.add((candidate, PSQ.hasValidationDecision, review))
    g.add((candidate, PSQ.hasScenarioQualityScore, score))
    g.add((candidate, PSQ.supportedByEvidence, psq("Evidence_SMS_BankLink_Introductory")))
    add_literal(g, candidate, PSQ.explanationText, "Candidate satisfies the demonstration quality envelope but remains marked for expert review before live use.", lang="en")

    for template in sorted(g.subjects(RDF.type, psq("ScenarioTemplate"))):
        for rule in rules:
            g.add((template, PSQ.hasQualityRule, rule))
        g.add((template, PSQ.importsPedagogicalConstraint, ped_constraint))
        g.add((template, PSQ.hasLegalConsequence, legal))
        for channel in g.objects(template, PSQ.usesChannel):
            g.add((template, PSQ.requiresChannel, channel))
        for scenario_id in g.objects(template, PSQ.scenarioId):
            add_literal(g, template, PSQ.scenarioID, str(scenario_id))

    packet = add_individual(g, "SemanticPacket_SMS_BankLink_v9", "SemanticPacket", "SMS bank-link semantic packet v9", "Selected subgraph for ontology-guided RAG and LLM generation.")
    g.add((packet, PSQ.targetsLearnerProfile, learner))
    g.add((packet, PSQ.basedOnTemplate, psq("TPL_SMS_BankLink_Introductory")))
    g.add((packet, PSQ.supportedByEvidence, psq("Evidence_SMS_BankLink_Introductory")))
    for rule in rules:
        g.add((packet, PSQ.hasQualityRule, rule))

    violation = add_individual(g, "Violation_ChannelMismatch", "ConstraintViolation", "Channel mismatch violation", "Generated scenario uses a different channel than the selected template requires.")
    err = add_individual(g, "Error_ChannelMismatch", "ErrorType", "Channel mismatch", "Error category for channel/template contradiction.")
    g.add((violation, PSQ.hasErrorType, err))
    add_literal(g, violation, PSQ.violationCode, "ChannelMismatch")
    add_literal(g, violation, PSQ.errorType, "channel_mismatch")
    add_literal(g, violation, PSQ.explanationText, "Candidate channel does not match template channel.", lang="en")


def build_queries():
    QUERY_VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    prefix = f"PREFIX psq: <{NEW_BASE}>\nPREFIX rdf: <{RDF}>\nPREFIX rdfs: <{RDFS}>\nPREFIX dcterms: <{DCTERMS}>\nPREFIX prov: <{PROV}>\n\n"
    queries = {
        "cq1-select-templates.rq": prefix
        + """# CQ1 - Scenario Selection
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
""",
        "cq2-cybersecurity-structure.rq": prefix
        + """# CQ2 - Cybersecurity Structure
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
""",
        "cq3-content-quality-control.rq": prefix
        + """# CQ3 - Content Quality Control
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
""",
        "cq4-evidence-provenance.rq": prefix
        + """# CQ4 - Evidence and Provenance Grounding
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
""",
    }
    for name, text in queries.items():
        (QUERY_ROOT / name).write_text(text, encoding="utf-8")

    asks = {
        "CQ1-POS-001.ask.rq": prefix
        + """ASK {
  psq:Learner_HR_Beginner psq:hasPerformanceState psq:Performance_Stable ;
                           psq:hasMoodContext psq:Mood_NotModeledNeutral .
  psq:TPL_SMS_BankLink_Introductory rdf:type psq:ScenarioTemplate .
  psq:TPL_SMS_Legitimate_Introductory rdf:type psq:ScenarioTemplate .
}
""",
        "CQ1-NEG-001.ask.rq": prefix
        + """ASK {
  FILTER NOT EXISTS {
    ?template rdf:type psq:ScenarioTemplate ;
              psq:suitableForRole psq:Role_HR ;
              psq:suitableForAgeGroup psq:Age_22_35 ;
              psq:usesChannel psq:VoiceCall ;
              psq:hasVariant psq:FakeVariant ;
              psq:hasDifficultyBand psq:Difficulty_Introductory .
  }
}
""",
        "CQ2-POS-001.ask.rq": prefix
        + """ASK {
  psq:TPL_SMS_BankLink_Introductory psq:hasLegalConsequence psq:LegalConsequence_ReportToITOrSecurity ;
                                     psq:hasRedFlag psq:RF_SuspiciousLink ;
                                     psq:implementsTechnique psq:T1566_003 .
}
""",
        "CQ2-NEG-001.ask.rq": prefix
        + """ASK {
  FILTER NOT EXISTS {
    psq:TPL_SMS_Legitimate_Introductory psq:hasRedFlag|psq:hasThreatAction|psq:usesPersuasionCue|psq:implementsTechnique ?bad .
  }
}
""",
        "CQ3-POS-001.ask.rq": prefix
        + """ASK {
  psq:TPL_SMS_BankLink_Introductory psq:hasQualityRule psq:Rule_TemplateEligibility ;
                                     psq:hasQualityRule psq:Rule_RequiredAttackStructure ;
                                     psq:hasQualityRule psq:Rule_ChannelConsistency ;
                                     psq:hasQualityRule psq:Rule_PersonaFit ;
                                     psq:hasQualityRule psq:Rule_EvidenceRequirement ;
                                     psq:hasQualityRule psq:Rule_QualityAcceptance ;
                                     psq:hasQualityRule psq:Rule_QualityRejection .
  psq:Generated_SMS_BankLink_Candidate_v9 psq:basedOnTemplate psq:TPL_SMS_BankLink_Introductory ;
                                           psq:hasValidationDecision psq:Decision_Review ;
                                           psq:hasScenarioQualityScore psq:Score_SMS_BankLink_Candidate .
}
""",
        "CQ3-NEG-001.ask.rq": prefix
        + """ASK {
  FILTER NOT EXISTS {
    psq:Generated_SMS_BankLink_Candidate_v9 psq:violatesConstraint ?violation .
  }
}
""",
        "CQ4-POS-001.ask.rq": prefix
        + """ASK {
  psq:TPL_Voice_ITSupport_Advanced psq:hasEvidencePack ?pack .
  ?pack psq:supportedBySource ?source ;
        psq:justifiesAttackClassification psq:Vishing .
  ?source dcterms:title ?title ;
          psq:retrievalDate ?date ;
          psq:verificationStatus ?status ;
          psq:licenseStatus ?license .
}
""",
        "CQ4-NEG-001.ask.rq": prefix
        + """ASK {
  FILTER NOT EXISTS {
    psq:TPL_Voice_ITSupport_Advanced psq:hasEvidencePack ?pack .
    ?pack psq:supportedBySource psq:Source_RAG2020 .
  }
}
""",
    }
    for name, text in asks.items():
        (QUERY_VALIDATION_ROOT / name).write_text(text, encoding="utf-8")

    (QUERY_ROOT / "README.md").write_text(
        "# PSQ-SCO v9 SPARQL queries\n\n"
        "- CQ1: scenario selection\n"
        "- CQ2: cybersecurity structure\n"
        "- CQ3: content quality control\n"
        "- CQ4: evidence and provenance grounding\n\n"
        "Run with: `python scripts/run_sparql_cq_v9.py --cq all`.\n",
        encoding="utf-8",
    )


def serialize_node(value):
    text = str(value)
    if text.startswith(NEW_BASE):
        return text[len(NEW_BASE) :]
    return text


def build_graph_exports(g: Graph) -> dict[str, int]:
    KG_ROOT.mkdir(parents=True, exist_ok=True)
    local_subjects = {s for s in set(g.subjects()) if isinstance(s, URIRef) and str(s).startswith(NEW_BASE)}
    nodes = []
    for subject in sorted(local_subjects, key=str):
        kinds = []
        for obj in g.objects(subject, RDF.type):
            kinds.append(serialize_node(obj))
        label = next((str(o) for o in g.objects(subject, RDFS.label)), serialize_node(subject))
        nodes.append({"id": serialize_node(subject), "iri": str(subject), "label": label, "kinds": sorted(set(kinds))})

    edges = []
    for subject, predicate, obj in g:
        if isinstance(subject, URIRef) and str(subject).startswith(NEW_BASE):
            if isinstance(obj, URIRef):
                target = serialize_node(obj)
                target_type = "iri"
            else:
                target = str(obj)
                target_type = "literal"
            edges.append(
                {
                    "source": serialize_node(subject),
                    "predicate": serialize_node(predicate),
                    "target": target,
                    "target_type": target_type,
                }
            )
    edges.sort(key=lambda row: (row["source"], row["predicate"], row["target"]))

    GRAPH_JSON.write_text(json.dumps({"version": VERSION, "nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with NODES_JSONL.open("w", encoding="utf-8") as handle:
        for row in nodes:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with EDGES_JSONL.open("w", encoding="utf-8") as handle:
        for row in edges:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with EDGES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "predicate", "target", "target_type"])
        writer.writeheader()
        writer.writerows(edges)
    g.serialize(TTL_OUT, format="turtle")

    parent_edges = [(row["source"], row["target"]) for row in edges if row["predicate"].endswith("subClassOf") and row["target_type"] == "iri"]
    children: dict[str, list[str]] = {}
    for child, parent in parent_edges:
        children.setdefault(parent, []).append(child)
    lines = []
    def walk(node: str, depth: int = 0):
        lines.append("  " * depth + node)
        for child in sorted(children.get(node, [])):
            if child != node:
                walk(child, depth + 1)
    walk("DomainEntity")
    CLASS_TREE_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with INSTANCE_CATALOG_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["individual", "type", "label"])
        writer.writeheader()
        for subject in sorted(local_subjects, key=str):
            if (subject, RDF.type, OWL.NamedIndividual) in g:
                types = [serialize_node(o) for o in g.objects(subject, RDF.type) if o != OWL.NamedIndividual]
                label = next((str(o) for o in g.objects(subject, RDFS.label)), serialize_node(subject))
                for type_name in types:
                    writer.writerow({"individual": serialize_node(subject), "type": type_name, "label": label})
    return {"nodes": len(nodes), "edges": len(edges)}


def copy_runtime():
    if RUNTIME_ROOT.exists():
        shutil.rmtree(RUNTIME_ROOT)
    shutil.copytree(SOURCE_RUNTIME, RUNTIME_ROOT)
    records = 0
    files = 0
    for path in RUNTIME_ROOT.rglob("*.jsonl"):
        files += 1
        updated = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            record["ontology_version"] = VERSION
            record["mapping_version"] = VERSION
            record["scenario_control_ontology"] = "PSQ-SCO"
            record["semantic_control_profile"] = "scenario_control_quality_rules_v9"
            card = record.get("semantic_card") or ""
            addition = " PSQ-SCO v9 adds scenario-control quality rules, validation decisions, and semantic-packet scoring metadata."
            if "PSQ-SCO v9" not in card:
                record["semantic_card"] = (card + addition).strip()
            updated.append(json.dumps(record, ensure_ascii=False))
            records += 1
        path.write_text("\n".join(updated) + ("\n" if updated else ""), encoding="utf-8")
    return {"records": records, "files": files}


def build_binding_files():
    BINDING_ROOT.mkdir(parents=True, exist_ok=True)
    vocab = json.loads(SOURCE_VOCAB.read_text(encoding="utf-8"))
    vocab["version"] = VERSION
    vocab["ontology_name"] = "PersonaShield Quest Scenario Control Ontology (PSQ-SCO)"
    vocab["ontology_file"] = "ontology/personashield-psq-sco-v9.owl"
    vocab["namespace"] = NEW_BASE
    vocab["reviewer_aligned_v9_additions"] = {
        "content_quality_rules": [
            "template_eligibility",
            "required_attack_structure",
            "legitimate_scenario_separation",
            "channel_consistency",
            "persona_fit",
            "evidence_requirement",
            "quality_acceptance",
            "quality_rejection",
        ],
        "validation_decisions": ["accept", "reject", "review"],
        "runtime_placeholders": ["performance_state", "mood_context_placeholder"],
    }
    VOCAB_OUT.write_text(json.dumps(vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    mapping = json.loads(SOURCE_MAPPING.read_text(encoding="utf-8"))
    mapping["version"] = VERSION
    mapping["scope"] = "PSQ-SCO v9 JSON/engine-to-ontology mapping contract with scenario-control quality rules."
    mapping["ontology_file"] = "ontology/personashield-psq-sco-v9.owl"
    extra_fields = [
        {
            "engine_field": "performance_state",
            "ontology_property": "hasPerformanceState",
            "expected_type": "controlled string -> PerformanceState individual",
            "required": "optional in current engine; required for full ODEACT runtime",
            "validation_rule": "If present, must map to a known PerformanceState individual.",
            "legacy_aliases": [],
        },
        {
            "engine_field": "mood_context",
            "ontology_property": "hasMoodContext",
            "expected_type": "controlled string -> MoodContext individual",
            "required": "placeholder only in v9",
            "validation_rule": "Must not be used to claim implemented emotion inference unless a validated mood model is added.",
            "legacy_aliases": [],
        },
        {
            "engine_field": "quality_rules[]",
            "ontology_property": "hasQualityRule",
            "expected_type": "array of ContentQualityRule identifiers",
            "required": true_value(),
            "validation_rule": "Generated candidates must be checked against the active quality-rule set.",
            "legacy_aliases": [],
        },
        {
            "engine_field": "validation_decision",
            "ontology_property": "hasValidationDecision",
            "expected_type": "accept/reject/review -> ValidationDecision individual",
            "required": "required for generated scenario candidates",
            "validation_rule": "Decision must be supported by quality score, rule checks, and evidence/provenance status.",
            "legacy_aliases": [],
        },
        {
            "engine_field": "scenario_quality_score",
            "ontology_property": "hasScenarioQualityScore/qualityScore",
            "expected_type": "decimal score plus ScenarioQualityScore individual",
            "required": "required for generated scenario candidates",
            "validation_rule": "Score must be accompanied by confidenceScore and validationStatus.",
            "legacy_aliases": [],
        },
    ]
    existing = {field["engine_field"] for field in mapping.get("fields", [])}
    for field in extra_fields:
        if field["engine_field"] not in existing:
            mapping.setdefault("fields", []).append(field)
    MAPPING_OUT.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    packet = json.loads(SOURCE_PACKET.read_text(encoding="utf-8"))
    packet["$id"] = "https://personashield.ait.ac.th/schema/semantic-packet-v9.json"
    packet["title"] = "PersonaShield PSQ-SCO semantic control packet v9"
    packet["properties"]["quality_rules"] = {"type": "array", "items": {"type": "object"}}
    packet["properties"]["validation_decision"] = {"type": ["object", "null"]}
    packet["properties"]["quality_score"] = {"type": ["object", "null"]}
    packet["properties"]["error_analysis"] = {"type": "array", "items": {"type": "object"}}
    for field in ("quality_rules", "validation_decision", "quality_score", "error_analysis"):
        if field not in packet["required"]:
            packet["required"].append(field)
    PACKET_SCHEMA_OUT.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def true_value():
    return True


def build_test_artifacts():
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    cq_tests = {
        "version": VERSION,
        "tests": [
            {"id": "CQ1-POS-001", "cq": "CQ1", "type": "positive", "expected": "learner has performance and mood placeholders and selects SMS templates"},
            {"id": "CQ1-NEG-001", "cq": "CQ1", "type": "negative", "expected": "incompatible voice/HR/introductory template not found"},
            {"id": "CQ2-POS-001", "cq": "CQ2", "type": "positive", "expected": "bank-link template has legal consequence and attack structure"},
            {"id": "CQ2-NEG-001", "cq": "CQ2", "type": "negative", "expected": "legitimate SMS template has no malicious red flag or attack technique"},
            {"id": "CQ3-POS-001", "cq": "CQ3", "type": "positive", "expected": "bank-link template has all v9 quality rules and candidate decision"},
            {"id": "CQ3-NEG-001", "cq": "CQ3", "type": "negative", "expected": "demonstration candidate has no asserted violation"},
            {"id": "CQ4-POS-001", "cq": "CQ4", "type": "positive", "expected": "voice template has verified evidence and provenance"},
            {"id": "CQ4-NEG-001", "cq": "CQ4", "type": "negative", "expected": "unrelated RAG source is excluded from voice template evidence"},
        ],
    }
    CQ_TESTS_OUT.write_text(json.dumps(cq_tests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = [
        ("Rule_TemplateEligibility", "template_eligibility", "CQ1", "Select only compatible template envelopes."),
        ("Rule_RequiredAttackStructure", "required_attack_structure", "CQ2|CQ3", "Require selected attack concepts and safe response."),
        ("Rule_LegitimateScenarioSeparation", "legitimate_scenario_separation", "CQ2|CQ3", "Keep legitimate examples free of malicious red flags."),
        ("Rule_ChannelConsistency", "channel_consistency", "CQ1|CQ3", "Reject candidates whose channel conflicts with template."),
        ("Rule_PersonaFit", "persona_fit", "CQ1|CQ3", "Reject candidates that mismatch learner persona."),
        ("Rule_EvidenceRequirement", "evidence_requirement", "CQ4|CQ3", "Require verified evidence for accepted candidates."),
        ("Rule_QualityAcceptance", "quality_acceptance", "CQ3", "Accept only candidates meeting thresholds."),
        ("Rule_QualityRejection", "quality_rejection", "CQ3", "Reject unsafe or contradictory candidates."),
    ]
    with RULE_REGISTER_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rule_id", "category", "supported_cqs", "purpose"])
        writer.writerows(rows)


def build_txt(stats: dict, graph_stats: dict, runtime_stats: dict):
    TXT_OUT.write_text(
        f"""PERSONASHIELD QUEST SCENARIO CONTROL ONTOLOGY (PSQ-SCO)
Version: {VERSION}
Date: 2026-06-30
Namespace: {NEW_BASE}
Prior version: ontology/personashield-odcgct-v8.2-reviewed.owl
Authoritative OWL: ontology/personashield-psq-sco-v9.owl

1. PURPOSE

PSQ-SCO v9 is a reviewer-aligned scenario-control ontology for PersonaShield
Quest. It is a task-oriented application ontology for controlling scenario
template selection, cybersecurity structure, learner compatibility, generated
content quality, evidence grounding, semantic packets, validation decisions,
and scoring metadata.

It does not generate natural language directly. It also does not claim a
complete implemented emotion model. MoodContext is retained only as a runtime
placeholder for the wider ODEACT framework.

2. MAIN V9 IMPROVEMENTS

- Renamed the ontology artifact to PersonaShield Quest Scenario Control
  Ontology (PSQ-SCO) while preserving v8.2 as the prior version.
- Moved CQ3 from broad pedagogical alignment to content quality control.
- Added a ContentQualityKnowledgeEntity module with quality rules, validation
  decisions, scenario-quality scores, constraint violations, and error types.
- Added PerformanceState and MoodContext placeholders for runtime context.
- Added SemanticPacket and GeneratedScenario resources for RAG/LLM control.
- Added minimal pedagogical-import classes for scenario-control constraints.
- Added legal-consequence, validation, scoring, and error-analysis properties.
- Added first-order predicate rule text as annotation metadata.
- Added v9 SPARQL queries, ASK validation cases, mappings, semantic-packet
  schema, runtime export, graph exports, and change log.

3. SIZE

- classes: {stats['classes']}
- object properties: {stats['object_properties']}
- datatype properties: {stats['data_properties']}
- annotation properties: {stats['annotation_properties']}
- named individuals: {stats['individuals']}
- graph nodes: {graph_stats['nodes']}
- graph edges: {graph_stats['edges']}
- runtime records: {runtime_stats['records']}

4. TEST

Run:
  & ".\\.venv-sparql-v8.2\\Scripts\\python.exe" scripts/run_sparql_cq_v9.py --cq all
  & ".\\.venv-sparql-v8.2\\Scripts\\python.exe" scripts/run_sparql_cq_v9.py --validate-cases
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run_hermit_reasoner_v8_2.ps1 -Ontology "ontology\\personashield-psq-sco-v9.owl" -Output "outputs\\v9\\hermit-reasoner-report.json"
  & ".\\.venv-sparql-v8.2\\Scripts\\python.exe" scripts/validate_psq_sco_v9.py

5. ENGINE

  PSQ_KB_DIR=ontology/data/ontology_runtime_v9
  PSQ_RAG_PROFILE=full

No PersonaShieldQuest-GenAI-Engine file is changed.
""",
        encoding="utf-8",
    )


def local_counts(g: Graph) -> dict[str, int]:
    def local_subjects_of_type(type_uri):
        return {s for s in g.subjects(RDF.type, type_uri) if isinstance(s, URIRef) and str(s).startswith(NEW_BASE)}
    return {
        "classes": len(local_subjects_of_type(OWL.Class)),
        "object_properties": len(local_subjects_of_type(OWL.ObjectProperty)),
        "data_properties": len(local_subjects_of_type(OWL.DatatypeProperty)),
        "annotation_properties": len(local_subjects_of_type(OWL.AnnotationProperty)),
        "individuals": len(local_subjects_of_type(OWL.NamedIndividual)),
    }


def build_change_log(stats: dict, graph_stats: dict, runtime_stats: dict):
    DOCS_OUT.write_text(
        f"""# PSQ-SCO v9 Reviewer-Aligned Change Log

Date: 2026-06-30

## Source

- Input reviewer-aligned document: `external-assets/PSQ_SCO_Reviewer_Aligned_Revision_v9.docx`
- Prior ontology: `ontology/personashield-odcgct-v8.2-reviewed.owl`
- New ontology: `ontology/personashield-psq-sco-v9.owl`

## Main Decisions

1. Rename the ontology artifact to **PersonaShield Quest Scenario Control Ontology (PSQ-SCO)**.
2. Treat ODEACT as the wider framework name, not as a claim that v9 implements a complete emotion ontology.
3. Preserve v8.2 as the prior version and create a separate v9 namespace.
4. Replace CQ3 pedagogical alignment with CQ3 content quality control.
5. Keep pedagogical entities only as imported scenario-control constraints.
6. Add quality rules, validation decisions, scoring resources, violation/error categories, and rule text.
7. Add semantic-packet and generated-scenario resources to make RAG/LLM control explicit.
8. Record intended domains and ranges for new v9 properties as annotations rather than hard RDFS domain/range axioms, preventing accidental OWL class inference during HermiT reasoning.

## Current Size

- Classes: {stats['classes']}
- Object properties: {stats['object_properties']}
- Datatype properties: {stats['data_properties']}
- Annotation properties: {stats['annotation_properties']}
- Named individuals: {stats['individuals']}
- Graph nodes: {graph_stats['nodes']}
- Graph edges: {graph_stats['edges']}
- Runtime records: {runtime_stats['records']}

## Validation

Run `scripts/validate_psq_sco_v9.py` after optional HermiT reasoning. The v9
validation package checks RDF loadability, CQ SELECT queries, eight ASK cases,
v9 schema additions, runtime export, and optional HermiT consistency output.
Current validated status: CQ SELECT checks pass, ASK validation passes, and
HermiT reports the ontology as consistent with zero unsatisfiable classes.
""",
        encoding="utf-8",
    )


def main():
    for path in (QUERY_ROOT, QUERY_VALIDATION_ROOT, KG_ROOT, TEST_ROOT, REPORT_ROOT, RUNTIME_ROOT):
        path.mkdir(parents=True, exist_ok=True)
    source = Graph()
    source.parse(SOURCE_OWL, format="xml")
    graph = remap_graph(source)
    update_ontology_header(graph)
    add_v9_schema(graph)
    add_v9_individuals_and_links(graph)
    graph.serialize(ONTOLOGY_OUT, format="xml")
    graph.serialize(TTL_OUT, format="turtle")
    build_queries()
    graph_stats = build_graph_exports(graph)
    runtime_stats = copy_runtime()
    build_binding_files()
    build_test_artifacts()
    stats = local_counts(graph)
    build_txt(stats, graph_stats, runtime_stats)
    build_change_log(stats, graph_stats, runtime_stats)
    print(json.dumps({"ontology": str(ONTOLOGY_OUT), "version": VERSION, "stats": stats, "graph": graph_stats, "runtime": runtime_stats}, indent=2))


if __name__ == "__main__":
    main()
