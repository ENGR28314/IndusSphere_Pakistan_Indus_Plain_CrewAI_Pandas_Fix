"""Evidence-led strategic water security, flood response and agricultural water module.

The module distinguishes dated official statements and reporting from claims supplied
by the project owner that still require primary-source verification.
"""
import pandas as pd
import streamlit as st

SOURCES = [
    {"title": "Pakistan Ministry of Planning — ministerial remarks on water security (25 Aug 2026)", "url": "https://pc.gov.pk/web/press/get_press/1736", "type": "Official statement", "date": "2026-08-25"},
    {"title": "Radio Pakistan — Corps Commanders' Conference on Pakistan's water rights (6 Jul 2026)", "url": "https://www.radio.gov.pk/06-07-2026/corps-commanders-vow-to-safeguard-pakistans-water-rights", "type": "Official reporting of military statement", "date": "2026-07-06"},
    {"title": "Pakistan Ministry of Foreign Affairs — IWT and water security address (30 Jun 2026)", "url": "https://mofa.gov.pk/press-releases/deputy-prime-ministerforeign-ministers-address-at-international-seminar-on-iwt-an-instrument-of-peace-and-regional-stability-at-jinnah-convention-center-in-islamabad-30-june-2026", "type": "Official statement", "date": "2026-06-30"},
    {"title": "SIFC — Agriculture & Livestock / Green Pakistan Initiative", "url": "https://www.sifc.gov.pk/agricuture-sector", "type": "Official programme page", "date": "Accessed 2026-10-21"},
    {"title": "Radio Pakistan — LIMS and modern irrigation approaches (3 Jul 2024)", "url": "https://www.radio.gov.pk/03-07-2024/sifc-takes-steps-to-revolutionize-country-s-economy", "type": "Official reporting", "date": "2024-07-03"},
    {"title": "Radio Pakistan — Green Pakistan Initiative and satellite crop monitoring (21 Jun 2025)", "url": "https://www.radio.gov.pk/21-06-2025/green-pakistan-initiative-boosts-sustainable-agri-livestock-growth", "type": "Official reporting", "date": "2025-06-21"},
    {"title": "Radio Pakistan — Pakistan Army flood rescue and relief (2 Sep 2022)", "url": "https://www.radio.gov.pk/02-09-2022/pakistan-army-continuing-rescue-relief-operations-in-flood-ravaged-areas-of-country", "type": "Official reporting", "date": "2022-09-02"},
    {"title": "Dawn — Sindh High Court stays IRSA water certificate (7 Apr 2025)", "url": "https://www.dawn.com/news/1902784", "type": "Court reporting", "date": "2025-04-07"},
    {"title": "Dawn — Punjab government to revisit Cholistan land transfer (27 Feb 2025)", "url": "https://www.dawn.com/news/amp/1894561", "type": "Court reporting", "date": "2025-02-27"},
    {"title": "UN Treaty Series — Indus Waters Treaty (1960)", "url": "https://treaties.un.org/doc/Publication/UNTS/Volume%20419/v419.pdf", "type": "Primary treaty text", "date": "1960"},
]

CLAIMS = [
    {"Topic":"Army / IWT stance", "Claim or figure":"Corps Commanders' Conference reaffirmed commitment to measures to ensure Pakistan's rightful water share", "Evidence status":"Documented official statement", "Handling":"Attribute to the conference; do not present as an independent legal finding.", "Source":"2026-07-06 official reporting"},
    {"Topic":"Flood response", "Claim or figure":"Army rescue, evacuation, relief camps and medical support during 2022 floods", "Evidence status":"Documented dated reporting", "Handling":"Keep dates and figures tied to the cited report; do not imply current operating numbers.", "Source":"Radio Pakistan / ISPR reporting, 2022"},
    {"Topic":"Flood engineering", "Claim or figure":"Engineer-in-Chief / FFC joint pre-flood structural audits, pre-positioned breaching teams and emergency stocks", "Evidence status":"Needs primary-source verification", "Handling":"Do not publish operational details as verified without FFC/NDMA/official engineering documentation.", "Source":"No primary document attached to the supplied claim"},
    {"Topic":"Drinking water", "Claim or figure":"Frontier Corps/local engineering units install solar water schemes and filtration plants in Balochistan/Chagai", "Evidence status":"Needs project-level verification", "Handling":"Add project name, location, commissioning date, capacity and implementing agency before counting outcomes.", "Source":"Project-level source needed"},
    {"Topic":"LIMS / GPI", "Claim or figure":"Satellite crop monitoring and modern irrigation methods promoted under GPI/SIFC", "Evidence status":"Official programme reporting exists", "Handling":"Describe programme aims separately from independently measured water savings.", "Source":"SIFC / Radio Pakistan links"},
    {"Topic":"Water use", "Claim or figure":"Agriculture uses 93% of water; 60% is lost; pivot irrigation saves 25%", "Evidence status":"Figures need definitions and primary citations", "Handling":"Require a specified denominator, location, baseline, method and study year; do not show as measured national facts.", "Source":"Not independently established by the supplied text"},
    {"Topic":"Investment / land", "Claim or figure":"4.4 million acres, 52,000 acres in Sindh, 50,000 acres in Cholistan, 40-40-20 profit split, Gulf investment figures", "Evidence status":"Project-specific claims require document checks", "Handling":"Verify each claim against executed agreements, official investment disclosures and dated land notifications.", "Source":"Agreements / official project documents needed"},
    {"Topic":"Canal disputes", "Claim or figure":"Sindh High Court stayed the IRSA water-availability certificate for Cholistan/Thal canals in April 2025", "Evidence status":"Dated court reporting located", "Handling":"This is a historical procedural snapshot, not a statement of the current case status; check latest court orders before operational use.", "Source":"Dawn, 7 Apr 2025"},
    {"Topic":"Land litigation", "Claim or figure":"Punjab government told LHC it had held two caretaker-era land-transfer agreements in abeyance pending cabinet review", "Evidence status":"Dated court reporting located", "Handling":"State the date and procedural posture; do not infer the final legal outcome.", "Source":"Dawn, 27 Feb 2025"},
    {"Topic":"Leaked directives / media control", "Claim or figure":"Alleged military media directives or leaked strategic instructions", "Evidence status":"Unverified allegation in supplied text", "Handling":"Exclude from factual narrative unless authenticated documents and credible corroboration are supplied.", "Source":"No authenticated source supplied"},
]


def _links(items):
    for item in items:
        st.markdown(f"- [{item['title']}]({item['url']}) — *{item['type']}* ({item['date']})")


def render_water_security_page():
    st.title("🛡️ Strategic Water Security, Flood Response & Agricultural Water Governance")
    st.caption("IndusSphere Pakistan · Research and decision-support module · Evidence reviewed through 21 October 2026")
    st.info("Evidence rule: official statements are attributed to the issuing institution; media reports are labelled as reporting; contested claims and project-owner-supplied figures are flagged for verification. This page is not a legal opinion or an operational flood-response plan.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Strategic water security & IWT", "Flood engineering & relief", "SIFC / LIMS / irrigation", "Land, canals & legal review", "Evidence register & sources"
    ])

    with tab1:
        st.subheader("Pakistan's stated strategic water-security position")
        st.write("Pakistan's official position is that the Indus Waters Treaty (IWT) remains binding and that the country's treaty-based water rights must be protected. In a report dated 6 July 2026, Radio Pakistan reported that the Corps Commanders' Conference reaffirmed its commitment to take measures to ensure Pakistan's rightful share of water, referencing the NSC directive of 24 April 2025.")
        st.markdown("**How to interpret this:** this is an attributed statement of Pakistan's national-security position, not an independent adjudication of treaty interpretation or the status of individual infrastructure projects.")
        st.markdown("#### Treaty and technical context")
        st.markdown("- Western Rivers: Indus, Jhelum and Chenab. Use the IWT text and formal institutional records for the precise obligations that apply to data exchange, projects and dispute resolution.")
        st.markdown("- Distinguish official Pakistani statements, Indian statements, treaty text, court/arbitral decisions, and hydrological observations in the evidence ledger.")
        st.markdown("- Flow-disruption scenarios should be tested with measured discharge, reservoir-operation records, rainfall, withdrawals and uncertainty ranges—not inferred from project capacity alone.")
        st.markdown("#### Selected references")
        _links([SOURCES[0], SOURCES[1], SOURCES[2], SOURCES[9]])
        with st.expander("Show the supplied deterrence claim and its evidence handling"):
            st.write("The supplied narrative says unilateral stopping or diversion of Pakistan's allocated flows would be treated as a grave national-security threat. The module records the documented official wording as an attributed policy statement; it does not add tactical or speculative descriptions of military countermeasures.")

    with tab2:
        st.subheader("Flood engineering, rescue and recovery")
        st.write("Pakistan Army participation in flood relief is documented in dated public reporting. For example, Radio Pakistan's 2 September 2022 report described evacuation, delivery of relief supplies and operation of relief camps during the 2022 flood emergency.")
        st.markdown("#### Disaster-management lifecycle")
        st.dataframe(pd.DataFrame([
            {"Phase":"Preparedness", "Typical civil-agency interface":"Forecasting, flood plans, infrastructure inspection and contingency coordination", "Evidence note":"Confirm each responsible agency and procedure against current FFC / NDMA / provincial plans."},
            {"Phase":"Response", "Typical support reported":"Evacuation, relief distribution, medical assistance and temporary access", "Evidence note":"Use dated official releases for numbers and locations."},
            {"Phase":"Recovery", "Typical engineering needs":"Access restoration, drainage, embankment repair and damage assessment", "Evidence note":"Do not assume every activity is Army-led; identify the actual lead agency and contractor."},
        ]), use_container_width=True, hide_index=True)
        st.markdown("#### Reported 2022 response source")
        _links([SOURCES[6]])
        st.warning("The supplied descriptions of controlled breaching sections, explosive pre-positioning and emergency stocks are not reproduced as operational instructions. Their institutional roles and procedures should be verified from current official flood-management documents before inclusion as facts.")

    with tab3:
        st.subheader("SIFC, Green Pakistan Initiative and LIMS")
        st.write("The SIFC's public agriculture-sector page describes the Green Pakistan Initiative and modernized agriculture as programme priorities. Radio Pakistan has also reported satellite crop monitoring and the promotion of drip, sprinkler and pivot irrigation. These sources establish stated programme activities and aims; they do not, by themselves, prove a specific national water-saving percentage.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Programme elements described in public sources**")
            st.markdown("- Satellite / remote-sensing crop monitoring")
            st.markdown("- Modern irrigation options: drip, sprinkler and pivot")
            st.markdown("- Farmer information and agricultural modernization")
            st.markdown("- Investment facilitation and farm development")
        with c2:
            st.markdown("**Indicators to collect for impact evaluation**")
            st.markdown("- Baseline and post-project water withdrawal (m³/ha)")
            st.markdown("- Crop yield and water productivity (kg/m³)")
            st.markdown("- Groundwater level and salinity trends")
            st.markdown("- Energy use, farm area and crop type")
        st.markdown("#### Official programme references")
        _links([SOURCES[3], SOURCES[4], SOURCES[5]])
        st.markdown("#### User-supplied figures needing verification")
        figdata = pd.DataFrame([
            {"Indicator":"Agriculture share of water use", "Reported value":"93%", "Status":"Verify denominator, year and source"},
            {"Indicator":"Water loss under conventional methods", "Reported value":"60%", "Status":"Verify whether this means field application, conveyance, or basin-scale depletion"},
            {"Indicator":"Center-pivot saving target", "Reported value":"25%", "Status":"Treat as a claimed target until a comparative study is cited"},
            {"Indicator":"Land identified for possible development", "Reported value":"4.4 million acres", "Status":"Programme-reported figure; verify current scope and land status"},
        ])
        st.dataframe(figdata, use_container_width=True, hide_index=True)
        st.caption("These figures are shown as claims supplied for research, not as independently measured or universally applicable values.")

    with tab4:
        st.subheader("Corporate farming, land review and inter-provincial water concerns")
        st.write("The supplied material raises questions about proposed canal transfers, corporate farming, public-land agreements, groundwater sustainability, local livelihoods and provincial water-sharing arrangements. These are distinct issues and should be assessed with separate legal, hydrological, environmental and socioeconomic evidence.")
        st.markdown("#### Dated procedural snapshots found in reporting")
        st.dataframe(pd.DataFrame([
            {"Date":"7 April 2025", "Issue":"IRSA water-availability certificate for Cholistan / Thal canals", "Reported procedural status":"Sindh High Court stayed / restrained action on the certificate in proceedings reported that day", "Caution":"Not a verified current status; check latest court docket and subsequent orders."},
            {"Date":"27 February 2025", "Issue":"Cholistan land-transfer agreements", "Reported procedural status":"Punjab officials told the LHC that two caretaker-era agreements had been held in abeyance pending cabinet review", "Caution":"This report does not establish the final legality or final outcome of the review."},
        ]), use_container_width=True, hide_index=True)
        _links([SOURCES[7], SOURCES[8]])
        st.markdown("#### Recommended impact-screening fields")
        st.dataframe(pd.DataFrame([
            {"Assessment area":"Hydrology", "Fields":"Monthly available flow, existing allocations, drought years, environmental flows, return flows"},
            {"Assessment area":"Provincial equity", "Fields":"Province-wise allocations, canal head/tail delivery, seasonal shortages, dispute-resolution record"},
            {"Assessment area":"Groundwater", "Fields":"Water-table trend, salinity, pumping energy, recharge and abstraction limits"},
            {"Assessment area":"Community / land", "Fields":"Land tenure, consultation, displacement risk, local employment and grievance mechanism"},
            {"Assessment area":"Environmental", "Fields":"Desert ecology, wetlands, delta flows, soil salinity, sandstorms and climate exposure"},
            {"Assessment area":"Legal", "Fields":"Executed agreements, notifications, court orders, IRSA/CCI decisions and current procedural status"},
        ]), use_container_width=True, hide_index=True)
        st.warning("Legal cases and water-allocation disputes evolve. The dated reporting above must not be treated as a current legal ruling without checking the latest primary court documents.")

    with tab5:
        st.subheader("Claim-by-claim evidence register")
        st.write("Use the search box to filter claims. The register separates sourced reporting from claims that need primary documents or independent measurement.")
        claims = pd.DataFrame(CLAIMS)
        q = st.text_input("Filter evidence register", placeholder="e.g. LIMS, 93%, land, media directives", key="water_security_claim_filter")
        if q.strip():
            mask = claims.astype(str).apply(lambda col: col.str.contains(q.strip(), case=False, na=False)).any(axis=1)
            claims = claims[mask]
        st.dataframe(claims, use_container_width=True, hide_index=True)
        st.markdown("#### Sources")
        _links(SOURCES)
        st.download_button("Download evidence register (CSV)", pd.DataFrame(CLAIMS).to_csv(index=False).encode("utf-8"), "indussphere_water_security_evidence_register.csv", "text/csv")
        st.caption("Last source review date in this project module: 21 October 2026. Verify each source and update dates before formal policy, legal or engineering use.")
