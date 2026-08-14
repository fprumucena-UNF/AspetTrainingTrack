import streamlit as st
import json
import os
import re
from datetime import datetime, date
from zoneinfo import ZoneInfo
import plotly.graph_objects as go

# Toronto local time — used for every "last saved/edited" timestamp shown in
# the UI. America/Toronto auto-switches EST/EDT with daylight saving, and
# %Z prints whichever one is currently in effect.
TORONTO_TZ = ZoneInfo("America/Toronto")


def now_toronto_str():
    return datetime.now(TORONTO_TZ).strftime("%Y-%m-%d %H:%M %Z")

st.set_page_config(page_title="UIP · ALM · AQM Training Track", layout="wide")

# ---------------------------------------------------------------------------
# BMO brand palette (official): Blue #0079C1 · Red #ED1C24 · White #FFFFFF
# ---------------------------------------------------------------------------
BMO_BLUE = "#0079C1"
BMO_BLUE_DARK = "#005587"
BMO_RED = "#ED1C24"
BMO_RED_DEEP = "#A8171D"
BMO_LIGHT_BLUE = "#66B2E0"
BMO_GRAY = "#6C757D"
BMO_GRAY_DEEP = "#4A4F54"

st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}
    [data-testid="stAppViewContainer"] {{
        background-color: #F3F2F1;
    }}
    .block-container {{
        padding-top: 3rem !important;
        padding-bottom: 1.2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }}
    /* Let column rows wrap onto a new line on narrower (laptop) screens instead
       of squeezing everything into one row that never adapts */
    [data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
    }}
    [data-testid="stHorizontalBlock"] > div {{
        min-width: 160px !important;
        flex: 1 1 160px !important;
    }}
    /* Card style for bordered containers (PowerBI tile look) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #FFFFFF !important;
        border-radius: 4px !important;
        border: 1px solid #E1DFDD !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] > div > div {{
        padding: 0.35rem 0.7rem !important;
    }}
    /* Tighter gaps everywhere */
    [data-testid="stVerticalBlock"] {{
        gap: 0.35rem !important;
    }}
    [data-testid="stHorizontalBlock"] {{
        gap: 0.5rem !important;
        align-items: center !important;
    }}
    /* Tabs — compact, PowerBI page-tab style, centered on a solid BMO navy bar */
    /* Uses ARIA roles (tablist/tab) instead of data-baseweb, since Streamlit
       has been removing the BaseWeb library from its components in 2026 releases. */
    [data-testid="stTabs"] [role="tablist"] {{
        gap: 6px !important;
        justify-content: center !important;
        background-color: {BMO_BLUE_DARK} !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15) !important;
    }}
    [data-testid="stTabs"] [role="tab"] {{
        padding: 18px 32px !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: none !important;
        border-radius: 8px !important;
    }}
    [data-testid="stTabs"] [role="tab"] * {{
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #F0F6FC !important;
    }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        background-color: #FFFFFF !important;
        border-bottom: none !important;
    }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] * {{
        color: {BMO_BLUE_DARK} !important;
        font-weight: 800 !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    /* Item labels — compact */
    .item-name {{
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        color: {BMO_BLUE_DARK} !important;
        margin: 0 0 0.15rem 0 !important;
    }}
    .item-weight {{
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: {BMO_BLUE} !important;
    }}
    .status-badge {{
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        padding: 3px 12px !important;
        border-radius: 8px !important;
        letter-spacing: 0.03em;
    }}
    .status-pending {{ background-color: {BMO_GRAY}22; color: {BMO_GRAY}; }}
    .status-completed {{ background-color: {BMO_RED}22; color: {BMO_RED}; }}
    /* Priority badges — Focus vs Deprioritize, per Mike's 2026-08-14 guidance.
       Small pill next to the module name, same visual language as the
       status badges above. Does not affect progress math or stored keys. */
    .priority-badge {{
        display: inline-block;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        padding: 2px 9px !important;
        border-radius: 8px !important;
        letter-spacing: 0.02em;
        margin-left: 6px;
        vertical-align: middle;
    }}
    .priority-focus {{ background-color: #1B873F22; color: #1B873F; }}
    .priority-later {{ background-color: {BMO_GRAY}22; color: {BMO_GRAY}; }}
    /* Completed module cards — stronger fill + accent border when the Done
       toggle is on, using the same "hidden marker div + :has()" trick as
       the Progress card below (Streamlit gives no direct way to style a
       container from a child widget's state). Card-only, doesn't touch
       the toggle widget itself. */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.card-done-marker) {{
        background-color: #E3F3E9 !important;
        border: 1px solid #1B873F !important;
        border-left: 5px solid #1B873F !important;
    }}
    /* Logbook sort buttons — whichever direction (Oldest/Newest first) was
       last clicked stays filled in, same marker + :has() trick again, this
       time targeting the column that holds the active button. Uses
       BMO_LIGHT_BLUE (already in the palette, just unused elsewhere) so the
       fill reads as brand blue but doesn't compete with BMO_BLUE_DARK,
       which the rest of the UI reserves for stronger/darker accents. */
    [data-testid="stHorizontalBlock"] > div:has(.sort-btn-active) button {{
        background-color: {BMO_LIGHT_BLUE} !important;
        color: {BMO_BLUE_DARK} !important;
        border: 1px solid {BMO_BLUE_DARK} !important;
        font-weight: 700 !important;
    }}
    /* Column header strip */
    .col-header {{
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: {BMO_GRAY} !important;
    }}
    /* Selectbox / date input */
    .stSelectbox div[data-baseweb="select"] * {{ font-size: 0.95rem !important; }}
    .stSelectbox div[data-baseweb="select"] {{ min-height: 36px !important; }}
    .stDateInput input {{ font-size: 0.95rem !important; padding: 6px 10px !important; }}
    /* Headings */
    h1 {{ font-size: 1.7rem !important; color: {BMO_BLUE_DARK} !important; margin-bottom: 0.3rem !important; }}
    h3 {{ font-size: 1.2rem !important; margin: 0.25rem 0 !important; color: {BMO_BLUE_DARK} !important; }}
    h4 {{ font-size: 1.05rem !important; margin: 0.25rem 0 !important; color: {BMO_BLUE_DARK} !important; }}
    [data-testid="stCaptionContainer"] {{ font-size: 0.85rem !important; margin: 0.1rem 0 0 0 !important; color: {BMO_GRAY} !important; }}
    /* Metrics — PowerBI KPI tile look */
    [data-testid="stMetric"] {{ padding: 0.25rem 0 !important; }}
    [data-testid="stMetricValue"] {{ font-size: 1.9rem !important; color: {BMO_BLUE_DARK} !important; }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.82rem !important; color: {BMO_GRAY} !important;
        text-transform: uppercase; letter-spacing: 0.03em;
    }}
    /* Progress bars — thin, BMO blue */
    .stProgress {{ margin: 0.15rem 0 !important; }}
    .stProgress > div > div {{ height: 9px !important; }}
    .stProgress > div > div > div > div {{ background-color: {BMO_BLUE} !important; }}
    /* Compact status slider (fillable "not started / in progress / done" bar) */
    .stSlider {{ padding-top: 0.1rem !important; margin-bottom: 0.2rem !important; }}
    .stSlider label {{ font-size: 0.8rem !important; }}
    /* Progress-by cards — solid BMO-tinted background with accent border */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.progress-card-marker) {{
        background-color: #EAF4FB !important;
        border: 1px solid {BMO_BLUE} !important;
        border-left: 5px solid {BMO_BLUE} !important;
    }}
    .progress-title {{
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: {BMO_BLUE_DARK} !important;
        margin: 0 0 0.3rem 0 !important;
    }}
    /* Section-header badge — same visual language as the tab labels above
       (solid BMO navy pill, bold white text) so section titles like
       "Progress" read as a matching part of the same design system. */
    .section-badge {{
        display: inline-block;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.02em;
        color: #FFFFFF !important;
        background-color: {BMO_BLUE_DARK};
        padding: 8px 22px;
        border-radius: 8px;
        margin: 0 0 1.3rem 0 !important;
    }}
    .progress-label {{
        font-size: 0.95rem !important;
        color: #333333 !important;
        display: block;
        margin: 0.4rem 0 0.15rem 0 !important;
    }}
    .progress-pct {{
        font-weight: 700 !important;
        color: {BMO_BLUE_DARK} !important;
    }}
    /* Logbook notepad — plain white writing area */
    .stTextArea textarea {{
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        font-size: 1.02rem !important;
        line-height: 1.7 !important;
        padding: 1rem !important;
        border: 1px solid #E1DFDD !important;
        border-radius: 6px !important;
    }}
    /* Ensure text stays dark/readable regardless of OS dark-mode preference */
    body, p, span, div, label {{ color: #1A1A1A; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Anchored to this script's own folder — guarantees progress.json is always
# read/written from the same place (TrainTrack/progress.json), no matter
# where the app is launched from (VS Code, a terminal at the repo root,
# Streamlit Cloud, etc). A plain "progress.json" relative path is what
# caused two divergent copies to appear in the repo (2026-08-14).
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress.json")
GENERAL_START_DEFAULT = date(2026, 8, 1)

# ---------------------------------------------------------------------------
# Data model — training curriculum: 3 products × 4 tracks
#
# Each item: id (unique within the platform), track, a *compact* name,
# a short desc (shown smaller/lighter under the name), and hours.
# There is no manual "weight" to keep in sync anymore — progress is
# weighted by `hours` automatically, so nothing can drift out of 100%.
#
# Optional `priority` field ("focus" / "deprioritize", omitted = neutral):
# added 2026-08-14 from Mike Freed's stakeholder guidance on where to spend
# time first within the existing curriculum. Purely a display/ordering hint
# — it does not touch item `id`, does not add/remove modules, and does not
# affect the hours-weighted progress math or stored progress.json keys.
# ---------------------------------------------------------------------------

TRACKS = ["User", "Supervisor", "Administrator", "Support Engineer"]

PLATFORM_ITEMS = {
    "UIP": [
        # User — 7h
        {"id": 1, "track": "User", "name": "Agent Interface (UAD)",
         "desc": "Login, status, transfer and conference calls", "hours": 2,
         "priority": "focus"},
        {"id": 2, "track": "User", "name": "Multichannel Support",
         "desc": "Voice, chat and callback in a single interaction flow", "hours": 3},
        {"id": 3, "track": "User", "name": "Unified Director",
         "desc": "Day-to-day use of the agent softphone", "hours": 2,
         "priority": "focus"},
        # Supervisor — 8h
        {"id": 4, "track": "Supervisor", "name": "URM Dashboard",
         "desc": "Real-time panel — queues, agents and SLAs", "hours": 3},
        {"id": 5, "track": "Supervisor", "name": "Team Management",
         "desc": "Escalation, barge-in/whisper and operational reports", "hours": 3},
        {"id": 6, "track": "Supervisor", "name": "Quick UCC-Admin",
         "desc": "Quick adjustments to routes and queues", "hours": 2},
        # Administrator — 22h
        {"id": 7, "track": "Administrator", "name": "General Architecture",
         "desc": "Core Server, DCP/TMS, Broker, URM and call flow", "hours": 3},
        {"id": 8, "track": "Administrator", "name": "Routing (ACD)",
         "desc": "ACD configuration and dial plans", "hours": 3},
        {"id": 9, "track": "Administrator", "name": "M3 Designer — Fundamentals",
         "desc": "IVR fundamentals with M3 Designer", "hours": 3,
         "priority": "deprioritize"},
        {"id": 10, "track": "Administrator", "name": "M3 Advanced",
         "desc": "Multi-document scripts and database integration", "hours": 3,
         "priority": "deprioritize"},
        {"id": 11, "track": "Administrator", "name": "Chat and Web Callback",
         "desc": "Configuring chat and web callback channels", "hours": 2,
         "priority": "deprioritize"},
        {"id": 12, "track": "Administrator", "name": "Enterprise Routing",
         "desc": "IPNIQ, Broker and cross-site routing", "hours": 3},
        {"id": 13, "track": "Administrator", "name": "UCC-Admin and URM",
         "desc": "Administration via UCC-Admin and Unified Resource Manager", "hours": 3},
        {"id": 14, "track": "Administrator", "name": "Security and Licensing",
         "desc": "Security, licensing and user management", "hours": 2,
         "priority": "deprioritize"},
        # Support Engineer — 17h
        {"id": 15, "track": "Support Engineer", "name": "Infrastructure and Network",
         "desc": "UIP infrastructure and network architecture", "hours": 3},
        {"id": 16, "track": "Support Engineer", "name": "Installation",
         "desc": "Installation and use of the Server Configurator", "hours": 3,
         "priority": "deprioritize"},
        {"id": 17, "track": "Support Engineer", "name": "Upgrade Process",
         "desc": "Upgrade prerequisites and troubleshooting", "hours": 3,
         "priority": "deprioritize"},
        {"id": 18, "track": "Support Engineer", "name": "Diagnostics",
         "desc": "Logs, Performance Monitor and network tools", "hours": 3},
        {"id": 19, "track": "Support Engineer", "name": "HA and DR/Failover",
         "desc": "High availability and disaster recovery/failover", "hours": 2},
        {"id": 20, "track": "Support Engineer", "name": "Enterprise Integration",
         "desc": "Integrated view of UIP + ALM + AQM + UCC-Admin", "hours": 3},
    ],
    "ALM": [
        # User — 2h
        {"id": 1, "track": "User", "name": "Outbound Operation",
         "desc": "Contacts and dispositions in outbound campaigns", "hours": 2,
         "priority": "focus"},
        # Supervisor — 4h
        {"id": 2, "track": "Supervisor", "name": "Real-Time Monitoring",
         "desc": "CPS and queues for outbound campaigns", "hours": 2},
        {"id": 3, "track": "Supervisor", "name": "List Management",
         "desc": "Contact lists and disposition rules", "hours": 2,
         "priority": "focus"},
        # Administrator — 8h
        {"id": 4, "track": "Administrator", "name": "Campaign Concepts",
         "desc": "Lists, dialers and Optimizer", "hours": 3},
        {"id": 5, "track": "Administrator", "name": "Campaign Configuration",
         "desc": "Contact rules and DNC compliance", "hours": 3},
        {"id": 6, "track": "Administrator", "name": "ALM ↔ UIP Integration",
         "desc": "Integration with UIP and databases", "hours": 2,
         "priority": "focus"},
        # Support Engineer — 9h
        {"id": 7, "track": "Support Engineer", "name": "Service Architecture",
         "desc": "QLE, QOP, QHD queues and Watchdog", "hours": 3},
        {"id": 8, "track": "Support Engineer", "name": "Installation and HA",
         "desc": "Installation, DFS Replication and high availability", "hours": 3,
         "priority": "deprioritize"},
        {"id": 9, "track": "Support Engineer", "name": "Troubleshooting",
         "desc": "sqlcmd, performance counters and logs", "hours": 3},
    ],
    "AQM": [
        # User — 2h
        {"id": 1, "track": "User", "name": "Desktop Client",
         "desc": "On-demand recording and self-evaluation", "hours": 2},
        # Supervisor/Mentor — 9h
        {"id": 2, "track": "Supervisor", "name": "Live Monitor",
         "desc": "Real-time monitoring and evaluation creation", "hours": 2,
         "priority": "focus"},
        {"id": 3, "track": "Supervisor", "name": "Scorecards",
         "desc": "Searching, playback and scoring of recordings", "hours": 3},
        {"id": 4, "track": "Supervisor", "name": "Mentor Calibration",
         "desc": "Calibration and peer review", "hours": 2},
        {"id": 5, "track": "Supervisor", "name": "Reports and Trends",
         "desc": "Reports and trend analysis", "hours": 2,
         "priority": "deprioritize"},
        # Administrator — 11h
        {"id": 6, "track": "Administrator", "name": "Fundamentals and Lifecycle",
         "desc": "Plan → record → review → report", "hours": 2,
         "priority": "focus"},
        {"id": 7, "track": "Administrator", "name": "Users and Access",
         "desc": "Rights and memberships — Agent/Skill Group, Team", "hours": 2,
         "priority": "focus"},
        {"id": 8, "track": "Administrator", "name": "Recording Rules",
         "desc": "Recording rules and scorecard templates", "hours": 3},
        {"id": 9, "track": "Administrator", "name": "CMQ",
         "desc": "Customer Measured Quality — surveys and invitation rules", "hours": 2},
        {"id": 10, "track": "Administrator", "name": "AQM ↔ UIP Integration",
         "desc": "Data sync and recording statistics", "hours": 2,
         "priority": "focus"},
        # Support Engineer — 10h
        {"id": 11, "track": "Support Engineer", "name": "Architecture and Config Utility",
         "desc": "Architecture and Desktop Client Configuration Utility", "hours": 3},
        {"id": 12, "track": "Support Engineer", "name": "DTC Installation",
         "desc": "Desktop Client installation (DTC Install)", "hours": 2},
        {"id": 13, "track": "Support Engineer", "name": "Troubleshooting",
         "desc": "Storage paths, transcoding and performance", "hours": 3},
        {"id": 14, "track": "Support Engineer", "name": "Maintenance and Patches",
         "desc": "Maintenance and hotfix application", "hours": 2,
         "priority": "deprioritize"},
    ],
}

STATUS_VALUE = {"Not started": 0, "In progress": 50, "Done": 100}

# Sort order for priority tags within a track: Focus first, neutral (no tag)
# in the middle, Deprioritize last. Python's sort is stable, so modules
# sharing a priority keep their original curriculum order among themselves.
PRIORITY_RANK = {"focus": 0, "deprioritize": 2}
PRIORITY_BADGE = {
    "focus": ("CCS Priority", "priority-focus"),
    "deprioritize": ("Later", "priority-later"),
}


def sort_by_priority(items):
    return sorted(items, key=lambda i: PRIORITY_RANK.get(i.get("priority"), 1))


# ---------------------------------------------------------------------------
# Verint Academy — data pulled from the Cornerstone/Verint LMS dashboard.
# Two curricula, each a list of modules with a simple Done / Not done toggle
# (not the 3-state slider used above). Where the LMS gave per-module minutes
# we kept them (`hours`); where it only gave a lesson-count fraction (e.g.
# "1/2") we don't have real hours, so `hours` is None and that curriculum
# falls back to equal-weight-per-module progress. The two curricula are then
# combined into the single "Verint WFO" gauge using Verint's own reported
# "Total Duration" per curriculum as the weight.
# ---------------------------------------------------------------------------

VERINT_CURRICULA = [
    "Partner Implementation Curriculum",
    "WFO 15 Enterprise User Management",
]

VERINT_TOTAL_HOURS = {
    "Partner Implementation Curriculum": 229 + 40 / 60,   # 229h 40m, as reported by Verint
    "WFO 15 Enterprise User Management": 11 + 50 / 60,     # 11h 50m, as reported by Verint
}

VERINT_ITEMS = {
    "Partner Implementation Curriculum": [
        {"id": 1, "name": "Accessing the Verint Training Labs [VU01]",
         "desc": "Lab access orientation", "hours": 2.0, "done": True},
        {"id": 2, "name": "Enterprise: Core Installation - On-Premise",
         "desc": "On-premise core installation", "hours": None, "done": False},
        {"id": 3, "name": "Enterprise: System Administration",
         "desc": "Enterprise system administration", "hours": None, "done": False},
        {"id": 4, "name": "Enterprise Authentication: SSO & LDAP Configuration",
         "desc": "Authentication via SSO and LDAP", "hours": None, "done": False},
        {"id": 5, "name": "Enterprise Authentication SAML Configuration",
         "desc": "Authentication via SAML", "hours": None, "done": False},
        {"id": 6, "name": "Enterprise Security: TLS/SSL Configuration",
         "desc": "Enterprise security — TLS/SSL", "hours": None, "done": False},
        {"id": 7, "name": "Encryption: Thales KMS",
         "desc": "Encryption key management with Thales KMS", "hours": None, "done": False},
        {"id": 8, "name": "Enterprise: User Management",
         "desc": "1 of 2 lessons completed (per Verint LMS)", "hours": None, "done": False},
        {"id": 9, "name": "Recording and Archive Configuration",
         "desc": "Recording and archive setup", "hours": None, "done": False},
        {"id": 10, "name": "Recording System Administration",
         "desc": "Recording system administration", "hours": None, "done": False},
        {"id": 11, "name": "Import/Export Manager Configuration",
         "desc": "0 of 2 lessons completed (per Verint LMS)", "hours": None, "done": False},
        {"id": 12, "name": "Quality Management (QM)/Interactions Overview",
         "desc": "0 of 1 lesson completed (per Verint LMS)", "hours": None, "done": False},
        {"id": 13, "name": "Quality Management (QM) Administration",
         "desc": "0 of 1 lesson completed (per Verint LMS)", "hours": None, "done": False},
        {"id": 14, "name": "Form Designer",
         "desc": "0 of 2 lessons completed (per Verint LMS)", "hours": None, "done": False},
        {"id": 15, "name": "Automated Quality Management - AQM",
         "desc": "0 of 1 lesson completed (per Verint LMS)", "hours": None, "done": False},
        {"id": 16, "name": "WFO Reporting",
         "desc": "0 of 1 lesson completed (per Verint LMS)", "hours": None, "done": False},
        {"id": 17, "name": "Performance Management - Scorecard Administration",
         "desc": "0 of 1 lesson completed (per Verint LMS)", "hours": None, "done": False},
        {"id": 18, "name": "Performance Management - Scorecard Configuration",
         "desc": "0 of 4 lessons completed (per Verint LMS)", "hours": None, "done": False},
        {"id": 19, "name": "Post-Curriculum Completion Activities",
         "desc": "Wrap-up activities after curriculum completion", "hours": None, "done": False},
    ],
    "WFO 15 Enterprise User Management": [
        {"id": 1, "name": "What is User Management",
         "desc": "WFO-SE-EUM-152-01", "hours": 0.5, "done": False},
        {"id": 2, "name": "Organisations",
         "desc": "WFO-SE-EUM-152-02", "hours": 0.75, "done": False},
        {"id": 3, "name": "Job Titles and Employee Types",
         "desc": "WFO-SE-EUM-152-03 · New", "hours": 0.25, "done": False},
        {"id": 4, "name": "Roles and Privileges",
         "desc": "WFO-SE-EUM-152-04", "hours": 1.5, "done": False},
        {"id": 5, "name": "Setting Self-Identification Criteria",
         "desc": "WFO-SE-EUM-152-05", "hours": 1 / 3, "done": False},
        {"id": 6, "name": "Groups",
         "desc": "WFO-SE-EUM-152-06", "hours": 0.75, "done": False},
        {"id": 7, "name": "User Defined Fields",
         "desc": "WFO-SE-EUM-152-07", "hours": 0.75, "done": False},
        {"id": 8, "name": "Employee Information",
         "desc": "WFO-SE-EUM-152-08", "hours": 1.0, "done": False},
        {"id": 9, "name": "Accessing the Verint Training Labs [VU01]",
         "desc": "Lab access for this curriculum", "hours": 0.0, "done": False},
        {"id": 10, "name": "WFO 15 Enterprise User Management - Hands on Lab",
         "desc": "Self-paced hands-on lab (WFO-15-EUM)", "hours": 6.0, "done": False},
        {"id": 11, "name": "Post-Curriculum Completion Activities",
         "desc": "Wrap-up activities after curriculum completion", "hours": 0.0, "done": False},
    ],
}

# Curricula whose modules have real per-item hours use hours-weighted progress;
# the rest (only a lesson-count fraction was available) fall back to counting
# modules toggled Done out of the total, equally weighted.
VERINT_HOURS_WEIGHTED = {"WFO 15 Enterprise User Management"}


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_progress(data):
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        st.error(f"Could not save progress: {e}")


if "progress" not in st.session_state:
    st.session_state.progress = load_progress()


def item_key(platform, item_id):
    return f"{platform}:{item_id}"


def get_status(platform, item_id):
    return st.session_state.progress.get(item_key(platform, item_id), "Not started")


def set_status(platform, item_id, status):
    st.session_state.progress[item_key(platform, item_id)] = status
    save_progress(st.session_state.progress)


def get_general_start():
    raw = st.session_state.progress.get("general_start")
    if raw:
        try:
            return date.fromisoformat(raw)
        except Exception:
            pass
    return GENERAL_START_DEFAULT


def set_general_start(value):
    st.session_state.progress["general_start"] = value.isoformat()
    save_progress(st.session_state.progress)


def get_logbook_text():
    return st.session_state.progress.get("logbook_text", "")


def set_logbook_text(value):
    st.session_state.progress["logbook_text"] = value
    st.session_state.progress["logbook_updated"] = now_toronto_str()
    save_progress(st.session_state.progress)


def get_logbook_updated():
    return st.session_state.progress.get("logbook_updated")


# Matches Fabio's Logbook line format, e.g.:
#   • [2026-07-23] - [CCS - Aspect/Alvaria] - Participated in ... - Learning: ...
# The bullet/dash before the date is optional so the pattern still catches a
# line even if it's typed without it — only the [YYYY-MM-DD] at (or near) the
# start of the line is required.
LOGBOOK_DATE_RE = re.compile(r"^\s*[•\-]?\s*\[(\d{4}-\d{2}-\d{2})\]")


def sort_logbook_text(text, ascending):
    """Reorders dated entry lines by the [YYYY-MM-DD] at their start.

    Lines that don't match the pattern (blank lines, freeform notes without a
    date) are left untouched and kept together, ahead of the sorted dated
    lines — they're never reordered or dropped, just not part of the sort.
    Same-date lines keep their original relative order (stable sort).
    """
    lines = text.split("\n")
    dated, other = [], []
    for line in lines:
        match = LOGBOOK_DATE_RE.match(line)
        if match:
            dated.append((match.group(1), line))
        else:
            other.append(line)
    dated.sort(key=lambda pair: pair[0], reverse=not ascending)
    sorted_lines = [line for _, line in dated]
    return "\n".join(other + sorted_lines) if other else "\n".join(sorted_lines)


def verint_key(curriculum, item_id):
    return f"verint:{curriculum}:{item_id}"


def get_verint_done(curriculum, item_id):
    key = verint_key(curriculum, item_id)
    if key in st.session_state.progress:
        return st.session_state.progress[key]
    # Not toggled locally yet — fall back to the snapshot pulled from Verint's LMS.
    item = next(i for i in VERINT_ITEMS[curriculum] if i["id"] == item_id)
    return item["done"]


def set_verint_done(curriculum, item_id, value):
    st.session_state.progress[verint_key(curriculum, item_id)] = value
    save_progress(st.session_state.progress)


# ---------------------------------------------------------------------------
# Calculations — everything is weighted by `hours`, so there is no manual
# percentage to keep summing to 100 anymore.
# ---------------------------------------------------------------------------

def items_by_track(platform):
    grouped = {t: [] for t in TRACKS}
    for i in PLATFORM_ITEMS[platform]:
        grouped[i["track"]].append(i)
    return grouped


def weighted_progress(items, platform):
    total = sum(i["hours"] for i in items)
    if not total:
        return 0.0
    earned = sum(i["hours"] * STATUS_VALUE[get_status(platform, i["id"])] / 100 for i in items)
    return round(earned / total * 100, 1)


def platform_progress(platform):
    return weighted_progress(PLATFORM_ITEMS[platform], platform)


def total_hours(platform=None):
    if platform:
        return sum(i["hours"] for i in PLATFORM_ITEMS[platform])
    return sum(i["hours"] for items in PLATFORM_ITEMS.values() for i in items)


def overall_progress():
    all_pairs = [(p, i) for p, items in PLATFORM_ITEMS.items() for i in items]
    grand_total = sum(i["hours"] for p, i in all_pairs)
    if not grand_total:
        return 0.0
    earned = sum(i["hours"] * STATUS_VALUE[get_status(p, i["id"])] / 100 for p, i in all_pairs)
    return round(earned / grand_total * 100, 1)


def format_duration(hours):
    total_minutes = round(hours * 60)
    h, m = divmod(total_minutes, 60)
    return f"{h}h {m}m" if m else f"{h}h"


def curriculum_progress(curriculum):
    items = VERINT_ITEMS[curriculum]
    if not items:
        return 0.0
    if curriculum in VERINT_HOURS_WEIGHTED:
        total = sum(i["hours"] for i in items)
        if not total:
            return 0.0
        earned = sum(i["hours"] for i in items if get_verint_done(curriculum, i["id"]))
        return round(earned / total * 100, 1)
    # No reliable per-module hours — count modules toggled Done, equally weighted.
    done = sum(1 for i in items if get_verint_done(curriculum, i["id"]))
    return round(done / len(items) * 100, 1)


def verint_overall_progress():
    total_h = sum(VERINT_TOTAL_HOURS.values())
    if not total_h:
        return 0.0
    earned = sum(curriculum_progress(c) / 100 * VERINT_TOTAL_HOURS[c] for c in VERINT_CURRICULA)
    return round(earned / total_h * 100, 1)


def make_gauge(value, title, bar_color="#FFFFFF", bg_color=BMO_BLUE_DARK):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": "%", "font": {"size": 30, "color": "#FFFFFF"}},
        title={"text": title, "font": {"size": 15, "color": "#FFFFFF"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#FFFFFF",
                      "tickfont": {"size": 10, "color": "#FFFFFF"}},
            "bar": {"color": bar_color, "thickness": 0.35},
            "bgcolor": "rgba(255,255,255,0.12)",
            "borderwidth": 0,
            "steps": [{"range": [0, 100], "color": "rgba(255,255,255,0.12)"}],
        },
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=25, r=25, t=55, b=15),
        paper_bgcolor=bg_color,
        font={"family": "Segoe UI, sans-serif"},
    )
    return fig


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def render_module_grid(items, get_done, set_done, key_prefix, hours_fmt=None, per_row=4):
    """Compact module cards, `per_row` to a row instead of one full-width row each."""
    for row_start in range(0, len(items), per_row):
        row_items = items[row_start:row_start + per_row]
        cols = st.columns(per_row)
        for col, i in zip(cols, row_items):
            with col:
                with st.container(border=True):
                    current_done = get_done(i)
                    if current_done:
                        st.markdown("<div class='card-done-marker'></div>", unsafe_allow_html=True)
                    badge_html = ""
                    priority = i.get("priority")
                    if priority in PRIORITY_BADGE:
                        label, css_class = PRIORITY_BADGE[priority]
                        badge_html = f"<span class='priority-badge {css_class}'>{label}</span>"
                    st.markdown(
                        f"<div class='item-name'>{i['name']}{badge_html}</div>",
                        unsafe_allow_html=True,
                    )
                    caption = i["desc"]
                    if i.get("hours") and hours_fmt:
                        caption = f"{caption} · {hours_fmt(i['hours'])}"
                    st.caption(caption)
                    new_done = st.toggle(
                        "Done", value=current_done,
                        key=f"{key_prefix}_{i['id']}", label_visibility="collapsed",
                        disabled=not EDIT_UNLOCKED,
                    )
                    if new_done != current_done:
                        set_done(i, new_done)
                        st.rerun()


def render_platform_tab(platform):
    prog = platform_progress(platform)
    p_hours = total_hours(platform)
    grand_total = total_hours()
    share = round(p_hours / grand_total * 100, 1) if grand_total else 0.0

    st.subheader(f"{platform} — {p_hours}h ({share}% of total training)")
    st.progress(prog / 100, text=f"{prog}% complete")

    grouped = items_by_track(platform)
    for track in TRACKS:
        t_items = grouped.get(track, [])
        if not t_items:
            continue
        t_hours = sum(i["hours"] for i in t_items)
        t_prog = weighted_progress(t_items, platform)

        st.markdown(f"<div class='progress-title' style='margin-top:1.1rem;'>{track}</div>", unsafe_allow_html=True)
        st.caption(f"{len(t_items)} modules · {t_hours}h")
        st.progress(t_prog / 100, text=f"{t_prog}%")

        render_module_grid(
            sort_by_priority(t_items),
            get_done=lambda i: get_status(platform, i["id"]) == "Done",
            set_done=lambda i, v: set_status(platform, i["id"], "Done" if v else "Not started"),
            key_prefix=f"stat_{platform}",
            hours_fmt=lambda h: f"{h}h",
        )


# ---------------------------------------------------------------------------
# Access — the app is view-only by default. Editing unlocks only when the
# correct password is entered, matched against a Streamlit Secret named
# `edit_password` (Settings → Secrets on Streamlit Cloud, or a local
# .streamlit/secrets.toml when running on your own machine). The password is
# never stored in this file, so it's safe even with a public GitHub repo. If
# no `edit_password` secret is configured for a given deployment, that
# deployment stays permanently view-only — handy for a "boss link" you never
# want editable at all.
# ---------------------------------------------------------------------------

try:
    EDIT_PASSWORD = st.secrets.get("edit_password")
except Exception:
    EDIT_PASSWORD = None

if "edit_unlocked" not in st.session_state:
    st.session_state.edit_unlocked = False

with st.sidebar:
    st.markdown("### Access")
    if st.session_state.edit_unlocked:
        st.success("Editing unlocked")
    elif EDIT_PASSWORD:
        pwd = st.text_input("Password to unlock editing", type="password", key="edit_pwd_input")
        if pwd:
            if pwd == EDIT_PASSWORD:
                st.session_state.edit_unlocked = True
                st.rerun()
            else:
                st.error("Wrong password")
    else:
        st.caption("View-only — no edit password configured for this deployment.")

    st.markdown("---")
    st.markdown("### Backup")
    st.caption(
        "Progress lives on this app's own server disk, not in GitHub. Download a "
        "copy here before pushing new code or redeploying — a redeploy resets this "
        "app's disk to whatever is currently committed in the repo."
    )
    st.download_button(
        "Download progress.json",
        data=json.dumps(st.session_state.progress, indent=2, ensure_ascii=False),
        file_name="progress_backup.json",
        mime="application/json",
    )

EDIT_UNLOCKED = st.session_state.edit_unlocked


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

st.title("UIP · ALM · AQM — Training Track Dashboard")
st.caption("BMO / Connexservice · Aspect / Alvaria Unified IP 7.4 SP2 · Fabio Prumucena — Aspect/Alvaria Specialist | BMO CCS | Connex")

tab_overview, tab_uip, tab_alm, tab_aqm, tab_verint, tab_logbook = st.tabs(
    ["Overview", "UIP", "ALM", "AQM", "Verint Academy", "Logbook"]
)

with tab_overview:
    overall = overall_progress()

    # First time the whole track hits 100%, freeze that date as "general end".
    if overall >= 100 and not st.session_state.progress.get("general_end"):
        st.session_state.progress["general_end"] = date.today().isoformat()
        save_progress(st.session_state.progress)
    general_end_raw = st.session_state.progress.get("general_end")

    with st.container(border=True):
        gcol1, gcol2, gcol3 = st.columns([1, 1, 2])
        with gcol1:
            st.markdown("<span class='col-header'>General start</span>", unsafe_allow_html=True)
            g_start = st.date_input("General start", value=get_general_start(),
                                     key="general_start_input", label_visibility="collapsed",
                                     disabled=not EDIT_UNLOCKED)
            if g_start != get_general_start():
                set_general_start(g_start)
        with gcol2:
            st.markdown("<span class='col-header'>General end</span>", unsafe_allow_html=True)
            if general_end_raw:
                g_end = date.fromisoformat(general_end_raw)
                st.markdown(
                    f"<span style='font-size:1rem;font-weight:700;'>{g_end.strftime('%b %d, %Y')}</span> "
                    f"<span class='status-badge status-completed'>COMPLETED</span>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<span style='font-size:1rem;'>—</span> "
                    "<span class='status-badge status-pending'>PENDING</span>",
                    unsafe_allow_html=True,
                )
        with gcol3:
            st.caption(
                "General end auto-fills the first time the whole track (all products, "
                "weighted by hours) reaches 100%."
            )

    with st.container(border=True):
        st.markdown("<div class='progress-card-marker'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-badge'>Progress</div>",
            unsafe_allow_html=True,
        )
        gauges = [
            ("Overall", overall, BMO_BLUE_DARK),
            ("UIP", platform_progress("UIP"), BMO_BLUE),
            ("ALM", platform_progress("ALM"), BMO_GRAY_DEEP),
            ("AQM", platform_progress("AQM"), BMO_RED_DEEP),
            ("Verint WFO", verint_overall_progress(), BMO_RED),
        ]
        gcols = st.columns(len(gauges))
        for gc, (label, value, color) in zip(gcols, gauges):
            with gc:
                st.plotly_chart(
                    make_gauge(value, label, bar_color="#FFFFFF", bg_color=color),
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"gauge_{label.replace(' ', '_').lower()}",
                )

with tab_uip:
    st.caption(
        "These are the main topics according to the official documentation. Note: I wasn't able to "
        "follow through Aspect's official training platform, so this curriculum was built independently "
        "from the docs instead."
    )
    render_platform_tab("UIP")

with tab_alm:
    render_platform_tab("ALM")

with tab_aqm:
    render_platform_tab("AQM")

with tab_logbook:
    with st.container(border=True):
        current_text = get_logbook_text()

        top = st.columns([3, 1, 1.3])
        with top[0]:
            st.markdown("<div class='progress-title'>Logbook</div>", unsafe_allow_html=True)
        with top[1]:
            last_updated = get_logbook_updated()
            if last_updated:
                st.caption(f"Last edited: {last_updated}")
        with top[2]:
            st.download_button(
                "Download Logbook",
                data=current_text,
                file_name=f"logbook_{date.today().isoformat()}.txt",
                mime="text/plain",
                disabled=not current_text,
            )

        st.caption(
            "A large part of this training has actually happened outside of formal modules — "
            "shadowing colleagues, reading Confluence articles, getting guidance and clarifying "
            "doubts with the CSS team, and above all working directly on tickets, cases, and "
            "incidents. This log is meant to capture some of the most significant ones."
        )

        # Tracks which sort direction was last clicked, purely so the matching
        # button can stay highlighted (see .sort-btn-active CSS above). Session-
        # only — resets on page reload, doesn't need to live in progress.json.
        st.session_state.setdefault("logbook_sort_dir", None)

        sort_cols = st.columns([1.3, 1.3, 4])
        with sort_cols[0]:
            if st.session_state["logbook_sort_dir"] == "asc":
                st.markdown("<div class='sort-btn-active'></div>", unsafe_allow_html=True)
            if st.button("↑ Oldest first", disabled=not EDIT_UNLOCKED or not current_text,
                         use_container_width=True):
                sorted_text = sort_logbook_text(current_text, ascending=True)
                set_logbook_text(sorted_text)
                # The text_area below is keyed "logbook_textarea" — once rendered,
                # Streamlit shows whatever is in st.session_state["logbook_textarea"]
                # and ignores the `value=` we pass it on later reruns. Without this
                # line the sort saves correctly but the box keeps showing the old
                # (unsorted) text until the user clicks into it. Setting the keyed
                # session_state entry directly before rerunning is what makes the
                # box actually refresh.
                st.session_state["logbook_textarea"] = sorted_text
                st.session_state["logbook_sort_dir"] = "asc"
                st.rerun()
        with sort_cols[1]:
            if st.session_state["logbook_sort_dir"] == "desc":
                st.markdown("<div class='sort-btn-active'></div>", unsafe_allow_html=True)
            if st.button("↓ Newest first", disabled=not EDIT_UNLOCKED or not current_text,
                         use_container_width=True):
                sorted_text = sort_logbook_text(current_text, ascending=False)
                set_logbook_text(sorted_text)
                st.session_state["logbook_textarea"] = sorted_text
                st.session_state["logbook_sort_dir"] = "desc"
                st.rerun()
        with sort_cols[2]:
            st.caption(
                "Sorts lines starting with a [YYYY-MM-DD] date. Any line without one "
                "(blank lines, freeform notes) is left as-is, grouped above the sorted entries."
            )

        new_text = st.text_area(
            "Logbook",
            value=current_text,
            height=560,
            key="logbook_textarea",
            label_visibility="collapsed",
            placeholder="Write freely here — daily notes, case details, anything worth remembering...",
            disabled=not EDIT_UNLOCKED,
        )
        if new_text != current_text:
            set_logbook_text(new_text)
            st.rerun()

with tab_verint:
    st.caption(
        "Courses from Verint's official partner training platform — "
        "[verintconnect.com/learn](https://verintconnect.com/learn)"
    )

    for curriculum in VERINT_CURRICULA:
        items = VERINT_ITEMS[curriculum]
        prog = curriculum_progress(curriculum)

        st.markdown(f"<div class='progress-title' style='margin-top:1.1rem;'>{curriculum}</div>", unsafe_allow_html=True)
        st.caption(f"{len(items)} modules · {format_duration(VERINT_TOTAL_HOURS[curriculum])} total")
        st.progress(prog / 100, text=f"{prog}% complete")

        render_module_grid(
            items,
            get_done=lambda i: get_verint_done(curriculum, i["id"]),
            set_done=lambda i, v: set_verint_done(curriculum, i["id"], v),
            key_prefix=f"verint_{curriculum}",
            hours_fmt=format_duration,
        )

st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
st.caption(f"Last saved: {now_toronto_str()} · Progress stored in {PROGRESS_FILE}")