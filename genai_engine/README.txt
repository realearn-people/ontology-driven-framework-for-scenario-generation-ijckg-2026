PersonaShield Quest v4.4 grounded patch

This package fixes the generation pipeline so RAG is actually used as grounding.

Replaced / patched files:
- generate_scenarios.py
- rag_engine.py
- prompt_engine.py
- validator.py
- audit_generated_pool.py
- prepare_rag_data.py (includes v5.1 fixes)

Main improvements:
1. Stronger RAG retrieval with relaxation ladder
2. Better indexing text extraction from JSONL fields
3. Prompt-level grounding instructions
4. Generation metadata now stores rag_source_files, rag_preview_snippets, retrieval tiers, and grounding status
5. Validator penalizes scenarios with zero RAG grounding
6. Audit script reports zero_rag_grounding

How to install:
Copy all files into archived-inputs/PersonaShieldQuest-GenAI-Engine and replace existing files.

How to run:
cd "genai_engine"
.\venv\Scripts\activate
python prepare_rag_data.py
python generate_scenarios.py --retrieval-mode ENGLISH_GLOBAL --llm gpt_nano --force

Optional:
python generate_scenarios.py --retrieval-mode ENGLISH_GLOBAL --llm gpt_nano --force --allow-ungrounded

How to verify grounding:
Inspect the generated bundle / scenario_pool JSON for:
- generation_meta.rag_example_count > 0
- generation_meta.rag_source_files non-empty
- generation_meta.grounding_status == "grounded"

Audit:
python audit_generated_pool.py scenario_pool\scenario_pool.json
