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

NAMING NOTE (2026-08-28, revised twice same day): every `people` entry
collapses to one of two labels — "Alvaria" for the vendor side, "CCS" for
the internal BMO/Connext side. Neither side tracks named individuals here
anymore:
  - Vendor side -> "Alvaria": covers "Alvaria Support", "Alvaria Customer
    Care", "Aspect" (Aspect Software rebranded to Alvaria), and any named
    person there (Paola Barreto Betancourt, Carlos Estrada, Pedro
    Gonzales, Candido Ortiz, or anyone else at Aspect/Alvaria).
  - Internal side -> "CCS": covers "CCS team" and named BMO/Connext
    colleagues (Parra Yeffer, Freed Mike, Patel Dharmendrakumar, Ali, or
    anyone else on the internal team).
Fabio's call: for this dashboard, which *organization* was on the thread
is what matters, not which specific person — so don't add a new named
individual on either side even if a future item names one; fold them into
"Alvaria" or "CCS" instead. (Two earlier versions of this note drew the
line differently — first keeping named individuals separate, then keeping
just the internal side separate — both superseded.) "Onsite/NOC support"
is left as its own label since it's a distinct function, not an
individual, and nobody's asked to fold it into "CCS" yet.

MERGE NOTE (2026-08-28): three pairs of items that told one continuous
story were combined into a single entry, at Fabio's request, so the
timeline reads as one card instead of two near-duplicates:
  - CASE-01607749 + CASE-01616878        -> CASE-URM
  - INIT-ROLLUP-ANALYSIS + INIT-ROLLUP-NOTES -> INIT-ROLLUP-REVIEW
  - CASE-01617931 + INIT-PII             -> INIT-PII-EXERCISE (renamed
    "PII Unmasked Data Exercise" per Fabio)
The old ids are gone rather than kept as aliases — if you're hunting for
one of them in an old export, it's now part of the merged entry above.
"""

# Fixed categorical palette (dataviz skill default, assigned in order — never cycled)
# Bumped to a punchier, more saturated version on 2026-08-28 for the "My BMO Work"
# tab redesign (Fabio asked for a more modern/marketing-forward look on that tab
# specifically). Same hues/order as before, just brighter — purely cosmetic, does
# not touch any stored key or the training-curriculum tabs.
WORKSTREAMS = {
    "UIP Rollup & Certificates":       "#2F6FED",  # blue
    "UMS Connectivity & Power Cycle":  "#FF6A3D",  # orange
    "UAD / Agent Desktop":             "#12C48B",  # aqua/teal
    "Infrastructure Performance":      "#FFC53D",  # yellow
    "Logging & PII Compliance":        "#FF4D8D",  # magenta/pink
    "CCS Ops Cadence":                 "#22B14C",  # green
}

# One emoji per workstream, same keys/order as WORKSTREAMS — used only by the
# "My BMO Work" tab's KPI/pulse cards for quick visual scanning. Purely
# decorative; add an entry here if you add a new workstream key above.
WORKSTREAM_ICONS = {
    "UIP Rollup & Certificates":       "🔐",
    "UMS Connectivity & Power Cycle":  "⚡",
    "UAD / Agent Desktop":             "🖥️",
    "Infrastructure Performance":      "🛠️",
    "Logging & PII Compliance":        "🔏",
    "CCS Ops Cadence":                 "🔁",
}

STATUS_COLORS = {
    "Resolved":    "#00C853",
    "In Progress": "#FF9800",
    "Active":      "#FF9800",
    "Unknown":     "#9E9E9E",
}

# One emoji per work-item type — used only by the "My BMO Work" tab's Detail
# Log for quick visual scanning. Purely decorative.
TYPE_EMOJI = {
    "Case":       "📁",
    "Incident":   "🚨",
    "Initiative": "🚀",
    "Event":      "📅",
    "Meeting":    "🔁",
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
        "people": ["CCS"], "evidence": "CCS Morning Meeting *New Invite* (recurring)",
        "confirmed": True,
    },
    {
        "id": "MTG-02", "type": "Meeting", "ref": "", "title": "Weekly CCS Deck Update Mtg",
        "workstream": "CCS Ops Cadence", "start": "2026-07-14", "end": TODAY,
        "status": "Active", "role": "Recurring contributor to the CCS status deck",
        "people": ["CCS"],
        "evidence": "Weekly CCS Deck Update Mtg (recurring)", "confirmed": True,
    },
    {
        "id": "MTG-03", "type": "Meeting", "ref": "", "title": "Discuss Incidents & Problems",
        "workstream": "CCS Ops Cadence", "start": "2026-07-14", "end": TODAY,
        "status": "Active", "role": "Operational review — incident & problem analysis",
        "people": ["CCS"], "evidence": "Discuss Incidents & Problems (recurring)",
        "confirmed": True,
    },
    {
        "id": "MTG-04", "type": "Meeting", "ref": "", "title": "P&V Prod Changes — Review & Discussion",
        "workstream": "CCS Ops Cadence", "start": "2026-07-14", "end": TODAY,
        "status": "Active", "role": "Reviews production changes ahead of implementation",
        "people": ["CCS"], "evidence": "P & V Prod Changes - review and discussion (recurring)",
        "confirmed": True,
    },
    {
        "id": "MTG-05", "type": "Meeting", "ref": "", "title": "CCS Dev & SD Leaders' Meeting (Weekly Update to Ali)",
        "workstream": "CCS Ops Cadence", "start": "2026-07-14", "end": TODAY,
        "status": "Active", "role": "Weekly leadership update forum",
        "people": ["CCS"], "evidence": "CCS Dev & SD Leaders' Meeting - Weekly Update to Ali (recurring)",
        "confirmed": True,
    },

    # ---- UAD / Agent Desktop ----
    {
        "id": "INIT-UADGW", "type": "Initiative", "ref": "", "title": "UAD GW Login Fail — Investigation",
        "workstream": "UAD / Agent Desktop", "start": "2026-07-24", "end": "2026-07-24",
        "status": "Resolved", "role": "Led technical investigation: analyzed CC2DCP, Prophecy, UMS, Teams; "
                                       "built hypotheses (DTMF, SBC, Direct Routing, Station ID) and a "
                                       "troubleshooting/validation plan",
        "people": ["CCS"], "evidence": "Fw: UAD GW FAIL", "confirmed": True,
    },
    {
        "id": "INC-9540244", "type": "Incident", "ref": "INC9540244", "title": "UAD Notify / Desktop Support Escalation",
        "workstream": "UAD / Agent Desktop", "start": TODAY, "end": "",
        "status": "Unknown", "role": "Referenced in Teams — detail not yet confirmed",
        "people": [], "evidence": "Referenced in Teams (unconfirmed)", "confirmed": False,
    },

    # ---- UIP Rollup & Certificates ----
    {
        # Merged 2026-08-28 from two separate URM cases (01607749 + 01616878)
        # at Fabio's request — same underlying topic (URM), so one card
        # tells the story better than two fragments a couple weeks apart.
        "id": "CASE-URM", "type": "Case", "ref": "01607749 / 01616878",
        "title": "URM — Certificate Validation & Dependency Question",
        "workstream": "UIP Rollup & Certificates", "start": "2026-08-04", "end": "2026-08-18",
        "status": "Resolved",
        "role": "Received and tracked the certificate-validation case thread, assessing operational "
                "impact; later authored a follow-up technical inquiry on isolated install vs. full "
                "Rollup and got confirmation the isolated install isn't supported — recommended the "
                "full Rollup",
        "people": ["CCS", "Alvaria"],
        "evidence": "FW: Customer Care | Case 01607749; Support Case 01616878", "confirmed": True,
    },
    {
        # Merged 2026-08-28 from the two same-day Rollup review items
        # (impact analysis + release notes) — one continuous piece of prep
        # work, not two separate ones.
        "id": "INIT-ROLLUP-REVIEW", "type": "Initiative", "ref": "",
        "title": "UIP 7.4 SP2 Rollup — Impact Analysis & Release Notes Review",
        "workstream": "UIP Rollup & Certificates", "start": "2026-08-13", "end": "2026-08-14",
        "status": "Resolved",
        "role": "Assessed TLS 1.3, JRE17 client, Hotfix Utility, and thick-client impact; sent findings "
                "to Freed, Mike. Also reviewed the official Alvaria release notes ahead of deployment",
        "people": ["CCS", "Alvaria"],
        "evidence": "FW: uip; UIP 7.4SP2 July 2026 Roll Up - ACC Release Notes", "confirmed": True,
    },
    {
        "id": "CASE-01615360", "type": "Case", "ref": "01615360",
        "title": "Requesting Aspect to Run Rollup 7.4 SP2 on Dev Environment",
        "workstream": "UIP Rollup & Certificates", "start": "2026-08-17", "end": "",
        "status": "Active", "role": "Opened and owns the case as primary contact",
        "people": ["Alvaria"], "evidence": "Support Case 01615360", "confirmed": True,
    },

    # ---- Infrastructure Performance ----
    {
        "id": "INC-9494962", "type": "Incident", "ref": "INC9494962",
        "title": "RDP Access to Support PC (Server Configurator Screenshot)",
        "workstream": "Infrastructure Performance", "start": "2026-08-17", "end": "2026-08-17",
        "status": "Resolved", "role": "Opened the incident to get RDP access", "people": ["Alvaria"],
        "evidence": "Incident INC9494962", "confirmed": True,
    },
    {
        "id": "CASE-01616122", "type": "Case", "ref": "01616122",
        "title": "Dev Core Server Extremely Slow (blocking UCC Modify/Install)",
        "workstream": "Infrastructure Performance", "start": "2026-08-18", "end": "",
        "status": "Active", "role": "Primary contact; received and is acting on Alvaria's recommendation to "
                                     "upgrade 2 vCPU → 4 vCPU",
        "people": ["Alvaria"], "evidence": "Support Case 01616122", "confirmed": True,
    },
    {
        "id": "CASE-01618600", "type": "Case", "ref": "01618600",
        "title": "Disk Space Alert — alm-ocbqwboe001",
        "workstream": "Infrastructure Performance", "start": "2026-08-27", "end": "2026-08-27",
        "status": "Resolved", "role": "Opened the case and diagnosed root cause (large files were SAP BOE/CMS, "
                                       "likely unrelated to the Aspect ALM)",
        "people": ["Alvaria"], "evidence": "Alvaria Folks", "confirmed": True,
    },

    # ---- UMS Connectivity & Power Cycle ----
    {
        "id": "CASE-01617334", "type": "Case", "ref": "01617334",
        "title": "UMS Loses Connection to CC2DCP Constantly",
        "workstream": "UMS Connectivity & Power Cycle", "start": "2026-08-24", "end": "",
        "status": "In Progress", "role": "Coordinated the physical power-cycle recommendation, operations "
                                          "communication, onsite support, and the Alvaria interface — "
                                          "the most significant case in this window",
        "people": ["Alvaria", "CCS"],
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
        "people": ["CCS"], "evidence": "Alvaria Folks (Teams)", "confirmed": True,
    },

    # ---- Logging & PII Compliance ----
    {
        # Merged 2026-08-28 from the log-level case (01617931) and the PII
        # delivery-letter initiative — the case's log-level work fed
        # straight into this delivery, so Fabio wanted it told as one
        # exercise rather than two disconnected entries.
        "id": "INIT-PII-EXERCISE", "type": "Initiative", "ref": "01617931 / CHG1107075 / CTASK2148271",
        "title": "PII Unmasked Data Exercise",
        "workstream": "Logging & PII Compliance", "start": "2026-08-24", "end": "2026-08-27",
        "status": "Active",
        "role": "Opened the case reviewing log level vs. retention/size trade-offs with Alvaria "
                "engineering; that work fed into the delivery letter covering Alvaria/Aspect lowering "
                "logging levels to minimize PII data exposure",
        "people": ["Alvaria"],
        "evidence": "New Case: 01617931 / Support Case Updated: 01617931; "
                    "Delivery Letter: Aspect Lowering Logging Levels to Minimize PII Data",
        "confirmed": True,
    },
]
