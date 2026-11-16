param(
    [string]$PythonExe = "python",
    [string]$ScenarioFile = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PackageRoot = $PSScriptRoot
$EngineRoot = Join-Path $PackageRoot "genai_engine"
$OntologyRoot = Join-Path $PackageRoot "ontology"
$OntologyPath = Join-Path $OntologyRoot "ontology\personashield-psq-sco-v9.1.owl"
$QueriesDir = Join-Path $OntologyRoot "queries\v9_1"
$HermitReport = Join-Path $OntologyRoot "outputs\v9_1\hermit-reasoner-report.json"
$GenerationRoot = Join-Path $PackageRoot ".psq_runs\minimal_four_modes"
$EvaluationRoot = Join-Path $PackageRoot ".psq_runs\minimal_four_modes_evaluation"

if ([string]::IsNullOrWhiteSpace($ScenarioFile)) {
    $latestGeneration = Get-ChildItem -LiteralPath $GenerationRoot -Directory -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($null -eq $latestGeneration) {
        throw "No generated run found. Run .\RUN_4_MODES_MINIMAL.ps1 first."
    }
    $ScenarioFiles = @(
        "scenarios_prompt_only.jsonl",
        "scenarios_prompt_rag.jsonl",
        "scenarios_ontology_prompt_rag.jsonl",
        "scenarios_ontology_text_rag.jsonl"
    ) | ForEach-Object { Join-Path $latestGeneration.FullName $_ }
} else {
    $ScenarioFiles = @((Resolve-Path -LiteralPath $ScenarioFile).Path)
}

foreach ($file in $ScenarioFiles) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Scenario JSONL file not found: $file"
    }
}

$arguments = @(
    ".\evaluate_three_layer.py",
    "--ontology-root", $OntologyRoot,
    "--ontology-path", $OntologyPath,
    "--queries-dir", $QueriesDir,
    "--hermit-report", $HermitReport,
    "--out-dir", $EvaluationRoot,
    "--diversity-embedding-backend", "hash",
    "--standard-metrics-only",
    "--smoke-report"
)
foreach ($file in $ScenarioFiles) {
    $arguments += @("--input-dir", $file)
}

try {
    Push-Location $EngineRoot
    & $PythonExe @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Three-layer evaluation failed with exit code $LASTEXITCODE."
    }
} finally {
    Pop-Location
}

$latestEvaluation = Get-ChildItem -LiteralPath $EvaluationRoot -Directory |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($null -eq $latestEvaluation) {
    throw "Evaluation completed but no result directory was found under: $EvaluationRoot"
}

$requiredOutputs = @(
    "ontology_validation.json",
    "scenario_scores.csv",
    "method_summary.csv",
    "evaluation_report.md",
    "run_metadata.json"
)
$missingOutputs = @(
    $requiredOutputs |
        Where-Object { -not (Test-Path -LiteralPath (Join-Path $latestEvaluation.FullName $_) -PathType Leaf) }
)
if ($missingOutputs.Count -gt 0) {
    throw "Evaluation is missing required outputs: $($missingOutputs -join ', ')"
}

$metadata = Get-Content -LiteralPath (Join-Path $latestEvaluation.FullName "run_metadata.json") -Raw |
    ConvertFrom-Json
if ([int]$metadata.scenario_record_count -lt 4) {
    throw "Evaluation loaded fewer than four scenario rows."
}

Write-Host ""
Write-Host "Three-layer evaluation passed: $($metadata.scenario_record_count) scenario rows."
Write-Host "Evaluation folder: $($latestEvaluation.FullName)"
Write-Host "Read first: $(Join-Path $latestEvaluation.FullName 'evaluation_report.md')"
