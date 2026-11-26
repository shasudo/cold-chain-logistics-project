"""Single place for all settings. Everything comes from `.env` (see `.env.example`)."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

# --- DeepSeek (the only LLM) ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# --- Telemetry DB (legacy MSSQL, read via the read-only view) ---
SQL_HOST = os.getenv("SQL_SERVER_HOST", "localhost")
SQL_PORT = os.getenv("SQL_SERVER_PORT", "1433")
SQL_AGENT_USER = os.getenv("SQL_AGENT_USER", "USR_FDE_RO")
SQL_AGENT_PASSWORD = os.getenv("SQL_AGENT_PASSWORD", "")
SQL_ADMIN_USER = os.getenv("SQL_ADMIN_USER", "sa")
SQL_ADMIN_PASSWORD = os.getenv("SQL_ADMIN_PASSWORD", "")

# --- Local paths ---
CHROMA_DIR = ROOT / "chroma_db"
SOP_DIR = ROOT / "data" / "policy"
CSV_PATH = ROOT / "data" / "dynamic_supply_chain_logistics_dataset.csv"
SYSTEM_PROMPT_PATH = ROOT / "src" / "prompts" / "system_prompt.txt"

TELEMETRY_VIEW = "FDE_VIEWS.VW_ACTIVE_FLEET"
SOP_COLLECTION = "coldchain-sop"
