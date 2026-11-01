"""India Indus-basin hydropower inventory used by the separate map in IndusSphere.

The 17-project grouping is a dashboard research dataset assembled from the
user-supplied list and checked against CEA/NHPC institutional records. Status
labels are kept as a separate field so that project inventory and construction
status are not conflated.
"""
import pandas as pd

PROJECTS = [
    # name, status, capacity, river, basin, lat, lon, source_note
    ("Uri-I", "Operational", 480.0, "Jhelum", "Jhelum / Indus", 34.08, 74.03, "CEA hydro profile"),
    ("Uri-II", "Operational", 240.0, "Jhelum", "Jhelum / Indus", 34.09, 74.04, "CEA hydro profile"),
    ("Lower Jhelum", "Operational", 105.0, "Jhelum", "Jhelum / Indus", 34.20, 74.35, "CEA hydro profile"),
    ("Upper Sindh-II & Extension", "Operational", 105.0, "Sindh Nallah", "Jhelum / Indus", 34.05, 74.58, "CEA hydro profile"),
    ("Kishenganga", "Operational", 330.0, "Kishanganga", "Jhelum / Indus", 34.63, 74.88, "CEA hydro profile"),
    ("Dulhasti", "Operational", 390.0, "Chenab", "Chenab / Indus", 33.65, 76.00, "CEA hydro profile"),
    ("Salal I & II", "Operational", 690.0, "Chenab", "Chenab / Indus", 33.12, 74.83, "CEA hydro profile"),
    ("Baglihar-I", "Operational", 450.0, "Chenab", "Chenab / Indus", 33.13, 75.18, "CEA hydro profile"),
    ("Baglihar-II", "Operational", 450.0, "Chenab", "Chenab / Indus", 33.14, 75.19, "CEA hydro profile"),
    ("Sewa-II", "Operational", 120.0, "Sewa", "Ravi / Indus", 32.65, 75.53, "CEA hydro profile"),
    ("Pakal Dul", "Under Construction", 1000.0, "Marusudar", "Chenab / Indus", 33.65, 76.05, "CEA + NHPC"),
    ("Parnai", "Under Construction", 37.5, "Suran / Parnai", "Jhelum / Indus", 33.77, 74.09, "CEA hydro profile; river naming normalized"),
    ("Kiru", "Under Construction", 624.0, "Chenab", "Chenab / Indus", 33.55, 76.02, "CEA + NHPC"),
    ("Ratle", "Under Construction", 850.0, "Chenab", "Chenab / Indus", 33.30, 75.90, "CEA + NHPC"),
    ("Kwar", "Under Construction", 540.0, "Chenab", "Chenab / Indus", 33.48, 76.08, "CEA + NHPC"),
    ("Uri-I Stage-II", "Under Construction", 240.0, "Jhelum", "Jhelum / Indus", 34.08, 74.03, "CEA + NHPC"),
    ("Dulhasti Stage-II", "Under Construction", 260.0, "Chenab", "Chenab / Indus", 33.66, 76.01, "CEA + NHPC"),
]

COLUMNS = ["project", "status", "capacity_mw", "river", "basin", "latitude", "longitude", "source_note"]
PROJECTS_DF = pd.DataFrame(PROJECTS, columns=COLUMNS)

# Descriptive context is intentionally separate from the source-note field.
# Coordinates are approximate map markers and must not be used for surveying.
PROJECT_DESCRIPTIONS = {
    "Uri-I": "Operational hydropower station on the Jhelum River system.",
    "Uri-II": "Operational hydropower station on the Jhelum River system.",
    "Lower Jhelum": "Operational hydropower project on the Jhelum River.",
    "Upper Sindh-II & Extension": "Operational project on Sindh Nallah, a tributary in the Jhelum system.",
    "Kishenganga": "Operational hydropower project on the Kishanganga River, a Jhelum tributary.",
    "Dulhasti": "Operational hydropower project on the Chenab River.",
    "Salal I & II": "Operational Salal hydropower scheme on the Chenab River; capacity is grouped as supplied.",
    "Baglihar-I": "Operational Baglihar stage on the Chenab River.",
    "Baglihar-II": "Operational Baglihar stage on the Chenab River.",
    "Sewa-II": "Operational hydropower project on the Sewa River in the Ravi/Indus basin context.",
    "Pakal Dul": "Listed under construction; a storage hydropower scheme on the Marusudar, a Chenab tributary.",
    "Parnai": "Listed under construction on the Parnai/Suran river system, associated with the Jhelum basin.",
    "Kiru": "Listed under construction hydropower project on the Chenab River.",
    "Ratle": "Listed under construction hydropower project on the Chenab River.",
    "Kwar": "Listed under construction hydropower project on the Chenab River.",
    "Uri-I Stage-II": "Listed under construction stage on the Jhelum River system.",
    "Dulhasti Stage-II": "Listed under construction stage associated with the Chenab River project system.",
}
PROJECTS_DF["description"] = PROJECTS_DF["project"].map(PROJECT_DESCRIPTIONS).fillna("Hydropower project in the Indus River System inventory.")

TOTAL_CAPACITY_MW = float(PROJECTS_DF["capacity_mw"].sum())
OPERATIONAL_CAPACITY_MW = float(PROJECTS_DF.loc[PROJECTS_DF.status == "Operational", "capacity_mw"].sum())
UNDER_CONSTRUCTION_CAPACITY_MW = float(PROJECTS_DF.loc[PROJECTS_DF.status == "Under Construction", "capacity_mw"].sum())

# These coordinates are approximate visualization points, not survey/GIS coordinates.
MAP_NOTE = "Approximate visualization coordinates are used for the separate project map; they are not project survey coordinates."

SOURCE_URLS = {
    "CEA — Profile on Hydro Development for U.T. of Jammu & Kashmir":
        "https://cea.nic.in/wp-content/uploads/hpi/2025/04/All_India_Hydro_Potential_Profile_April_25-2.pdf",
    "CEA — HPPI Reports": "https://cea.nic.in/hpi-report/?lang=en",
    "NHPC — Project List": "https://www.nhpcindia.com/welcome/project.html",
    "User-provided project summary (secondary reference)": "https://www.linkedin.com/posts/rabia-akhtar-ph-d-4a702b49_before-we-debate-indias-hydro-war-on-pakistan-activity-7480966828253667328-hIeh",
}
