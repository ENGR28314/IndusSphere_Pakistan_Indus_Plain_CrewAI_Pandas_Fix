"""CrewAI-powered agentic workflow for IndusSphere Pakistan.

The crew provides decision-support drafts, not autonomous operational control.
No external actions are taken; users review outputs before acting.
"""
from __future__ import annotations
import os
import streamlit as st


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)


def _patch_groq_cache_breakpoint() -> None:
    """Strip CrewAI's Anthropic-only cache_breakpoint from Groq payloads."""
    import copy
    import sys
    import litellm

    def strip(value):
        if isinstance(value, dict):
            value.pop("cache_breakpoint", None)
            for child in list(value.values()):
                strip(child)
        elif isinstance(value, list):
            for child in value:
                strip(child)
        return value

    original = getattr(litellm, "completion", None)
    if original is None:
        raise RuntimeError("LiteLLM completion API unavailable; install crewai[litellm].")
    if getattr(original, "_indussphere_cache_breakpoint_patch", False):
        return

    def completion_without_groq_cache_marker(*args, **kwargs):
        model = str(kwargs.get("model", args[0] if args else ""))
        api_base = str(kwargs.get("api_base", kwargs.get("base_url", "")))
        if model.startswith("groq/") or "api.groq.com" in api_base.lower():
            kwargs = dict(kwargs)
            kwargs["caching"] = False
            if "messages" in kwargs:
                kwargs["messages"] = strip(copy.deepcopy(kwargs["messages"]))
            elif len(args) > 1:
                args = list(args)
                args[1] = strip(copy.deepcopy(args[1]))
                args = tuple(args)
        return original(*args, **kwargs)

    completion_without_groq_cache_marker._indussphere_cache_breakpoint_patch = True
    litellm.completion = completion_without_groq_cache_marker
    try:
        import litellm.main as litellm_main
        if getattr(litellm_main, "completion", None) is original:
            litellm_main.completion = completion_without_groq_cache_marker
    except Exception:
        pass
    for module_name, module in tuple(sys.modules.items()):
        if module is None or not (module_name.startswith("crewai.") or module_name.startswith("litellm.")):
            continue
        try:
            if getattr(module, "completion", None) is original:
                setattr(module, "completion", completion_without_groq_cache_marker)
        except Exception:
            pass
    try:
        import crewai.llms.cache as crewai_cache
        crewai_cache.mark_cache_breakpoint = lambda message: message
        for module_name, module in tuple(sys.modules.items()):
            if module is not None and module_name.startswith("crewai."):
                try:
                    if getattr(module, "mark_cache_breakpoint", None) is not None:
                        setattr(module, "mark_cache_breakpoint", lambda message: message)
                except Exception:
                    pass
    except Exception:
        pass


def _build_llm(provider: str, api_key: str, model: str):
    from crewai import LLM
    if provider == "Groq":
        return LLM(
            model=f"groq/{model}",
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.2,
        )
    return LLM(model=f"openai/{model}", api_key=api_key, temperature=0.2)


# Sector playbooks guide the agents toward the relevant analysis without
# pretending that the dashboard has supplied measurements or verified sources.
SECTOR_PLAYBOOKS = {
    "Integrated water resources and basin hydrology": {
        "focus": "basin water balance, river flows, reservoir operations, allocations, environmental flows, seasonal variability, and upstream/downstream dependencies",
        "indicators": "inflow/outflow time series, discharge and volume units, storage and release records, water balance closure error, seasonal supply-demand gap, gauge coverage, and data period",
        "deliverables": "basin/system boundary; water-balance table specification; seasonal and scenario assessment; upstream/downstream effects; monitoring and data-quality plan",
        "cautions": "Do not invent river flows, reservoir releases, allocations, or current storage. Distinguish measured, modelled, illustrative, and missing values.",
    },
    "Irrigation, canals and groundwater": {
        "focus": "crop water demand, canal delivery and conveyance, groundwater levels and abstraction, recharge, irrigation equity, and farm-level adaptation",
        "indicators": "crop area and crop coefficient (Kc), reference evapotranspiration, effective rainfall, delivery efficiency, groundwater depth trend, pumping/energy cost, and supply-demand deficit",
        "deliverables": "crop/season demand method; canal and groundwater evidence gaps; basin/district comparison plan; adaptation options; calibrated-model and field-validation checklist",
        "cautions": "Do not call groundwater sustainable from a simple trend threshold alone. Require aquifer properties, recharge estimates, abstraction records, calibration, and uncertainty bounds.",
    },
    "Floods, flash floods and disaster risk": {
        "focus": "riverine and pluvial flooding, hill torrents, flash floods, cloudbursts, landslides/mudflows, exposure, warning lead time, and response capacity",
        "indicators": "rainfall intensity/duration, observed and modelled discharge, return period only when derived, inundation depth/extent, exposed people/assets, warning lead time, and event date/source",
        "deliverables": "hazard-exposure-vulnerability separation; scenario and trigger table; evacuation/communications considerations; infrastructure and community mitigation; validation checklist",
        "cautions": "Do not issue operational alerts or infer return periods from one event. Mark hazard maps and trigger thresholds as provisional until calibrated and approved by authorities.",
    },
    "Climate change and climate scenarios": {
        "focus": "historical climate baselines, CMIP6 ensemble selection, downscaling/bias correction, heat, drought, precipitation extremes, and adaptation pathways",
        "indicators": "baseline period, model IDs, scenario pathway, precipitation/temperature/PET, bias-correction method, ensemble spread, extreme-event indices, and validation metrics",
        "deliverables": "baseline and future-scenario matrix; model-selection rationale; uncertainty range; sector impacts; adaptation options and monitoring plan",
        "cautions": "Do not equate RCP and SSP pathways without explanation or treat ensemble means as a full representation of extremes. State model and time-period limitations.",
    },
    "Terrain, geology and landslide susceptibility": {
        "focus": "mountain ranges, elevation/slope/aspect, lithology, faults where evidenced, erosion, landslide susceptibility, accessibility, and terrain constraints",
        "indicators": "DEM resolution/source, slope units, geology map scale, land cover, rainfall triggers, known inventory dates, susceptibility validation, and positional uncertainty",
        "deliverables": "terrain constraints; susceptibility-factor inventory; field-check plan; infrastructure/tourism implications; limitations of mapping scale",
        "cautions": "Do not label susceptibility as a deterministic prediction or claim a site is safe based on a map alone. Require field and qualified geotechnical review for site-specific decisions.",
    },
    "Agriculture, crops and food security": {
        "focus": "Rabi/Kharif crop patterns, yields, irrigation reliability, soil constraints, food availability/access, climate exposure, and farm livelihoods",
        "indicators": "crop area, production, yield (with units/year), irrigation source, crop calendar, prices if sourced, food-security measure, and district/province coverage",
        "deliverables": "crop-season baseline; water/climate stress pathways; vulnerable groups; feasible adaptation options; data and validation needs",
        "cautions": "Do not fabricate production, price, or yield statistics. Distinguish food availability from affordability, access, nutrition, and stability.",
    },
    "Livestock, apiculture and aquaculture": {
        "focus": "livestock water/feed/heat stress, veterinary access, honey production, fisheries/aquaculture water quality, cold chains, and rural livelihoods",
        "indicators": "stock/production and units, season, mortality or disease data if provided, water quality, feed availability, market access, and survey coverage",
        "deliverables": "subsector baseline; climate/water dependencies; livelihood and market risks; feasible interventions; monitoring requirements",
        "cautions": "Do not infer animal health, production volumes, or water suitability without observations and appropriate specialist assessment.",
    },
    "Soils, water quality and wastewater": {
        "focus": "surface/groundwater quality, salinity/sodicity, nutrients, pathogens, industrial effluent, treatment performance, reuse suitability, and receiving-water effects",
        "indicators": "pH, EC/TDS, DO, BOD/COD, turbidity, nutrients, microbial indicators, sampling date/location, analytical method, standards version, and detection limits",
        "deliverables": "parameter-by-parameter assessment; source/pathway/receptor analysis; treatment and monitoring options; standards comparison only when jurisdiction and version are known",
        "cautions": "Do not infer potability or regulatory compliance from incomplete parameters. Separate screening from accredited laboratory confirmation and applicable standard requirements.",
    },
    "Forests, biodiversity and ecosystem services": {
        "focus": "forest cover, habitat connectivity, biodiversity pressures, watershed services, degradation, restoration, and protected-area/community considerations",
        "indicators": "land-cover year/resolution, area units, classification accuracy, species/source provenance, fragmentation, restoration survival, and ecosystem-service assumptions",
        "deliverables": "baseline and pressure pathways; conservation/restoration options; co-benefits and trade-offs; monitoring indicators; stakeholder and land-tenure questions",
        "cautions": "Do not claim species presence, area change, or biodiversity outcomes without traceable survey or geospatial evidence.",
    },
    "Mining and mineral resources": {
        "focus": "mineral occurrence versus reserves/resources, extraction, water/energy use, tailings, acid drainage, dust, worker/community safety, transport, and closure planning",
        "indicators": "resource classification and reporting date, production units, water intensity, waste/tailings characteristics, emissions, permits, rehabilitation liabilities, and source provenance",
        "deliverables": "resource-data quality review; lifecycle risks; water/energy dependencies; safeguards and monitoring; closure/rehabilitation considerations",
        "cautions": "Do not present speculative in-ground wealth as recoverable value or verified reserves. Separate exploration estimates, reported resources, reserves, and actual production.",
    },
    "Dry fruit and mountain value chains": {
        "focus": "orchards and wild-harvest sources, seasonal production, water needs, post-harvest losses, processing, storage, transport, market access, and livelihoods",
        "indicators": "crop/product, harvest season, production unit/year, source location, quality grade, loss rate, storage conditions, market price/source/date, and employment evidence",
        "deliverables": "value-chain map; climate/water and logistics bottlenecks; value-addition options; smallholder inclusion; data collection plan",
        "cautions": "Do not invent production, export, price, or employment figures. Identify whether values are measured, reported, or illustrative.",
    },
    "Energy, hydropower and solar": {
        "focus": "generation, seasonal hydrology, installed versus operational capacity, grid access, solar resource, reliability, environmental/social impacts, and project status",
        "indicators": "MW versus MWh, capacity factor basis, commissioning/status date, generation series, water-release dependency, grid constraints, and source",
        "deliverables": "energy baseline; seasonal and climate dependencies; project-status distinctions; alternatives and safeguards; data validation plan",
        "cautions": "Do not equate installed capacity with actual generation or treat proposed/under-construction projects as operational. Verify dates and source documents.",
    },
    "Transport, telecom and critical infrastructure": {
        "focus": "roads, bridges, communication networks, power/water assets, hazard exposure, redundancy, service continuity, access, and maintenance",
        "indicators": "asset inventory/date, location accuracy, condition, hazard exposure, criticality, outage duration, redundancy, population served, and inspection status",
        "deliverables": "asset-risk register; dependencies and cascading failure pathways; resilience measures; continuity plan; inspection/engineering review checklist",
        "cautions": "Do not assert asset condition or failure probability without inspection/records. Avoid disclosing sensitive security details; require qualified engineering assessment.",
    },
    "Urban growth, housing and municipal services": {
        "focus": "urban expansion, drainage, water supply, wastewater, solid waste, heat, land-use pressure, service access, and climate resilience",
        "indicators": "population year/source, built-up area and resolution, service coverage, demand/supply basis, flood exposure, heat metrics, and infrastructure capacity",
        "deliverables": "urban service baseline; spatial growth scenarios; vulnerable-neighbourhood considerations; investment options; governance and monitoring plan",
        "cautions": "Do not treat modelled urban boundaries or population projections as observations. Respect privacy and resolution limits in household data.",
    },
    "Socio-economic development and employment": {
        "focus": "poverty, employment, livelihoods, distributional impacts, rural/urban differences, gender and inclusion where evidence supports it, and access to services",
        "indicators": "survey/year, sample and geographic resolution, income/employment definitions, price basis, missingness, uncertainty, and disaggregation limits",
        "deliverables": "who benefits/who bears costs; distributional pathways; data-quality assessment; safeguards; monitoring and consultation plan",
        "cautions": "Do not infer individual or household conditions from district averages. Do not expose confidential microdata or fabricate demographic breakdowns.",
    },
    "IWT, water diplomacy and legal-policy evidence": {
        "focus": "treaty text and annexes, institutional roles, procedural chronology, technical data exchange, party positions, and evidence-based policy options",
        "indicators": "document title/date/article or annex, primary versus secondary source, procedural status/date, attributed position, and unresolved factual question",
        "deliverables": "verified chronology from supplied evidence; legal text versus party interpretation; technical questions; evidence gaps; neutral options and verification matrix",
        "cautions": "Do not present legal conclusions as settled advice. Attribute positions, distinguish fact from allegation/interpretation, and request qualified legal review.",
    },
    "Environmental, ESG and SDG assessment": {
        "focus": "environmental and social risks, governance, materiality, stakeholder impacts, safeguards, SDG alignment, indicators, and reporting boundaries",
        "indicators": "indicator definition, baseline/year, unit, scope, data owner, methodology, target, evidence quality, and reporting standard/version",
        "deliverables": "material issues; impacts/risks/opportunities; SDG mapping with rationale; mitigation hierarchy; KPI register; disclosure gaps",
        "cautions": "Do not claim certification, compliance, or SDG achievement without auditable evidence. Separate commitments, activities, outputs, and measured outcomes.",
    },
    "Disaster resilience and emergency preparedness": {
        "focus": "multi-hazard preparedness, early-warning communication, response capacity, critical-service continuity, recovery, and vulnerable populations",
        "indicators": "hazard source/date, lead time, warning reach, evacuation capacity, shelter/service access, response resources, and after-action evidence",
        "deliverables": "preparedness gap assessment; roles and communication pathways; scenario exercises; continuity and recovery actions; verification checklist",
        "cautions": "This is planning support, not an official warning or emergency instruction. Follow competent authorities and validated local protocols.",
    },
    "Governance, institutions and public investment": {
        "focus": "mandates, coordination, budgets, procurement, data stewardship, accountability, implementation capacity, and monitoring/evaluation",
        "indicators": "mandate/source, budget year, expenditure basis, procurement status, responsible entity, milestones, output/outcome measures, and audit trail",
        "deliverables": "institutional responsibility matrix; implementation dependencies; procurement and transparency risks; milestones; monitoring framework",
        "cautions": "Do not infer misconduct or legal compliance from incomplete records. Distinguish announced, budgeted, contracted, spent, and completed activities.",
    },
    "Tourism, recreation and mountain safety": {
        "focus": "seasonality, access, carrying capacity, weather and terrain hazards, water/sanitation, ecosystem impacts, local livelihoods, and visitor safety",
        "indicators": "visitor data source/year, access season, hazard inventory, trail/site condition, service capacity, waste/water pressure, and incident records",
        "deliverables": "destination baseline; seasonal constraints; resilience and environmental measures; local benefit options; visitor-safety and monitoring needs",
        "cautions": "Do not claim a route/site is safe or open without current authoritative information. Require local operators and competent authorities for operational decisions.",
    },
    "Cross-sector integrated assessment": {
        "focus": "interdependencies across water, climate, terrain, hazards, food, energy, infrastructure, ecosystems, livelihoods, governance, and policy",
        "indicators": "shared baseline years/units, dependency links, common scenarios, distributional effects, uncertainty, and evidence provenance",
        "deliverables": "systems map; sector-by-sector findings; trade-off matrix; compound/cascading risks; ranked options with rationale; joint data and monitoring plan",
        "cautions": "Do not combine incompatible scales, periods, or units without explanation. Avoid double counting and make weights/value judgements explicit.",
    },
}


def _run_reporting_crew(provider: str, key: str, model: str, goal: str, context: str,
                       detail: str, selected_sectors: list[str], integrated: bool,
                       settings: dict | None = None) -> str:
    """Run one reviewed CrewAI report, for one sector or a multi-sector synthesis."""
    if provider == "Groq":
        _patch_groq_cache_breakpoint()
    from crewai import Agent, Crew, Process, Task

    llm = _build_llm(provider, key, model)
    playbook_blocks = []
    for sector in selected_sectors:
        pb = SECTOR_PLAYBOOKS[sector]
        playbook_blocks.append(
            f"SECTOR: {sector}\nFOCUS: {pb['focus']}\nINDICATORS: {pb['indicators']}\n"
            f"DELIVERABLES: {pb['deliverables']}\nSAFEGUARDS: {pb['cautions']}"
        )
    settings = settings or {}
    mode = "INTEGRATED CROSS-SECTOR ASSESSMENT" if integrated else "SEPARATE SECTOR ASSESSMENT"
    setting_text = "\n".join(f"{k}: {v}" for k, v in settings.items()) or "No additional controls selected."
    user_brief = (
        f"REPORTING MODE: {mode}\nSELECTED SECTORS: {', '.join(selected_sectors)}\n"
        f"DEPTH: {detail}\nUSER GOAL: {goal.strip()}\nANALYSIS SETTINGS:\n{setting_text}\n\nSECTOR PLAYBOOKS:\n"
        + "\n\n".join(playbook_blocks)
        + "\n\nSUPPLIED CONTEXT / EVIDENCE:\n"
        + (context.strip() or "No additional context supplied.")
        + "\n\nEVIDENCE RULES: For each quantitative claim state value, unit, period, geography, "
          "source/provenance, and whether observed, modelled, user-supplied, illustrative, or unavailable. "
          "Never fabricate citations, datasets, measurements, project status, legal provisions, or numerical results. "
          "Clearly separate supplied evidence, general knowledge, inference, assumptions, and missing data."
    )

    planner = Agent(
        role="Planning and Evidence Coordination Agent",
        goal="Decompose the request, map evidence and gaps, and establish a defensible analysis plan across the selected sectors.",
        backstory="You are a careful interdisciplinary decision-support planner. You do not claim live research or invent sources.",
        llm=llm, verbose=False, allow_delegation=False,
    )
    analyst_role = "Integrated Systems Analyst" if integrated else f"{selected_sectors[0]} Technical Analyst"
    analyst_goal = (
        "Analyze cross-sector dependencies, shared drivers, cumulative and cascading risks, competing demands, "
        "trade-offs, synergies, and coordinated options. Avoid double counting and explain incompatible scales or periods."
        if integrated else
        "Develop a sector-specific technical assessment, indicators, options, implementation considerations, and limitations."
    )
    analyst = Agent(
        role=analyst_role,
        goal=analyst_goal,
        backstory="You are an evidence-conscious systems-thinking analyst. State assumptions, units and provenance; do not present illustrative values as measured facts.",
        llm=llm, verbose=False, allow_delegation=False,
    )
    reviewer = Agent(
        role="Independent Risk, Evidence and Quality Reviewer",
        goal="Challenge unsupported claims, identify uncertainty and omissions, and produce a prioritized verification checklist.",
        backstory="You distinguish evidence from interpretation. For legal and treaty matters, separate text, attributed positions and analysis. Require qualified review for safety-critical engineering.",
        llm=llm, verbose=False, allow_delegation=False,
    )
    plan_task = Task(
        description=("Prepare a plan, objectives, evidence inventory, missing data, assumptions to avoid, "
                     "and analysis sequence.\n\n" + user_brief),
        expected_output="Analysis plan, evidence inventory, gaps and method sequence.", agent=planner,
    )
    analysis_task = Task(
        description=("Prepare the technical assessment using the plan and supplied brief. For integrated mode, "
                     "explicitly analyze sector interfaces and cumulative/cascading effects. For separate mode, "
                     "stay focused on the selected sector. Include findings, options and limitations.\n\n" + user_brief),
        expected_output="Structured assessment with evidence labels, analysis, options and limitations.",
        agent=analyst, context=[plan_task],
    )
    review_task = Task(
        description=("Independently review the plan and analysis. Include these report sections: Executive Summary; "
                     "Scope and Evidence Basis; Sector Baseline; Key Findings; Cross-Sector Linkages (where relevant); "
                     "Risks and Trade-offs; Options and Recommendations; Uncertainties; Data Needed; Monitoring Indicators; "
                     "Implementation Priorities; Verification Checklist. Mark unavailable information explicitly. "
                     "Do not imply that a model, field survey, calculation, legal review or source verification occurred "
                     "unless it actually did. Keep recommendations proportionate to evidence.\n\n" + user_brief),
        expected_output="Final reviewed Markdown report with provenance, uncertainties, data requirements and verification actions.",
        agent=reviewer, context=[plan_task, analysis_task],
    )
    crew = Crew(agents=[planner, analyst, reviewer], tasks=[plan_task, analysis_task, review_task],
                process=Process.sequential, verbose=False)
    return str(crew.kickoff())



# Task & Decision Library: one reusable task and decision set for every sector playbook.
SECTOR_TASK_LIBRARY = {'Integrated water resources and basin hydrology': {'task': 'Assess basin water balance, river flows, reservoir operations, allocations, environmental flows, seasonal variability, and upstream/downstream dependencies. Use the relevant indicators (inflow/outflow time series, discharge and volume units, storage and release records, water balance closure error, seasonal supply-demand gap, gauge coverage, and data period) where data are supplied, and follow the sector deliverables (basin/system boundary; water-balance table specification; seasonal and scenario assessment; upstream/downstream effects; monitoring and data-quality plan).', 'questions': ['How should basin water be allocated across competing uses while accounting for seasonal supply and environmental flows?', 'Which sub-basins or seasons show the strongest evidence of water stress?', 'Which monitoring, storage or demand-management interventions should be prioritised?'], 'outputs': 'basin/system boundary; water-balance table specification; seasonal and scenario assessment; upstream/downstream effects; monitoring and data-quality plan'}, 'Irrigation, canals and groundwater': {'task': 'Assess crop water demand, canal delivery and conveyance, groundwater levels and abstraction, recharge, irrigation equity, and farm-level adaptation. Use the relevant indicators (crop area and crop coefficient (Kc), reference evapotranspiration, effective rainfall, delivery efficiency, groundwater depth trend, pumping/energy cost, and supply-demand deficit) where data are supplied, and follow the sector deliverables (crop/season demand method; canal and groundwater evidence gaps; basin/district comparison plan; adaptation options; calibrated-model and field-validation checklist).', 'questions': ['Which canal commands and groundwater areas need priority efficiency or sustainability assessment?', 'How can crop-water demand be matched to seasonal surface-water and groundwater availability?', 'Which irrigation and recharge interventions merit further feasibility work?'], 'outputs': 'crop/season demand method; canal and groundwater evidence gaps; basin/district comparison plan; adaptation options; calibrated-model and field-validation checklist'}, 'Floods, flash floods and disaster risk': {'task': 'Assess riverine and pluvial flooding, hill torrents, flash floods, cloudbursts, landslides/mudflows, exposure, warning lead time, and response capacity. Use the relevant indicators (rainfall intensity/duration, observed and modelled discharge, return period only when derived, inundation depth/extent, exposed people/assets, warning lead time, and event date/source) where data are supplied, and follow the sector deliverables (hazard-exposure-vulnerability separation; scenario and trigger table; evacuation/communications considerations; infrastructure and community mitigation; validation checklist).', 'questions': ['Which exposed districts and assets require priority flood-risk reduction?', 'Where are early-warning, drainage or emergency-response gaps?', 'Which mitigation options are robust across the available hazard scenarios?'], 'outputs': 'hazard-exposure-vulnerability separation; scenario and trigger table; evacuation/communications considerations; infrastructure and community mitigation; validation checklist'}, 'Climate change and climate scenarios': {'task': 'Assess historical climate baselines, CMIP6 ensemble selection, downscaling/bias correction, heat, drought, precipitation extremes, and adaptation pathways. Use the relevant indicators (baseline period, model IDs, scenario pathway, precipitation/temperature/PET, bias-correction method, ensemble spread, extreme-event indices, and validation metrics) where data are supplied, and follow the sector deliverables (baseline and future-scenario matrix; model-selection rationale; uncertainty range; sector impacts; adaptation options and monitoring plan).', 'questions': ['Which regions and sectors appear most vulnerable under the supplied climate scenarios?', 'Which adaptation options remain useful across different climate assumptions?', 'What baseline, model and uncertainty information is needed before investment decisions?'], 'outputs': 'baseline and future-scenario matrix; model-selection rationale; uncertainty range; sector impacts; adaptation options and monitoring plan'}, 'Terrain, geology and landslide susceptibility': {'task': 'Assess mountain ranges, elevation/slope/aspect, lithology, faults where evidenced, erosion, landslide susceptibility, accessibility, and terrain constraints. Use the relevant indicators (DEM resolution/source, slope units, geology map scale, land cover, rainfall triggers, known inventory dates, susceptibility validation, and positional uncertainty) where data are supplied, and follow the sector deliverables (terrain constraints; susceptibility-factor inventory; field-check plan; infrastructure/tourism implications; limitations of mapping scale).', 'questions': ['Which corridors or sites require additional terrain or geotechnical investigation?', 'Where should landslide, erosion or slope monitoring be prioritised?', 'How should terrain constraints influence infrastructure and land-use planning?'], 'outputs': 'terrain constraints; susceptibility-factor inventory; field-check plan; infrastructure/tourism implications; limitations of mapping scale'}, 'Agriculture, crops and food security': {'task': 'Assess Rabi/Kharif crop patterns, yields, irrigation reliability, soil constraints, food availability/access, climate exposure, and farm livelihoods. Use the relevant indicators (crop area, production, yield (with units/year), irrigation source, crop calendar, prices if sourced, food-security measure, and district/province coverage) where data are supplied, and follow the sector deliverables (crop-season baseline; water/climate stress pathways; vulnerable groups; feasible adaptation options; data and validation needs).', 'questions': ['Which crop patterns are compatible with seasonal water and climate conditions?', 'Where do crop production, food access or livelihood vulnerabilities overlap?', 'Which agricultural adaptation investments offer the strongest evidence-based benefits?'], 'outputs': 'crop-season baseline; water/climate stress pathways; vulnerable groups; feasible adaptation options; data and validation needs'}, 'Livestock, apiculture and aquaculture': {'task': 'Assess livestock water/feed/heat stress, veterinary access, honey production, fisheries/aquaculture water quality, cold chains, and rural livelihoods. Use the relevant indicators (stock/production and units, season, mortality or disease data if provided, water quality, feed availability, market access, and survey coverage) where data are supplied, and follow the sector deliverables (subsector baseline; climate/water dependencies; livelihood and market risks; feasible interventions; monitoring requirements).', 'questions': ['Which livestock, apiculture or aquaculture systems face the greatest resource constraints?', 'Where are water, feed, habitat or market-access gaps limiting production?', 'Which sustainable interventions could improve rural livelihoods without increasing ecosystem pressure?'], 'outputs': 'subsector baseline; climate/water dependencies; livelihood and market risks; feasible interventions; monitoring requirements'}, 'Soils, water quality and wastewater': {'task': 'Assess surface/groundwater quality, salinity/sodicity, nutrients, pathogens, industrial effluent, treatment performance, reuse suitability, and receiving-water effects. Use the relevant indicators (pH, EC/TDS, DO, BOD/COD, turbidity, nutrients, microbial indicators, sampling date/location, analytical method, standards version, and detection limits) where data are supplied, and follow the sector deliverables (parameter-by-parameter assessment; source/pathway/receptor analysis; treatment and monitoring options; standards comparison only when jurisdiction and version are known).', 'questions': ['Which monitored sites or parameters show the greatest water-quality concern?', 'What treatment, pollution-control or reuse options merit technical evaluation?', 'What sampling and compliance evidence is missing?'], 'outputs': 'parameter-by-parameter assessment; source/pathway/receptor analysis; treatment and monitoring options; standards comparison only when jurisdiction and version are known'}, 'Forests, biodiversity and ecosystem services': {'task': 'Assess forest cover, habitat connectivity, biodiversity pressures, watershed services, degradation, restoration, and protected-area/community considerations. Use the relevant indicators (land-cover year/resolution, area units, classification accuracy, species/source provenance, fragmentation, restoration survival, and ecosystem-service assumptions) where data are supplied, and follow the sector deliverables (baseline and pressure pathways; conservation/restoration options; co-benefits and trade-offs; monitoring indicators; stakeholder and land-tenure questions).', 'questions': ['Which ecosystems require priority baseline surveys or conservation measures?', 'Where could proposed development affect habitats or ecosystem services?', 'How can restoration and monitoring be integrated with local livelihoods?'], 'outputs': 'baseline and pressure pathways; conservation/restoration options; co-benefits and trade-offs; monitoring indicators; stakeholder and land-tenure questions'}, 'Mining and mineral resources': {'task': 'Assess mineral occurrence versus reserves/resources, extraction, water/energy use, tailings, acid drainage, dust, worker/community safety, transport, and closure planning. Use the relevant indicators (resource classification and reporting date, production units, water intensity, waste/tailings characteristics, emissions, permits, rehabilitation liabilities, and source provenance) where data are supplied, and follow the sector deliverables (resource-data quality review; lifecycle risks; water/energy dependencies; safeguards and monitoring; closure/rehabilitation considerations).', 'questions': ['Which mineral prospects require further verified geological and economic investigation?', 'What water, waste, biodiversity and community safeguards are needed?', 'How can local benefits and environmental monitoring be built into project planning?'], 'outputs': 'resource-data quality review; lifecycle risks; water/energy dependencies; safeguards and monitoring; closure/rehabilitation considerations'}, 'Dry fruit and mountain value chains': {'task': 'Assess orchards and wild-harvest sources, seasonal production, water needs, post-harvest losses, processing, storage, transport, market access, and livelihoods. Use the relevant indicators (crop/product, harvest season, production unit/year, source location, quality grade, loss rate, storage conditions, market price/source/date, and employment evidence) where data are supplied, and follow the sector deliverables (value-chain map; climate/water and logistics bottlenecks; value-addition options; smallholder inclusion; data collection plan).', 'questions': ['Which mountain areas merit detailed horticulture or dry-fruit suitability assessment?', 'Where could storage, processing and market access reduce value-chain constraints?', 'How can watershed and forest protection be aligned with rural enterprise development?'], 'outputs': 'value-chain map; climate/water and logistics bottlenecks; value-addition options; smallholder inclusion; data collection plan'}, 'Energy, hydropower and solar': {'task': 'Assess generation, seasonal hydrology, installed versus operational capacity, grid access, solar resource, reliability, environmental/social impacts, and project status. Use the relevant indicators (MW versus MWh, capacity factor basis, commissioning/status date, generation series, water-release dependency, grid constraints, and source) where data are supplied, and follow the sector deliverables (energy baseline; seasonal and climate dependencies; project-status distinctions; alternatives and safeguards; data validation plan).', 'questions': ['Which energy options merit further technical and financial feasibility assessment?', 'How do water availability, climate exposure and grid access affect project choices?', 'What trade-offs exist among hydropower, irrigation and environmental requirements?'], 'outputs': 'energy baseline; seasonal and climate dependencies; project-status distinctions; alternatives and safeguards; data validation plan'}, 'Transport, telecom and critical infrastructure': {'task': 'Assess roads, bridges, communication networks, power/water assets, hazard exposure, redundancy, service continuity, access, and maintenance. Use the relevant indicators (asset inventory/date, location accuracy, condition, hazard exposure, criticality, outage duration, redundancy, population served, and inspection status) where data are supplied, and follow the sector deliverables (asset-risk register; dependencies and cascading failure pathways; resilience measures; continuity plan; inspection/engineering review checklist).', 'questions': ['Which critical assets or corridors require priority resilience assessment?', 'Where are connectivity and service-continuity gaps most significant?', 'Which engineering and environmental investigations are required before project approval?'], 'outputs': 'asset-risk register; dependencies and cascading failure pathways; resilience measures; continuity plan; inspection/engineering review checklist'}, 'Urban growth, housing and municipal services': {'task': 'Assess urban expansion, drainage, water supply, wastewater, solid waste, heat, land-use pressure, service access, and climate resilience. Use the relevant indicators (population year/source, built-up area and resolution, service coverage, demand/supply basis, flood exposure, heat metrics, and infrastructure capacity) where data are supplied, and follow the sector deliverables (urban service baseline; spatial growth scenarios; vulnerable-neighbourhood considerations; investment options; governance and monitoring plan).', 'questions': ['Which urban areas show the greatest water, drainage, sanitation or service gaps?', 'Where should municipal infrastructure upgrades be prioritised?', 'How can urban expansion avoid high-risk and environmentally sensitive areas?'], 'outputs': 'urban service baseline; spatial growth scenarios; vulnerable-neighbourhood considerations; investment options; governance and monitoring plan'}, 'Socio-economic development and employment': {'task': 'Assess poverty, employment, livelihoods, distributional impacts, rural/urban differences, gender and inclusion where evidence supports it, and access to services. Use the relevant indicators (survey/year, sample and geographic resolution, income/employment definitions, price basis, missingness, uncertainty, and disaggregation limits) where data are supplied, and follow the sector deliverables (who benefits/who bears costs; distributional pathways; data-quality assessment; safeguards; monitoring and consultation plan).', 'questions': ['Which regions show the strongest evidence of livelihood or service-access disparities?', 'Which sectors could support inclusive employment based on local assets and constraints?', 'How do climate and infrastructure risks affect vulnerable households?'], 'outputs': 'who benefits/who bears costs; distributional pathways; data-quality assessment; safeguards; monitoring and consultation plan'}, 'IWT, water diplomacy and legal-policy evidence': {'task': 'Assess treaty text and annexes, institutional roles, procedural chronology, technical data exchange, party positions, and evidence-based policy options. Use the relevant indicators (document title/date/article or annex, primary versus secondary source, procedural status/date, attributed position, and unresolved factual question) where data are supplied, and follow the sector deliverables (verified chronology from supplied evidence; legal text versus party interpretation; technical questions; evidence gaps; neutral options and verification matrix).', 'questions': ['What verified flow, project and treaty records are needed to assess the technical issue?', 'Which questions should be distinguished as treaty text, party position, technical evidence or interpretation?', 'What monitoring and information-exchange gaps limit a defensible assessment?'], 'outputs': 'verified chronology from supplied evidence; legal text versus party interpretation; technical questions; evidence gaps; neutral options and verification matrix'}, 'Environmental, ESG and SDG assessment': {'task': 'Assess environmental and social risks, governance, materiality, stakeholder impacts, safeguards, SDG alignment, indicators, and reporting boundaries. Use the relevant indicators (indicator definition, baseline/year, unit, scope, data owner, methodology, target, evidence quality, and reporting standard/version) where data are supplied, and follow the sector deliverables (material issues; impacts/risks/opportunities; SDG mapping with rationale; mitigation hierarchy; KPI register; disclosure gaps).', 'questions': ['Which environmental and social outcomes are supported by measurable indicators?', 'Where are safeguards, governance or monitoring gaps?', 'Which indicators should be tracked through the project lifecycle?'], 'outputs': 'material issues; impacts/risks/opportunities; SDG mapping with rationale; mitigation hierarchy; KPI register; disclosure gaps'}, 'Disaster resilience and emergency preparedness': {'task': 'Assess multi-hazard preparedness, early-warning communication, response capacity, critical-service continuity, recovery, and vulnerable populations. Use the relevant indicators (hazard source/date, lead time, warning reach, evacuation capacity, shelter/service access, response resources, and after-action evidence) where data are supplied, and follow the sector deliverables (preparedness gap assessment; roles and communication pathways; scenario exercises; continuity and recovery actions; verification checklist).', 'questions': ['Which preparedness and coordination gaps should be addressed first?', 'How can warnings and response resources reach exposed communities more effectively?', 'What institutional capabilities are required for resilient recovery?'], 'outputs': 'preparedness gap assessment; roles and communication pathways; scenario exercises; continuity and recovery actions; verification checklist'}, 'Governance, institutions and public investment': {'task': 'Assess mandates, coordination, budgets, procurement, data stewardship, accountability, implementation capacity, and monitoring/evaluation. Use the relevant indicators (mandate/source, budget year, expenditure basis, procurement status, responsible entity, milestones, output/outcome measures, and audit trail) where data are supplied, and follow the sector deliverables (institutional responsibility matrix; implementation dependencies; procurement and transparency risks; milestones; monitoring framework).', 'questions': ['Which institutional or implementation bottlenecks most affect project outcomes?', 'How should public investments be prioritised transparently against agreed criteria?', 'What accountability and monitoring arrangements are needed?'], 'outputs': 'institutional responsibility matrix; implementation dependencies; procurement and transparency risks; milestones; monitoring framework'}, 'Tourism, recreation and mountain safety': {'task': 'Assess seasonality, access, carrying capacity, weather and terrain hazards, water/sanitation, ecosystem impacts, local livelihoods, and visitor safety. Use the relevant indicators (visitor data source/year, access season, hazard inventory, trail/site condition, service capacity, waste/water pressure, and incident records) where data are supplied, and follow the sector deliverables (destination baseline; seasonal constraints; resilience and environmental measures; local benefit options; visitor-safety and monitoring needs).', 'questions': ['Which destinations have tourism potential subject to environmental and access constraints?', 'Where are visitor safety, emergency access or carrying-capacity gaps?', 'How can tourism benefits be balanced with ecosystem and community protection?'], 'outputs': 'destination baseline; seasonal constraints; resilience and environmental measures; local benefit options; visitor-safety and monitoring needs'}, 'Cross-sector integrated assessment': {'task': 'Assess interdependencies across water, climate, terrain, hazards, food, energy, infrastructure, ecosystems, livelihoods, governance, and policy. Use the relevant indicators (shared baseline years/units, dependency links, common scenarios, distributional effects, uncertainty, and evidence provenance) where data are supplied, and follow the sector deliverables (systems map; sector-by-sector findings; trade-off matrix; compound/cascading risks; ranked options with rationale; joint data and monitoring plan).', 'questions': ['Which intervention offers the strongest cross-sector benefits with manageable trade-offs?', 'Where could a decision in one sector transfer costs or risks to another?', 'Which shared datasets and governance arrangements are needed for coordinated planning?'], 'outputs': 'systems map; sector-by-sector findings; trade-off matrix; compound/cascading risks; ranked options with rationale; joint data and monitoring plan'}}

def _read_uploaded_evidence(files) -> tuple[str, list[dict]]:
    """Extract bounded text from user-supplied evidence files; no network access."""
    import io
    import pandas as pd
    chunks, profiles = [], []
    for uploaded in files or []:
        name = uploaded.name
        raw = uploaded.getvalue()
        suffix = name.lower().rsplit(".", 1)[-1] if "." in name else ""
        try:
            if suffix == "csv":
                df = pd.read_csv(io.BytesIO(raw), nrows=500)
                profile = {"file": name, "rows_loaded": len(df), "columns": list(df.columns),
                           "missing_cells": int(df.isna().sum().sum()), "preview": df.head(8).to_string(index=False)}
                profiles.append(profile)
                chunks.append(f"\n### Uploaded CSV: {name}\nRows loaded (max 500): {len(df)}\nColumns: {list(df.columns)}\nMissing cells: {profile['missing_cells']}\nPreview:\n{profile['preview']}")
            elif suffix in ("xlsx", "xls"):
                df = pd.read_excel(io.BytesIO(raw), nrows=500)
                profile = {"file": name, "rows_loaded": len(df), "columns": list(df.columns),
                           "missing_cells": int(df.isna().sum().sum()), "preview": df.head(8).to_string(index=False)}
                profiles.append(profile)
                chunks.append(f"\n### Uploaded spreadsheet: {name}\nRows loaded (max 500): {len(df)}\nColumns: {list(df.columns)}\nMissing cells: {profile['missing_cells']}\nPreview:\n{profile['preview']}")
            elif suffix == "pdf":
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(raw))
                text = "\n".join((page.extract_text() or "") for page in reader.pages[:30])
                chunks.append(f"\n### Uploaded PDF: {name}\n{text[:18000]}")
                profiles.append({"file": name, "pages": len(reader.pages), "characters_extracted": len(text)})
            elif suffix in ("txt", "md"):
                text = raw.decode("utf-8", errors="replace")
                chunks.append(f"\n### Uploaded text: {name}\n{text[:18000]}")
                profiles.append({"file": name, "characters_extracted": len(text)})
            else:
                profiles.append({"file": name, "status": "Unsupported format; not included"})
        except Exception as exc:
            profiles.append({"file": name, "status": f"Could not read: {type(exc).__name__}: {exc}"})
    return "\n".join(chunks)[:60000], profiles


def render_agentic_ai_page():
    st.title("🤖 Agentic AI Command Centre — CrewAI")
    st.caption("Interactive, evidence-aware reporting across IndusSphere Pakistan sectors.")
    st.info("Decision-support only. Outputs are drafts, not operational control, official warnings, legal advice, or certified engineering assessments. Human review is required.")

    with st.expander("How the agent team works", expanded=False):
        st.markdown("""
        **Planner → Sector Analyst → Independent Reviewer → Human decision-maker.**
        Separate mode creates one report per selected sector. Integrated mode creates a synthesis of dependencies,
        cumulative risks, trade-offs and coordinated priorities. Uploaded files are parsed locally by this app and
        supplied as context; this workflow does not perform live web research or independently authenticate sources.
        """)

    st.subheader("📚 Task & Decision Library")
    st.caption("Select any sector, choose a decision question, and insert a ready-to-edit task into the agent workflow.")
    lib_col1, lib_col2 = st.columns(2)
    with lib_col1:
        library_sector = st.selectbox("Sector library", list(SECTOR_TASK_LIBRARY.keys()), key="agentic_library_sector_v3")
    with lib_col2:
        library_question = st.selectbox("Decision question", SECTOR_TASK_LIBRARY[library_sector]["questions"], key="agentic_library_question_v3")
    st.markdown("**Recommended task**")
    st.info(SECTOR_TASK_LIBRARY[library_sector]["task"])
    st.caption("Expected deliverables: " + SECTOR_TASK_LIBRARY[library_sector]["outputs"])
    if st.button("➕ Insert task and decision question", use_container_width=True, key="agentic_insert_library_v3"):
        st.session_state["agentic_goal_v2"] = (
            f"SECTOR: {library_sector}\nASSESSMENT TASK: {SECTOR_TASK_LIBRARY[library_sector]['task']}\n"
            f"PRIMARY DECISION QUESTION: {library_question}\n"
            "Compare realistic options, explain trade-offs, prioritise recommendations, state assumptions and uncertainties, "
            "and list the additional evidence needed before implementation. Do not invent measurements, citations or project status."
        )
        st.session_state["agentic_context_v2"] = (
            "Expected deliverables: " + SECTOR_TASK_LIBRARY[library_sector]["outputs"] + "\n"
            "Separate user-supplied evidence, general knowledge, assumptions and unavailable data. Identify geography, time period, "
            "units, provenance and confidence for quantitative claims."
        )
        st.rerun()

    goal = st.text_area("Task / decision question", placeholder="Choose a task above or enter your own question. Example: Assess water, food, energy and climate resilience priorities for a development programme in Pakistan.", height=120, key="agentic_goal_v2")
    context = st.text_area("Additional project context", placeholder="Add geography, project phase, dates, assumptions, constraints and known sources.", height=100, key="agentic_context_v2")

    with st.expander("1. Evidence room — upload project data", expanded=True):
        uploads = st.file_uploader("Upload CSV, Excel, PDF, TXT or Markdown evidence", type=["csv", "xlsx", "xls", "pdf", "txt", "md"], accept_multiple_files=True, key="agentic_evidence_upload_v2")
        evidence_text, evidence_profiles = _read_uploaded_evidence(uploads)
        if evidence_profiles:
            st.write("Local file inspection")
            st.dataframe(evidence_profiles, use_container_width=True, hide_index=True)
            st.caption("Spreadsheet previews are limited to 500 rows per file; PDF extraction to 30 pages; extracted evidence is truncated to 60,000 characters in total.")

    with st.expander("2. Analysis controls", expanded=True):
        mode = st.radio("Reporting mode", ["Separate reports for each selected sector", "One integrated cross-sector report"], horizontal=True, key="agentic_mode_v2")
        sectors = st.multiselect("Select sectors", options=list(SECTOR_PLAYBOOKS.keys()), default=["Integrated water resources and basin hydrology"], key="agentic_sectors_v2")
        c1, c2, c3 = st.columns(3)
        with c1:
            geography = st.text_input("Geographic scope", value="Pakistan", key="agentic_geo_v2")
            horizon = st.selectbox("Assessment horizon", ["Current baseline", "Near term (1–5 years)", "Mid-term (5–15 years)", "Long term (15+ years)", "Historical review", "User-defined"], key="agentic_horizon_v2")
        with c2:
            scenario = st.selectbox("Scenario lens", ["Baseline / business as usual", "Climate-stress scenario", "High-growth / demand scenario", "Resilience / adaptation scenario", "Compare multiple scenarios"], key="agentic_scenario_v2")
            audience = st.selectbox("Intended audience", ["Engineering and technical team", "Policy and planning", "Development partners / donors", "Academic / research", "Executive decision-makers", "General project stakeholders"], key="agentic_audience_v2")
        with c3:
            detail = st.select_slider("Analysis depth", options=["Concise", "Standard", "Detailed", "Comprehensive"], value="Detailed", key="agentic_depth_v2")
            priority = st.selectbox("Priority lens", ["Balanced", "Risk reduction", "Cost and implementation", "Equity and livelihoods", "Environmental sustainability", "Data and evidence quality"], key="agentic_priority_v2")
        provider = st.selectbox("LLM provider", ["Groq", "OpenAI"], key="agentic_provider_v2")
        model = st.selectbox("Model", ["openai/gpt-oss-120b"] if provider == "Groq" else ["gpt-4o-mini", "gpt-4.1-mini"], key="agentic_model_v2")
        key_name = "GROQ_API_KEY" if provider == "Groq" else "OPENAI_API_KEY"
        key_from_secret = _secret(key_name)
        api_key = st.text_input(f"{provider} API key (or configure {key_name} in Streamlit Secrets)", type="password", key="agentic_key_v2", help="Never commit API keys to GitHub.")
        approved = st.checkbox("I will review and independently verify factual, legal, environmental and engineering claims.", key="agentic_human_review_v2")

    generate = st.button("🚀 Run agent team and generate report(s)", type="primary", use_container_width=True, key="agentic_run_v2")
    if generate:
        if not goal.strip():
            st.error("Enter a task or decision question.")
            return
        if not sectors:
            st.error("Select at least one sector.")
            return
        if not approved:
            st.warning("Confirm human review before running the agents.")
            return
        key = api_key.strip() or key_from_secret
        if not key:
            st.error(f"No API key found. Configure {key_name} in Streamlit Secrets or enter it above. Never commit keys to GitHub.")
            return
        full_context = "\n\n".join(x for x in [context.strip(), evidence_text] if x) or "No additional context supplied."
        settings = {"Geographic scope": geography, "Assessment horizon": horizon, "Scenario lens": scenario,
                    "Intended audience": audience, "Priority lens": priority,
                    "Evidence files": ", ".join(f.name for f in (uploads or [])) or "None"}
        total = 1 if mode == "One integrated cross-sector report" else len(sectors)
        progress = st.progress(0, text="Preparing agent workflow…")
        status = st.empty()
        reports = {}
        try:
            if mode == "One integrated cross-sector report":
                status.info("Planner, integrated analyst and independent reviewer are working…")
                reports["Integrated_Cross_Sector_Report"] = _run_reporting_crew(provider, key, model, goal, full_context, detail, sectors, True, settings)
                progress.progress(1.0, text="Integrated report complete")
            else:
                for index, sector in enumerate(sectors, start=1):
                    status.info(f"Running sector workflow {index}/{total}: {sector}")
                    safe_name = "_".join("".join(ch for ch in word if ch.isalnum()) for word in sector.split())
                    reports[safe_name + "_Report"] = _run_reporting_crew(provider, key, model, goal, full_context, detail, [sector], False, settings)
                    progress.progress(index / total, text=f"Completed {index} of {total} sector reports")
            st.session_state["crewai_sector_reports"] = reports
            st.session_state["crewai_last_goal"] = goal.strip()
            st.session_state["crewai_reporting_mode"] = mode
            st.session_state["crewai_report_settings"] = settings
            status.success(f"Generated {len(reports)} report(s). Review evidence and limitations before use.")
        except ImportError as exc:
            status.empty(); st.error("A required CrewAI/provider dependency could not be imported.")
            with st.expander("Import error details"): st.code(f"{type(exc).__name__}: {exc}")
            return
        except Exception as exc:
            status.empty(); st.error("The agent workflow could not complete. Check provider credentials, model availability, quota and logs.")
            with st.expander("Technical error details"): st.code(f"{type(exc).__name__}: {exc}")
            return

    reports = st.session_state.get("crewai_sector_reports", {})
    if reports:
        st.subheader("📑 Agent-generated reports")
        st.caption(st.session_state.get("crewai_reporting_mode", "Generated reports"))
        import io, zipfile
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for name, report_text in reports.items():
                content = f"# IndusSphere Pakistan — {name.replace('_', ' ')}\n\n{report_text}"
                with st.expander(name.replace("_", " "), expanded=(len(reports) == 1)):
                    st.markdown(report_text)
                    st.download_button("⬇️ Download Markdown", data=content.encode("utf-8"), file_name=f"{name}.md", mime="text/markdown", key=f"download_{name}_v2")
                zf.writestr(f"{name}.md", content)
        st.download_button("📦 Download all reports (ZIP)", data=archive.getvalue(), file_name="indussphere_agentic_reports.zip", mime="application/zip", use_container_width=True, key="download_all_agentic_v2")
        if st.button("Clear generated reports", key="clear_agentic_reports_v2"):
            st.session_state.pop("crewai_sector_reports", None)
            st.rerun()
