# Fork, upload, and open a pull request

The upstream repository is:

`https://github.com/realearn-people/ontology-driven-framework-for-scenario-generation-ijckg-2026`

The contribution branch prepared in this folder is:

`psq-sco-internship-handover`

Direct write access to the upstream repository is not required. Use the fork and
pull-request workflow below.

## 1. Create the fork

Sign in to GitHub as `HopeChanphot`, then open:

`https://github.com/realearn-people/ontology-driven-framework-for-scenario-generation-ijckg-2026/fork`

Create this fork:

`https://github.com/HopeChanphot/ontology-driven-framework-for-scenario-generation-ijckg-2026`

Do this before running `git push`.

## 2. Sign in from PowerShell

```powershell
Set-Location 'PSQ_SCO_GitHub_Ready_2026-07-30'

git credential-manager github login `
  --username HopeChanphot `
  --web `
  --force
```

If browser login is unavailable, replace the login command with:

```powershell
git credential-manager github login `
  --username HopeChanphot `
  --device `
  --force
```

## 3. Confirm the remotes

```powershell
git remote -v
```

The expected remotes are:

- `origin` - `https://github.com/HopeChanphot/ontology-driven-framework-for-scenario-generation-ijckg-2026.git`
- `upstream` - `https://github.com/realearn-people/ontology-driven-framework-for-scenario-generation-ijckg-2026.git`

They are already configured in this prepared folder.

## 4. Synchronize, verify, and push to the fork

```powershell
git switch psq-sco-internship-handover
git fetch upstream
git rebase upstream/main

python .\tools\package_integrity.py verify

git push -u origin psq-sco-internship-handover

git status --short --branch
git log -1 --oneline
```

Do not use `git push --force`. If the rebase reports a conflict, stop and resolve
the conflict before pushing.

## 5. Open the pull request

After the push succeeds, open:

`https://github.com/realearn-people/ontology-driven-framework-for-scenario-generation-ijckg-2026/compare/main...HopeChanphot:psq-sco-internship-handover?expand=1`

Confirm these selections:

- Base repository: `realearn-people/ontology-driven-framework-for-scenario-generation-ijckg-2026`
- Base branch: `main`
- Head repository: `HopeChanphot/ontology-driven-framework-for-scenario-generation-ijckg-2026`
- Compare branch: `psq-sco-internship-handover`

Suggested pull-request title:

`Add PSQ-SCO internship research artifact and reproducibility package`

Review the changed-files tab before selecting **Create pull request**.

## Data boundary

This public repository contains the redistributable synthetic RAG fixture at
`genai_engine/minimal_kb/email/psq_minimal_examples_en.jsonl`. Do not copy the
separate private raw-corpus ZIP or any local `.env` file into this repository.
See `DATA_AVAILABILITY.md` and `LICENSE_AND_DATA_NOTICE.md`.
