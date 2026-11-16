param(
    [string]$PythonExe = "python",
    [ValidateRange(1, 1000)]
    [int]$Limit = 1,
    [ValidateSet("qwen2_5_7b", "qwen3_8b", "mistral_7b", "phi3_mini")]
    [string]$Model = "qwen2_5_7b",
    [switch]$Live,
    [switch]$SkipRag
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PackageRoot = $PSScriptRoot
$EngineRoot = Join-Path $PackageRoot "genai_engine"
$OntologyPath = Join-Path $PackageRoot "ontology\ontology\personashield-psq-sco-v9.1.owl"
$MinimalKb = Join-Path $EngineRoot "minimal_kb"
$OutputRoot = Join-Path $PackageRoot ".psq_runs\minimal_four_modes"

if (-not (Test-Path -LiteralPath $OntologyPath -PathType Leaf)) {
    throw "Ontology file not found: $OntologyPath"
}
if (-not (Test-Path -LiteralPath (Join-Path $EngineRoot "generate_scenarios_sco.py") -PathType Leaf)) {
    throw "Generation entry point not found under: $EngineRoot"
}
if (-not $SkipRag -and -not (Test-Path -LiteralPath $MinimalKb -PathType Container)) {
    throw "Minimal RAG knowledge base not found: $MinimalKb"
}

$priorKb = $env:PSQ_KB_DIR
$priorLexical = $env:PSQ_FORCE_LEXICAL_RAG
$arguments = @(
    ".\generate_scenarios_sco.py",
    "--ontology-path", $OntologyPath,
    "--mode", "all_modes",
    "--case-set", "single",
    "--limit", "$Limit",
    "--llm", $Model,
    "--out-dir", $OutputRoot,
    "--no-progress"
)

if ($Live) {
    $arguments += "--require-live-llm"
} else {
    $arguments += "--dry-run"
}

if ($SkipRag) {
    $arguments += "--skip-rag"
} else {
    $env:PSQ_KB_DIR = $MinimalKb
    $env:PSQ_FORCE_LEXICAL_RAG = "1"
}

try {
    Push-Location $EngineRoot
    & $PythonExe @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Four-mode generation failed with exit code $LASTEXITCODE."
    }
} finally {
    Pop-Location
    if ($null -eq $priorKb) {
        Remove-Item Env:PSQ_KB_DIR -ErrorAction SilentlyContinue
    } else {
        $env:PSQ_KB_DIR = $priorKb
    }
    if ($null -eq $priorLexical) {
        Remove-Item Env:PSQ_FORCE_LEXICAL_RAG -ErrorAction SilentlyContinue
    } else {
        $env:PSQ_FORCE_LEXICAL_RAG = $priorLexical
    }
}

$latestRun = Get-ChildItem -LiteralPath $OutputRoot -Directory |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($null -eq $latestRun) {
    throw "Generation completed but no run directory was found under: $OutputRoot"
}

$scenarioFile = Join-Path $latestRun.FullName "scenarios.jsonl"
if (-not (Test-Path -LiteralPath $scenarioFile -PathType Leaf)) {
    throw "Generation completed but scenarios.jsonl was not found: $scenarioFile"
}

$rows = @(
    Get-Content -LiteralPath $scenarioFile |
        Where-Object { $_.Trim() } |
        ForEach-Object { $_ | ConvertFrom-Json }
)
$expectedModes = @("prompt_only", "prompt_rag", "ontology_prompt_rag", "ontology_text_rag")
$actualModes = @($rows | ForEach-Object { $_.mode } | Sort-Object -Unique)
$missingModes = @($expectedModes | Where-Object { $_ -notin $actualModes })
if ($missingModes.Count -gt 0) {
    throw "Output is missing modes: $($missingModes -join ', ')"
}
$failedValidation = @($rows | Where-Object { -not $_.validation_passed })
if ($failedValidation.Count -gt 0) {
    $failedModeNames = @($failedValidation | ForEach-Object { $_.mode })
    throw "Generated scenarios failed engine validation in: $($failedModeNames -join ', ')"
}
if (-not $SkipRag) {
    $promptRag = $rows | Where-Object { $_.mode -eq "prompt_rag" } | Select-Object -First 1
    if ($null -eq $promptRag -or @($promptRag.rag_examples).Count -lt 1) {
        throw "prompt_rag ran without a retrieved minimal knowledge-base example."
    }
}

Write-Host ""
Write-Host "Four-mode generation passed: $($rows.Count) scenario rows; all passed engine validation."
Write-Host "Modes: $($actualModes -join ', ')"
Write-Host "Scenario file: $scenarioFile"
Write-Host "Next: .\EVALUATE_4_MODES_MINIMAL.ps1 -PythonExe `"$PythonExe`""
