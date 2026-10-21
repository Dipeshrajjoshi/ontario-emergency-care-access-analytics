#!/usr/bin/env python3
"""Clean and explore Ontario ambulance response-time and call-volume data."""
from pathlib import Path
import re
import sys
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "average_response_times_and_call_volumes.csv"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

def normalize(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())

def find_column(columns, candidates):
    mapping = {normalize(c): c for c in columns}
    for candidate in candidates:
        if normalize(candidate) in mapping:
            return mapping[normalize(candidate)]
    for norm, original in mapping.items():
        if any(normalize(candidate) in norm for candidate in candidates):
            return original
    return None

def numeric(series):
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False)
                    .str.replace(r"[^0-9.\\-]", "", regex=True),
        errors="coerce"
    )

def main():
    if not RAW_FILE.exists() or RAW_FILE.stat().st_size < 20:
        sys.exit(f"Source CSV not found or empty: {RAW_FILE}")

    df = pd.read_csv(RAW_FILE, encoding="utf-8-sig")
    if df.empty:
        sys.exit("The source CSV contains no data rows.")

    service_col = find_column(df.columns, ["CACC Location", "Ambulance Service Coverage Area", "Service Area"])
    year_col = find_column(df.columns, ["Reporting Year", "Reporting Year"])
    response_col = find_column(df.columns, ["Average Response Time", "Average Response Times"])
    volume_col = find_column(df.columns, ["Call Volume", "Call Volumes"])
    org_col = find_column(df.columns, ["Organization ID"])

    required = {"service": service_col, "year": year_col, "response_time": response_col, "call_volume": volume_col}
    missing = [name for name, col in required.items() if col is None]
    if missing:
        print("Columns found:", list(df.columns))
        sys.exit("Could not identify required columns: " + ", ".join(missing))

    clean = pd.DataFrame({
        "service_area": df[service_col].astype("string").str.strip(),
        "reporting_year": df[year_col].astype("string").str.strip(),
        "average_response_time": numeric(df[response_col]),
        "call_volume": numeric(df[volume_col]),
    })
    if org_col:
        clean["organization_id"] = df[org_col].astype("string").str.strip()

    clean["reporting_year"] = pd.to_numeric(clean["reporting_year"].str.extract(r"(\d{4})", expand=False), errors="coerce").astype("Int64")
    clean = clean.dropna(subset=["service_area", "reporting_year"])
    clean = clean.drop_duplicates()
    clean["service_area"] = clean["service_area"].str.replace(r"\s+", " ", regex=True)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    clean.to_csv(PROCESSED / "cleaned_ambulance_response_data.csv", index=False)

    valid = clean.dropna(subset=["average_response_time"])
    summary = (clean.groupby(["service_area", "reporting_year"], dropna=False)
                    .agg(average_response_time=("average_response_time", "mean"),
                         call_volume=("call_volume", "sum"),
                         records=("service_area", "size"))
                    .reset_index()
                    .sort_values(["reporting_year", "average_response_time"], ascending=[True, False]))
    summary.to_csv(PROCESSED / "summary_by_service_and_year.csv", index=False)

    lines = [
        "Ontario Emergency Care Access Analytics — Run Summary",
        "=" * 55,
        f"Rows in source: {len(df):,}",
        f"Rows after basic cleaning: {len(clean):,}",
        f"Service areas: {clean['service_area'].nunique(dropna=True):,}",
        f"Reporting years: {clean['reporting_year'].nunique(dropna=True):,}",
        f"Missing average response times: {clean['average_response_time'].isna().sum():,}",
        f"Missing call volumes: {clean['call_volume'].isna().sum():,}",
    ]
    if not valid.empty:
        lines += [
            f"Overall mean of reported service-level response-time values: {valid['average_response_time'].mean():.2f}",
            "Note: this is an unweighted mean of available rows, not a call-weighted provincial estimate."
        ]

    yearly = (clean.dropna(subset=["average_response_time"])
                   .groupby("reporting_year", as_index=False)["average_response_time"].mean()
                   .sort_values("reporting_year"))
    if not yearly.empty:
        plt.figure(figsize=(9, 5))
        plt.plot(yearly["reporting_year"].astype(int), yearly["average_response_time"], marker="o")
        plt.title("Average Reported Ambulance Response Time by Reporting Year")
        plt.xlabel("Reporting year")
        plt.ylabel("Average response time (source units)")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(REPORTS / "average_response_time_by_year.png", dpi=160)
        plt.close()

    latest_year = clean["reporting_year"].max()
    latest = clean[(clean["reporting_year"] == latest_year) & clean["average_response_time"].notna()]
    if not latest.empty:
        latest = latest.sort_values("average_response_time", ascending=False).head(15)
        plt.figure(figsize=(10, max(5, len(latest) * 0.35)))
        plt.barh(latest["service_area"].astype(str)[::-1], latest["average_response_time"][::-1])
        plt.title(f"Highest Reported Average Response Times — {int(latest_year)}")
        plt.xlabel("Average response time (source units)")
        plt.ylabel("Service area")
        plt.tight_layout()
        plt.savefig(REPORTS / "highest_average_response_times_latest_year.png", dpi=160)
        plt.close()

    (REPORTS / "analysis_summary.txt").write_text("\\n".join(lines) + "\\n", encoding="utf-8")
    print("\\n".join(lines))
    print("\\nOutputs saved to data/processed/ and reports/")

if __name__ == "__main__":
    main()
