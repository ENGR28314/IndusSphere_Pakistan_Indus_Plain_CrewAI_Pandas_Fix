"""Interactive mining and dry-fruit sector profile for IndusSphere Pakistan.

Figures supplied in project notes are presented as reported/indicative and should
be independently checked against current official statistical and legal sources.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

MINERAL_DATA = [
    {"Mineral / resource": "Copper and gold", "Key area": "Chagai, Balochistan", "Province": "Balochistan", "Status / context": "Reko Diq development; Saindak operating project", "Value chain opportunity": "Concentrating, smelting, refining, local services", "Evidence status": "Project details and dates require current source check"},
    {"Mineral / resource": "Rock salt", "Key area": "Salt Range, Punjab", "Province": "Punjab", "Status / context": "Established extraction and processing", "Value chain opportunity": "Food-grade processing, packaging, traceability", "Evidence status": "General resource profile; verify reserve rankings"},
    {"Mineral / resource": "Coal", "Key area": "Thar, Sindh", "Province": "Sindh", "Status / context": "Large lignite resource and energy development", "Value chain opportunity": "Mine safety, emissions management, rehabilitation", "Evidence status": "Project and reserve figures need current source check"},
    {"Mineral / resource": "Chromite", "Key area": "Balochistan and Khyber Pakhtunkhwa", "Province": "Multiple", "Status / context": "Metallic mineral extraction", "Value chain opportunity": "Beneficiation and responsible export processing", "Evidence status": "Broad sector profile"},
    {"Mineral / resource": "Iron ore", "Key area": "Multiple locations", "Province": "Multiple", "Status / context": "Resource occurrence and extraction vary by deposit", "Value chain opportunity": "Ore upgrading and domestic industrial inputs", "Evidence status": "Deposit-specific assessment required"},
    {"Mineral / resource": "Gypsum and industrial minerals", "Key area": "Punjab, Khyber Pakhtunkhwa, Balochistan", "Province": "Multiple", "Status / context": "Used in construction and manufacturing", "Value chain opportunity": "Local processing and product standards", "Evidence status": "Broad sector profile"},
    {"Mineral / resource": "Gemstones and dimension stone", "Key area": "Gilgit-Baltistan, KP, Balochistan, Punjab", "Province": "Multiple", "Status / context": "Small and medium-scale extraction and trading", "Value chain opportunity": "Cutting, polishing, certification and safer quarrying", "Evidence status": "Regional profile; production data varies"},
]

PROJECT_DATA = [
    {"Project": "Reko Diq", "Province": "Balochistan", "Commodity": "Copper and gold", "Project context": "Large-scale development project; ownership and financing details should be checked against current company and government disclosures", "Indicative milestone": "First production has been reported as targeted for late 2028; schedule may change", "Source": "https://www.barrick.com/English/operations/reko-diq/default.aspx"},
    {"Project": "Saindak", "Province": "Balochistan", "Commodity": "Copper, gold and silver", "Project context": "Operating project with a long-running Chinese operator arrangement", "Indicative milestone": "Check latest operator and government updates for current phase/status", "Source": "https://www.csis.org/analysis/minerals-diplomacy-meets-market-reality-case-pakistan"},
    {"Project": "Thar coal", "Province": "Sindh", "Commodity": "Lignite coal", "Project context": "Mine-mouth energy and associated infrastructure", "Indicative milestone": "Operational status differs by block and power project", "Source": "https://www.pc.gov.pk/uploads/plans/Ch24-Manufacturing-minerals2.pdf"},
]

FRUIT_DATA = [
    {"Product / value chain": "Apricot", "Main hubs": "Hunza, Skardu, Gilgit-Baltistan; northern KP", "Province / territory": "Gilgit-Baltistan / KP", "Processing opportunities": "Hygienic drying, moisture control, grading, kernels and packaging", "Climate / water considerations": "Cool highland growing conditions; post-harvest handling and drying weather matter"},
    {"Product / value chain": "Walnut", "Main hubs": "Gilgit-Baltistan, Chitral and other northern valleys", "Province / territory": "Gilgit-Baltistan / KP", "Processing opportunities": "Cracking, sorting, food-safe storage, oil and packaged kernels", "Climate / water considerations": "Highland orchards; frost, water access and storage conditions vary"},
    {"Product / value chain": "Pine nuts (chilgoza)", "Main hubs": "Balochistan and selected northern areas", "Province / territory": "Balochistan / northern regions", "Processing opportunities": "Responsible collection, shelling, grading and traceable packaging", "Climate / water considerations": "Forest ecosystem protection and sustainable harvesting are important"},
    {"Product / value chain": "Almond", "Main hubs": "Balochistan, including Quetta and Kalat region", "Province / territory": "Balochistan", "Processing opportunities": "Mechanical shelling, grading, aflatoxin control and packaging", "Climate / water considerations": "Dryland orchard conditions; drought and heat risks need local assessment"},
    {"Product / value chain": "Pistachio", "Main hubs": "Dry upland locations including parts of Balochistan", "Province / territory": "Balochistan / other suitable zones", "Processing opportunities": "Sorting, safe drying, roasting where appropriate, packaging", "Climate / water considerations": "Suitability is location-specific; avoid treating all districts as equivalent"},
    {"Product / value chain": "Raisins", "Main hubs": "Balochistan grape-growing districts, including Pishin and Quetta region", "Province / territory": "Balochistan", "Processing opportunities": "Covered drying, sorting, residue compliance and export packaging", "Climate / water considerations": "Drying conditions and food-safety controls affect quality"},
    {"Product / value chain": "Dates", "Main hubs": "Khairpur and other Sindh districts; parts of Balochistan", "Province / territory": "Sindh / Balochistan", "Processing opportunities": "Sorting, grading, hygienic packing, paste and value-added products", "Climate / water considerations": "Heat and irrigation demand; dates are tracked separately from dried-fruit categories in trade data"},
]

SOURCE_LINKS = [
    ("Geological Survey of Pakistan — mineral resources overview", "https://gsp.gov.pk/report/an-overview-of-mineral-resources-of-pakistan-1995/"),
    ("Trade Development Authority of Pakistan — minerals and metals sector analysis", "https://tdap.gov.pk/wp-content/uploads/2022/03/Analysis-of-Minerals-and-Metals-Sector-of-Pakistan-A-Case-of-Gypsum.pdf"),
    ("Punjab Mines & Minerals — investment and business promotion", "https://mnm.punjab.gov.pk/investment_and_business_promotion"),
    ("Barrick — Reko Diq project", "https://www.barrick.com/English/operations/reko-diq/default.aspx"),
    ("Trade Development Authority of Pakistan — Pakistan dry fruits", "https://tdap.gov.pk/wp-content/uploads/2023/02/Pakistan-Dry-Fruits.pdf"),
    ("TDAP — dates production, consumption and export potential", "https://tdap.gov.pk/wp-content/uploads/2025/01/Dates-Production-Consumption-Exports-Potential.pdf"),
    ("Ministry of Commerce — Fruits and Vegetable Sector Strategy", "https://www.commerce.gov.pk/wp-content/uploads/2024/05/Fruits_and_Vegetable_sector_strategy-Pakistan-3_web.pdf"),
    ("OEC — Pakistan dried-fruit trade profile", "https://oec.world/en/profile/bilateral-product/dried-fruits/reporter/pak"),
    ("Pakistan Customs Tariff 2025–26 (FBR)", "https://download1.fbr.gov.pk/Docs/20258111683941732Tariff-2025-26.pdf"),
    ("Centre for Strategic and International Studies — Pakistan minerals diplomacy", "https://www.csis.org/analysis/minerals-diplomacy-meets-market-reality-case-pakistan"),
]

def render_mining_dryfruit_page():
    st.title("⛏️ Pakistan Mining & Dry Fruit Sectors")
    st.write("Interactive overview of mineral resources, major projects, provincial governance questions, highland and dryland fruit value chains, export readiness, and climate-linked risks.")
    st.warning("Evidence note: some numerical estimates and future event details supplied in the project brief are not independently verified here. Use the linked primary sources and current official statistics before citing figures as facts.")
    tab_m, tab_f, tab_trade, tab_sources = st.tabs(["⛏️ Mining", "🥜 Dry fruit & dates", "📦 Processing & trade", "🔗 Sources & evidence"])
    with tab_m:
        st.subheader("Mineral resources and value-chain opportunities")
        q = st.text_input("Search mineral, province, or opportunity", key="mining_search")
        provinces = ["All"] + sorted({x["Province"] for x in MINERAL_DATA})
        prov = st.selectbox("Province filter", provinces, key="mining_province")
        df = pd.DataFrame(MINERAL_DATA)
        if prov != "All":
            df = df[df["Province"] == prov]
        if q.strip():
            df = df[df.astype(str).apply(lambda c: c.str.contains(q.strip(), case=False, na=False)).any(axis=1)]
        st.dataframe(df, use_container_width=True, hide_index=True)
        chart = pd.DataFrame(MINERAL_DATA).groupby("Province", as_index=False).size().rename(columns={"size":"Listed resource categories"})
        st.plotly_chart(px.bar(chart, x="Province", y="Listed resource categories", title="Listed mineral-resource categories by province/region"), use_container_width=True)
        st.caption("This chart counts illustrative resource categories in this dashboard; it is not a measure of reserves, production, or economic value.")
        st.subheader("Selected projects and development context")
        st.dataframe(pd.DataFrame(PROJECT_DATA).drop(columns=["Source"]), use_container_width=True, hide_index=True)
        for item in PROJECT_DATA:
            st.markdown(f"- [{item['Project']} project reference]({item['Source']})")
        st.subheader("Provincial governance and legal context")
        st.markdown("Mining regulation in Pakistan involves constitutional provisions, provincial legislation, federal responsibilities, and project-specific agreements. Do not assume a single blanket rule applies to every mineral, offshore resource, lease, or concession.")
        st.markdown("**Review checklist:** constitutional provision cited; relevant provincial statute and amendments; licensing authority; lease/concession document; environmental approvals; community consultation; water use and mine drainage; royalties and revenue-sharing; court status; date of latest update.")
        st.info("The 18th Amendment and Article 172(3) are included as research prompts, not a substitute for legal advice. Confirm the constitutional text and the mineral/resource category with authoritative legal sources.")
        st.subheader("Investment forum note")
        st.write("The project brief identifies Pakistan Minerals Investment Forum (PMIF) 2026 as scheduled for 12–13 November 2026 in Islamabad. Treat the date, venue, attendance estimates, export targets, and raw-mineral export-policy claims as provisional until confirmed by an official event or government notice.")
    with tab_f:
        st.subheader("Regional dry-fruit and dates value chains")
        fruit_df = pd.DataFrame(FRUIT_DATA)
        fprov = st.selectbox("Region filter", ["All"] + sorted(fruit_df["Province / territory"].unique().tolist()), key="fruit_province")
        fsearch = st.text_input("Search fruit, hub, or processing opportunity", key="fruit_search")
        if fprov != "All": fruit_df = fruit_df[fruit_df["Province / territory"] == fprov]
        if fsearch.strip(): fruit_df = fruit_df[fruit_df.astype(str).apply(lambda c: c.str.contains(fsearch.strip(), case=False, na=False)).any(axis=1)]
        st.dataframe(fruit_df, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(pd.DataFrame(FRUIT_DATA).groupby("Province / territory", as_index=False).size().rename(columns={"size":"Listed product chains"}), x="Province / territory", y="Listed product chains", title="Illustrative product chains by region"), use_container_width=True)
        st.caption("Product/region listings are qualitative and not production rankings.")
        st.subheader("Climate resilience and post-harvest priorities")
        st.markdown("- Covered, food-safe drying and controlled moisture levels\n- Sorting, grading, traceability, hygienic storage, and packaging\n- Testing for aflatoxins, pesticide residues, and other market-specific requirements\n- Orchard water-efficiency, drought and frost monitoring, and climate-resilient varieties\n- Sustainable harvesting and ecosystem safeguards for forest-linked products such as pine nuts")
    with tab_trade:
        st.subheader("Trade figures supplied in the project brief")
        st.write("The values below are reported in the user's source notes and should be reconciled with the relevant HS codes, year, and official trade datasets before publication.")
        trade = pd.DataFrame([
            {"Trade category":"Dried fruits (excluding separately reported dates where classification permits)","Reported year":2024,"Reported export value (USD)":5940000,"Verification status":"Needs HS-code and source validation"},
            {"Trade category":"Dates", "Reported year":2024,"Reported export value (USD)":53000000,"Verification status":"Separate category; verify against TDAP / trade dataset"},
        ])
        st.dataframe(trade, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(trade, x="Trade category", y="Reported export value (USD)", color="Trade category", title="Reported export values — provisional figures", hover_data=["Reported year","Verification status"]), use_container_width=True)
        st.subheader("Export compliance checklist")
        checks = [
            "Confirm HS code, destination market, and current customs tariff treatment",
            "Check export duties/taxes and any exemptions in the current FBR tariff and rules",
            "Verify SPS, pesticide-residue and maximum-residue-limit requirements for destination market",
            "Use accredited laboratory testing and document aflatoxin / microbiological controls where relevant",
            "Maintain traceability, batch records, packaging and phytosanitary documentation",
            "Recheck tariff rates for imported raw nuts; rates may vary by HS code, origin, concession and current SRO",
        ]
        for c in checks: st.checkbox(c, key="tradecheck_" + str(checks.index(c)))
        st.info("Do not treat headline customs-duty, regulatory-duty, or sales-tax percentages as universally applicable; tariff treatment depends on the exact HS line, origin, trade regime, and current notifications.")
        st.download_button("Download sector tables (CSV)", pd.concat([pd.DataFrame(MINERAL_DATA).assign(dataset="Mining"), pd.DataFrame(FRUIT_DATA).assign(dataset="Dry fruit")], ignore_index=True, sort=False).to_csv(index=False).encode("utf-8"), "pakistan_mining_dry_fruit_sector_tables.csv", "text/csv")
    with tab_sources:
        st.subheader("Supporting sources")
        for title, url in SOURCE_LINKS:
            st.markdown(f"- [{title}]({url})")
        st.markdown("### How to interpret this page")
        st.markdown("- **Official source:** government, regulator, court, or project owner publication.\n- **Reported figure:** secondary reporting or user-supplied value requiring reconciliation.\n- **Indicative profile:** qualitative description for exploration, not an official statistical estimate.\n- **Legal status:** confirm current court orders, legislation, amendments, and notifications before relying on a summary.")
