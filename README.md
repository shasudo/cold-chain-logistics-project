# Cold-Chain Dispatch Agent

Simple DeepSeek agent that chats with cold-chain fleet data: SQL telemetry, live corridor weather, and SOP compliance stored in local ChromaDB. No Pinecone, no OpenAI, no Ollama.

## Structure

- `config.py` — all settings from `.env`
- `src/app.py` — Streamlit chat UI (`streamlit run src/app.py`)
- `src/agent.py` — DeepSeek ReAct agent via LangChain `create_agent` (also CLI: `python src/agent.py`)
- `src/tools.py` — the 3 tools as LangChain `@tool` functions
- `src/rag.py` — SOP vector store (LangChain `Chroma` + local ONNX embeddings)
- `src/prompts/system_prompt.txt` — agent instructions
- `scripts/ingest_legacy_data.py` — one-time CSV load into MSSQL
- `scripts/ingest_sop_chroma.py` — SOP markdown files into local ChromaDB (`./chroma_db`)
- `scripts/setup_security_and_view.sql` — read-only view + agent login for MSSQL
- `scripts/count_fleet_rows.sql` — row-count sanity check
- `data/dynamic_supply_chain_logistics_dataset.csv` — source dataset
- `data/policy/` — SOP markdown files indexed into ChromaDB

## Setup

```bash
conda create -n coldchain python=3.11 --override-channels -c conda-forge -y
conda activate coldchain
pip install -r requirements.txt
cp .env.example .env   # then fill in DEEPSEEK_API_KEY and SQL passwords

# 1. Start MSSQL (Docker) and load the telemetry table
python scripts/ingest_legacy_data.py

# 2. Create the read-only view + agent login (run in your SQL client)
#    -> scripts/setup_security_and_view.sql

# 3. Index the SOP docs into local ChromaDB (no API key needed)
python scripts/ingest_sop_chroma.py

# 4. Chat
streamlit run src/app.py
```

## Try asking

- Find active shipments near Los Angeles (lat ~33.8, lon ~-118.1). Check the weather there, and tell me if cargo temperature violates the SOP for fresh perishables.
- Explain the difference between a Tier 1 and Tier 2 escalation.
