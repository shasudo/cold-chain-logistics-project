"""Agent tools as LangChain @tool functions (docstrings become the tool schemas)."""

import urllib

import requests
from langchain_core.tools import tool

import config
from src.rag import get_vectorstore


@tool
def query_telemetry_db(sql_query: str) -> str:
    """Run a SQL SELECT against FDE_VIEWS.VW_ACTIVE_FLEET and return up to 10 rows.

    Columns: Timestamp, Latitude, Longitude, Current_Temperature_C,
    Cargo_Condition_Code, Risk_Classification, Delay_Probability,
    Port_Congestion_Level, Route_Risk_Index. Only SELECT statements are allowed.
    """
    if not sql_query.strip().upper().startswith("SELECT"):
        return "SECURITY BLOCK: Only SELECT operations are authorized on this view."

    try:
        from sqlalchemy import create_engine, text
    except Exception as e:
        return f"Database Error: SQL driver not installed ({e})."

    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={config.SQL_HOST},{config.SQL_PORT};"
        "DATABASE=master;"
        f"UID={config.SQL_AGENT_USER};"
        f"PWD={config.SQL_AGENT_PASSWORD};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}"
    )
    try:
        with engine.connect() as conn:
            cursor = conn.execute(text(sql_query))
            columns = list(cursor.keys())
            rows = cursor.fetchmany(10)
    except Exception as e:
        return f"Database Error: {e}"

    if not rows:
        return "No records matched the query criteria."
    lines = [f"COLUMNS: {', '.join(columns)}"]
    lines += [str(tuple(row)) for row in rows]
    return "\n".join(lines)


@tool
def fetch_corridor_conditions(latitude: float, longitude: float) -> str:
    """Fetch live weather and corridor conditions for GPS coordinates via Open-Meteo."""
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
            },
            timeout=6,
        )
        resp.raise_for_status()
        current = resp.json().get("current_weather", {})
        temp = current.get("temperature", "N/A")
        wind = current.get("windspeed", 0.0)
    except Exception as e:
        return f"Corridor API Communication Failure: {e}"

    congested = wind > 10.0
    return (
        "--- LIVE CORRIDOR TELEMETRY ---\n"
        f"Target GPS: {latitude}, {longitude}\n"
        f"External Temp: {temp}C | Wind Speed: {wind} km/h\n"
        "Corridor Risk: "
        f"{'High Transit Disruption' if congested else 'Corridor Normal'}"
        f" (Congestion Index: {8.5 if congested else 2.5}/10)\n"
        "-------------------------------"
    )


@tool
def search_compliance_sop(query: str) -> str:
    """Search cold-chain Standard Operating Procedures for temperature thresholds, breach mitigations, and escalation rules."""
    try:
        docs = get_vectorstore().as_retriever(search_kwargs={"k": 3}).invoke(query)
    except Exception as e:
        return f"Vector Store Retrieval Error: {e}"

    if not docs:
        return "No matching compliance clauses found. Run scripts/ingest_sop_chroma.py first."
    blocks = [
        f"[Source: {d.metadata.get('source_file', 'SOP')}]\n{d.page_content}"
        for d in docs
    ]
    return "--- COMPLIANCE SOP CONTEXT ---\n" + "\n\n".join(blocks) + "\n------------------------------"


TOOLS = [query_telemetry_db, fetch_corridor_conditions, search_compliance_sop]
