"""One-time load: CSV dataset -> legacy MSSQL table (needs admin credentials in .env)."""

import sys
import urllib
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config  # noqa: E402

TABLE = "TBL_SC_FLEET_HIST_RAW"

LEGACY_MAPPING = {
    "timestamp": "TS_UTC",
    "vehicle_gps_latitude": "V_LAT",
    "vehicle_gps_longitude": "V_LON",
    "iot_temperature": "IOT_TEMP_VAL_C",
    "cargo_condition_status": "CGO_COND_CD",
    "risk_classification": "RISK_CLS_TXT",
    "delay_probability": "DELAY_PROB_DEC",
    "port_congestion_level": "PRT_CNG_LVL",
    "route_risk_level": "RT_RSK_IDX",
}


def main() -> None:
    print(f"Loading CSV from {config.CSV_PATH}...")
    df = pd.read_csv(config.CSV_PATH)
    df_legacy = df[list(LEGACY_MAPPING)].rename(columns=LEGACY_MAPPING)
    df_legacy["SYS_INGEST_FLAG"] = "Y"

    print("Connecting to legacy MSSQL database...")
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={config.SQL_HOST},{config.SQL_PORT};"
        "DATABASE=master;"
        f"UID={config.SQL_ADMIN_USER};"
        f"PWD={config.SQL_ADMIN_PASSWORD};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}"
    )
    print(f"Ingesting into {TABLE}...")
    df_legacy.to_sql(TABLE, engine, if_exists="replace", index=False, schema="dbo")
    print("Legacy data ingestion complete.")


if __name__ == "__main__":
    main()
