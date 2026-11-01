# IndusSphere Pakistan — Agentic Reporting Update

This update extends the existing Streamlit application without removing its existing pages or workflows.

## Included changes
- Every report generated in the Agentic AI Command Centre can be downloaded as Markdown (`.md`) and PDF (`.pdf`).
- The all-reports ZIP now contains both formats for each report.
- Each report expander displays an interactive OpenStreetMap reference map for recognised Pakistan locations explicitly mentioned in the report, plus an interactive Plotly bar chart for clearly labelled numeric values stated in the report.
- The Indus Plain CrewAI assessment has the same Markdown/PDF exports and report-specific visualisations.
- Visuals do not invent risk scores, measurements, or hazard boundaries. Map markers are approximate reference locations; graph values are extracted from report text and must be checked against units and sources.

## Deploy
1. Replace the repository `app.py` with the included `app.py`.
2. Add/replace `agentic_ai.py` and `requirements.txt` with the included versions.
3. Keep your existing Streamlit secrets (`GROQ_API_KEY` or `OPENAI_API_KEY`) in Streamlit Cloud settings; do not commit keys.
4. Commit and push. Streamlit Cloud will install the updated dependencies and redeploy.

## Notes
- PDF export requires ReportLab (included in `requirements.txt`).
- Plotly charts and maps are interactive in the Streamlit app; PDF exports contain the textual report, not interactive map/chart widgets.
- Run reports using verified uploaded evidence and independently review all AI-generated conclusions.
