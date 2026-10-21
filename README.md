# Ontario Emergency Care Access Analytics

**A public-data analytics project examining ambulance response performance and potential emergency-care access disparities across Ontario.**

## Overview

Emergency care accessibility is shaped by several distinct factors: where people live, how quickly ambulance services respond, where hospitals are located, and how long patients spend in emergency departments. This project starts with official Ontario ambulance performance data and provides a reproducible workflow for cleaning, exploring, and summarizing reported response times and call volumes.

The analysis is designed to support evidence-based questions such as:
- How do reported average ambulance response times vary by dispatch centre and reporting year?
- Which service areas report comparatively higher response times or call volumes?
- How have reported metrics changed over time?
- What additional geographic and hospital-level data would be needed to investigate access more directly?

## Data source

**Dataset:** Land Ambulance Response Time Standard – Response Times  
**Resource:** Average Response Times and Call Volumes (English CSV)  
**Publisher:** Government of Ontario, Ministry of Health  
**Last updated by publisher:** April 29, 2024  
**Licence:** Open Government Licence – Ontario

- [Dataset landing page](https://data.ontario.ca/en/dataset/land-ambulance-response-time-standard-response-times)
- [Direct CSV download](https://data.ontario.ca/dataset/0c4c8e2d-5e72-4a72-9101-1570e5a28677/resource/feaebc4c-a197-44ba-84e7-bd19c358e87c/download/average_response_times_and_call_volumes.csv)

The project includes a downloader for the official source CSV. The download could not be completed in the packaging environment because outbound access to the Ontario catalogue was blocked, so no fabricated or empty dataset is included. Run `python src/download_data.py` on your Mac to fetch the real CSV into `data/raw/`. Keep the raw source file unchanged; processed outputs are written to `data/processed/`.

## Repository structure

```text
ontario-emergency-care-access/
├── data/
│   ├── raw/
│   │   └── average_response_times_and_call_volumes.csv
│   └── processed/                 # Generated outputs
├── reports/                       # Generated charts and summaries
├── src/
│   ├── download_data.py
│   └── analyze_access.py
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or later
- `pandas`
- `matplotlib`

## Run the analysis on macOS

Open this folder in VS Code, then run these commands in the integrated terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python src/download_data.py
python src/analyze_access.py
```

The script reads the bundled CSV and creates:
- `data/processed/cleaned_ambulance_response_data.csv`
- `data/processed/summary_by_service_and_year.csv`
- `reports/average_response_time_by_year.png`
- `reports/highest_average_response_times_latest_year.png`
- `reports/analysis_summary.txt`

If the source file uses slightly different column labels or includes non-numeric values, the script attempts to normalize common variants and reports any columns it cannot interpret.

## Suggested analysis

1. **Data quality:** inspect missing values, duplicate rows, data types, and reporting-year coverage.
2. **Service comparison:** compare average response times and call volumes across reporting areas.
3. **Trend analysis:** examine changes in the reported average response time over available years.
4. **Outlier review:** flag service/year combinations with comparatively high reported averages for further investigation.
5. **Dashboard:** import the processed CSV files into Power BI, Tableau, or another BI tool to build service-area and year filters, KPI cards, trend charts, and ranked comparisons.

## Interpretation and limitations

- Average ambulance response time is a service-performance measure; it is **not** the same as a patient's travel time to a hospital or time spent waiting in an emergency department.
- Service-area averages can conceal differences within a service area and across call severity categories.
- The data is reported at an aggregate level and should not be used to infer outcomes for individual patients.
- A longer reported average does not, by itself, establish that a community has inadequate care. Geography, case mix, dispatch processes, traffic, service definitions, and reporting coverage can affect comparisons.
- Hospital locations, road-network travel times, population estimates, rurality measures, and emergency-department time-spent data are separate sources that should be integrated in a later phase before making stronger claims about geographic accessibility.
- This project is for analytical and educational purposes. It is not a live emergency-routing tool and must not be used to decide where to seek urgent care.

## Data refresh

To download or refresh the source, run `python src/download_data.py`. It retrieves the English CSV from the official resource and saves it under `data/raw/`. Record the download date and review any schema changes before comparing results across releases.

## Reproducibility

The analysis script does not modify the raw CSV. It produces derived tables and visualizations from the bundled source data. Run the script again whenever the raw source is updated.

## Author

Prepared as a portfolio analytics project using publicly available Ontario government data.
