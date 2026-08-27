"""
Work portfolio data — Fabio Prumucena @ BMO (allocated via Connext)
Extracted from an Outlook/Teams scan (Microsoft Copilot), July–August 2026.

HOW TO UPDATE THIS FILE
------------------------
Each entry in WORK_ITEMS is one piece of work: a support case, an incident,
an initiative/investigation, an event, or a recurring meeting.
Add a new dict to the list to add a new item — the dashboard picks it up
automatically, no code changes needed elsewhere.

Fields:
    id          str   short unique key
    type        str   "Case" | "Incident" | "Initiative" | "Event" | "Meeting"
    ref         str   ticket/case number, or "" if none
    title       str   short title
    workstream  str   must be a key in WORKSTREAMS below
    start       str   "YYYY-MM-DD"
    end         str   "YYYY-MM-DD" or "" if single-day / ongoing
    status      str   "Resolved" | "In Progress" | "Active" | "Unknown"
    role        str   what Fabio actually did
    people      list  collaborators / counterparts mentioned
    evidence    str   where this came from (email subject / meeting / doc)
    confirmed   bool  False = Copilot flagged this as not fully verified
"""

# Fixed categorical palette (dataviz skill default, assigned in order — never cycled)
WORKSTREAMS = {
    "UIP Rollup & Certificates":       "#2a78d6",  # blue
    "UMS Connectivity & Power Cycle":  "#eb6834",  # orange
    "UAD / Agent Desktop":             "#1baf7a",  # aqua
    "Infrastructure Performance":      "#eda100",  # yellow
    "Logging & PII Compliance":        "#e87ba4",  # magenta
    "CCS Ops Cadence":                 "#008300",  # green
}

STATUS_COLORS = {
    "Resolved":    "#0ca30c",
    "In Progress": "#fab219",
    "Active":      "#fab219",
    "Unknown":     "#898781",
}

TYPE_SYMBOLS = {
    "Case":       "circle",
    "Incident":   "diamond",
    "Initiative": "square",
    "Event":      "triangle-up",
    "Meeting":    "circle-open",
}

JOIN_DATE = "2026-07-13"   # meados de julho — adjust if you know the exact date
TODAY = "2026-08-27"

WORK_ITEMS = [
    # ---- Recurring CCS operating cadence (ongoing since arrival) ----
    {
        "id": "MTG-01", "type": "Meeting", "ref": "", "title": "CCS Morning Meeting",
        "workstream": "CCS Ops Cadence", "start": JOIN_DATE, "end": TODAY,
        "status": "Active", "role": "Daily participant — brought on to cover CCS during a teammate's absence",
        "people": ["CCS team"], "evidence": "CCS Morning Meeting *New Invite* (recurring)",
        "confirmed": True,
    },
    {
        "id": "MTG-02", "type": "Meeting", "ref": "", "title": "Weekly CCS Deck Update Mtg",
        "workstream": "CCS Ops Cadence", "start": "2026-07-14", "end": TODAY,
        "status": "Active", "role": "Recurring contributor to the CCS status deck",
        "people": ["Parra, Yeffer", "Patel, Dharmendrakumar", "Freed, Mike"],
        "evidence": "Weekly CCS Deck Update Mtg (recurring)", "confirmed": True,
    },
    {
        "id": "MTG-03", "type": "Meeting", "ref": "", "title": "Discuss Incidents & Problems",
        "workstream": "CCS Ops Cadence", "start": "2026-07-14", "end": TODAY,
        "status": "Active", "role": "Operational review — incident & problem analysis",
        "people": ["CCS team"], "evidence": "Discuss Incidents & Problems (recurring)",
        "confirmed": True,
    },
    {
        "id": "MTG-04", "type": "Meeting", "ref": "", "title": "P&V Prod Changes — Review & Discussion",
        "workstream": "CCS Ops Cadence", "start": "2026-07-14", "end": TODAY,
        "status": "Active", "role": "Reviews production changes ahead of implementation",
        "people": ["CCS team"], "evidence": "P & V Prod Changes - review and discussion (recurring)",
        "confirmed": True,
    },
    {
        "id": "MTG-05", "type": "Meeting", "ref": "", "title": "CCS Dev & SD Leaders' Meeting (Weekly Update to Ali)",
        "workstream": "CCS Ops Cadence", "start": "2026-07-14", "end": TODAY,
        "status": "Active", "role": "Weekly leadership update forum",
        "people": ["Ali (leadership)"], "evidence": "CCS Dev & SD Leaders' Meeting - Weekly Update to Ali (recurring)",
        "confirmed": True,
    },

    # ---- UAD / Agent Desktop ----
    {
        "id": "INIT-UADGW", "type": "Initiative", "ref": "", "title": "UAD GW Login Fail — Investigation",
        "workstream": "UAD / Agent Desktop", "start": "2026-07-24", "end": "2026-07-24",
        "status": "Resolved", "role": "Led technical investigation: analyzed CC2DCP, Prophecy, UMS, Teams; "
                                       "built hypotheses (DTMF, SBC, Direct Routing, Station ID) and a "
                                       "troubleshooting/validation plan",
        "people": ["CCS team"], "evidence": "Fw: UAD GW FAIL", "confirmed": True,
    },
    {
        "id": "INC-9540244", "type": "Incident", "ref": "INC9540244", "title": "UAD Notify / Desktop Support Escalation",
        "workstream": "UAD / Agent Desktop", "start": TODAY, "end": "",
        "status": "Unknown", "role": "Referenced in Teams — detail not yet confirmed",
        "people": [], "evidence": "Referenced in Teams (unconfirmed)", "confirmed": False,
    },

    # ---- UIP Rollup & Certificates ----
    {
        "id": "CASE-01607749", "type": "Case", "ref": "01607749",
        "title": "URM — Certificate Validation Errors",
        "workstream": "UIP Rollup & Certificates", "start": "2026-08-04", "end": "2026-08-07",
        "status": "Active", "role": "Received and tracked the full case thread; assessed operational impact",
        "people": ["Parra, Yeffer", "Alvaria Customer Care"],
        "evidence": "FW: Customer Care | Case 01607749", "confirmed": True,
    },
    {
        "id": "INIT-ROLLUP-ANALYSIS", "type": "Initiative", "ref": "",
        "title": "UIP 7.4 SP2 Rollup — Impact Analysis",
        "workstream": "UIP Rollup & Certificates", "start": "2026-08-13", "end": "2026-08-13",
        "status": "Resolved", "role": "Assessed TLS 1.3, JRE17 client, Hotfix Utility, and thick-client impact; "
                                       "sent findings to Freed, Mike",
        "people": ["Freed, Mike"], "evidence": "FW: uip", "confirmed": True,
    },
    {
        "id": "INIT-ROLLUP-NOTES", "type": "Initiative", "ref": "",
        "title": "UIP 7.4 SP2 Rollup — Release Notes Reviewed",
        "workstream": "UIP Rollup & Certificates", "start": "2026-08-14", "end": "2026-08-14",
        "status": "Resolved", "role": "Reviewed official Alvaria release notes ahead of deployment",
        "people": ["Alvaria"], "evidence": "UIP 7.4SP2 July 2026 Roll Up - ACC Release Notes", "confirmed": True,
    },
    {
        "id": "CASE-01615360", "type": "Case", "ref": "01615360",
        "title": "Requesting Aspect to Run Rollup 7.4 SP2 on Dev Environment",
        "workstream": "UIP Rollup & Certificates", "start": "2026-08-17", "end": "",
        "status": "Active", "role": "Opened and owns the case as primary contact",
        "people": ["Alvaria Support"], "evidence": "Support Case 01615360", "confirmed": True,
    },
    {
        "id": "CASE-01616878", "type": "Case", "ref": "01616878",
        "title": "URM Dependency Question (isolated install vs. full Rollup)",
        "workstream": "UIP Rollup & Certificates", "start": "2026-08-18", "end": "2026-08-18",
        "status": "Resolved", "role": "Authored the technical inquiry; got confirmation the isolated install "
                                       "isn't supported — recommended the full Rollup",
        "people": ["Alvaria Support"], "evidence": "Support Case 01616878", "confirmed": True,
    },

    # ---- Infrastructure Performance ----
    {
        "id": "INC-9494962", "type": "Incident", "ref": "INC9494962",
        "title": "RDP Access to Support PC (Server Configurator Screenshot)",
        "workstream": "Infrastructure Performance", "start": "2026-08-17", "end": "2026-08-17",
        "status": "Resolved", "role": "Opened the incident to get RDP access", "people": ["Alvaria Support"],
        "evidence": "Incident INC9494962", "confirmed": True,
    },
    {
        "id": "CASE-01616122", "type": "Case", "ref": "01616122",
        "title": "Dev Core Server Extremely Slow (blocking UCC Modify/Install)",
        "workstream": "Infrastructure Performance", "start": "2026-08-18", "end": "",
        "status": "Active", "role": "Primary contact; received and is acting on Alvaria's recommendation to "
                                     "upgrade 2 vCPU → 4 vCPU",
        "people": ["Alvaria Support"], "evidence": "Support Case 01616122", "confirmed": True,
    },
    {
        "id": "CASE-01618600", "type": "Case", "ref": "01618600",
        "title": "Disk Space Alert — alm-ocbqwboe001",
        "workstream": "Infrastructure Performance", "start": "2026-08-27", "end": "2026-08-27",
        "status": "Resolved", "role": "Opened the case and diagnosed root cause (large files were SAP BOE/CMS, "
                                       "likely unrelated to the Aspect ALM)",
        "people": ["Alvaria Support"], "evidence": "Alvaria Folks", "confirmed": True,
    },

    # ---- UMS Connectivity & Power Cycle ----
    {
        "id": "CASE-01617334", "type": "Case", "ref": "01617334",
        "title": "UMS Loses Connection to CC2DCP Constantly",
        "workstream": "UMS Connectivity & Power Cycle", "start": "2026-08-24", "end": "",
        "status": "In Progress", "role": "Coordinated the physical power-cycle recommendation, operations "
                                          "communication, onsite support, and the Alvaria interface — "
                                          "the most significant case in this window",
        "people": ["Paola Barreto Betancourt (Alvaria)", "Parra, Yeffer", "Freed, Mike"],
        "evidence": "Case 01617334 / Paola Barreto Betancourt thread", "confirmed": True,
    },
    {
        "id": "EVT-POWERCYCLE", "type": "Event", "ref": "",
        "title": "Power Cycle Executed — UIP-BCCBDVUMS01 (10.197.20.16)",
        "workstream": "UMS Connectivity & Power Cycle", "start": "2026-08-25", "end": "2026-08-25",
        "status": "Resolved", "role": "Coordinated the shutdown and onsite physical restart of the appliance",
        "people": ["Onsite/NOC support"], "evidence": "RE: POWER CYCLE UIP-BCCBDVUMS01", "confirmed": True,
    },
    {
        "id": "MTG-POWERCYCLE", "type": "Meeting", "ref": "",
        "title": "Teams Discussion — UMS Power Cycle Process",
        "workstream": "UMS Connectivity & Power Cycle", "start": "2026-08-25", "end": "2026-08-25",
        "status": "Resolved", "role": "Aligned on the official power-cycle process, onsite requirements, and "
                                       "BCC/NOC location",
        "people": ["Parra, Yeffer", "Freed, Mike"], "evidence": "Alvaria Folks (Teams)", "confirmed": True,
    },

    # ---- Logging & PII Compliance ----
    {
        "id": "CASE-01617931", "type": "Case", "ref": "01617931",
        "title": "UIP Log Level Changes in QA",
        "workstream": "Logging & PII Compliance", "start": "2026-08-24", "end": "2026-08-25",
        "status": "In Progress", "role": "Opened the case; reviewing log level vs. retention/size trade-offs "
                                          "with Alvaria engineering — status moved to Technical Support Resolving",
        "people": ["Alvaria Support"], "evidence": "New Case: 01617931 / Support Case Updated: 01617931",
        "confirmed": True,
    },
    {
        "id": "INIT-PII", "type": "Initiative", "ref": "CHG1107075 / CTASK2148271",
        "title": "Delivery Letter — Aspect Lowering Logging Levels to Minimize PII",
        "workstream": "Logging & PII Compliance", "start": "2026-08-27", "end": "",
        "status": "Active", "role": "Involved in the PII logging-reduction delivery",
        "people": ["Alvaria"], "evidence": "Delivery Letter: Aspect Lowering Logging Levels to Minimize PII Data",
        "confirmed": True,
    },
]