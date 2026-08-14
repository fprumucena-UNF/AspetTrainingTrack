import streamlit as st
import json
import os
from datetime import datetime, date
import plotly.graph_objects as go

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
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        color: {BMO_BLUE_DARK} !important;
        margin: 0 0 0.4rem 0 !important;
    }}
    .item-weight {{
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: {BMO_BLUE} !important;
    }}
    .priority-badge {{
        font-size: 0.85rem !important;
        padding: 3px 11px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
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
    [data-testid="stCaptionContainer"] {{ font-size: 0.88rem !important; margin: 0.15rem 0 0 0 !important; }}
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
    /* Checkbox text */
    .stCheckbox label p {{ font-size: 1rem !important; }}
    /* Progress-by cards — solid BMO-tinted background with accent border */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.progress-card-marker) {{
        background-color: #EAF4FB !important;
        border: 1px solid {BMO_BLUE} !important;
        border-left: 5px solid {BMO_BLUE} !important;
    }}
    .progress-title {{
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: {BMO_BLUE_DARK} !important;
        margin: 0 0 0.5rem 0 !important;
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
    /* Journal entry tag badges */
    .tag-badge {{
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        padding: 2px 9px !important;
        border-radius: 8px !important;
        background-color: {BMO_LIGHT_BLUE}33 !important;
        color: {BMO_BLUE_DARK} !important;
        margin-right: 4px !important;
        display: inline-block;
    }}
    /* Ensure text stays dark/readable regardless of OS dark-mode preference */
    body, p, span, div, label {{ color: #1A1A1A; }}
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
    </style>
    """,
    unsafe_allow_html=True,
)

PROGRESS_FILE = "progress.json"
GENERAL_START_DEFAULT = date(2026, 8, 1)

# ---------------------------------------------------------------------------
# Data model — sourced directly from Training_Track_UIP_ALM_AQM.docx
# ---------------------------------------------------------------------------

PLATFORM_WEIGHTS = {"UIP": 35, "ALM": 35, "AQM": 30}

PLATFORM_ITEMS = {
    "UIP": [
        {"id": 1, "name": "General architecture (Core Server, CenterCord, CC2DCP, Alert Server, Import/Export, DBI)",
         "weight": 10, "priority": "Base", "note": "Review — you already know most of this"},
        {"id": 2, "name": "HA per component (independent failover, quorum vs. AlwaysOn+FSW)",
         "weight": 15, "priority": "High", "note": "Reinforce with the PRB0068431 case"},
        {"id": 3, "name": "LDAP / Integrated Authentication (Windows Logon + Domain)",
         "weight": 10, "priority": "Medium", "note": "Recurring in login troubleshooting"},
        {"id": 4, "name": "Certificate management (LDAP/AD root, Tomcat Portal, UCCAdmin)",
         "weight": 15, "priority": "High", "note": "Tied to the URM case 01607749"},
        {"id": 5, "name": "M3 (IVR scripting) — script / service / server",
         "weight": 20, "priority": "High", "note": "New area — highest time investment"},
        {"id": 6, "name": "Unified Director / UCCAdmin (Adapter, Server, Enterprise DB)",
         "weight": 15, "priority": "Medium", "note": "Central multi-site administration"},
        {"id": 7, "name": "Enterprise deployment rules (upgrade, backup/recovery, add/remove sites)",
         "weight": 10, "priority": "Medium", "note": "Relevant for CAB / change control"},
        {"id": 8, "name": "Alerts and severities (Alert Server, message catalog)",
         "weight": 5, "priority": "Low", "note": "Quick reference, not deep study"},
    ],
    "ALM": [
        {"id": 1, "name": "Components (Primary Server, Business Objects Server, Reporting DB Server)",
         "weight": 10, "priority": "High", "note": "Starting point — platform new to you"},
        {"id": 2, "name": "Installation types (Stand-Alone, HA, Reporting)",
         "weight": 10, "priority": "Medium", "note": "Understand client topology"},
        {"id": 3, "name": "List Build: Static vs. Dynamic (order, priority, catch-all)",
         "weight": 20, "priority": "High", "note": "Functional core of outbound campaigns"},
        {"id": 4, "name": "AOD Interface (ALM ↔ CenterCord) — certificates and security",
         "weight": 15, "priority": "High", "note": "Connects directly to your cert work on UIP"},
        {"id": 5, "name": "Watchdog + Windows Performance Monitor (almCounter)",
         "weight": 10, "priority": "Medium", "note": "ALM's own diagnostic tool"},
        {"id": 6, "name": "Optimizer (\"lift\") — RPC, contacts per agent-hour",
         "weight": 15, "priority": "Medium", "note": "If BMO uses optimized outbound"},
        {"id": 7, "name": "Backup / DR (DFS Replication for ALM DR)",
         "weight": 10, "priority": "Medium", "note": "Tied to the storage/SAN discussion (PRB0068431)"},
        {"id": 8, "name": "MELDB job schedules (daily / weekly / monthly stored procedures)",
         "weight": 10, "priority": "Low", "note": "Database maintenance"},
    ],
    "AQM": [
        {"id": 1, "name": "AQM architecture (Mentor Server, recording, IMON)",
         "weight": 10, "priority": "Base", "note": "Already deep in this — consolidate"},
        {"id": 2, "name": "Users: mandatory filter by Switch + Role",
         "weight": 10, "priority": "Base", "note": "Already confirmed in production"},
        {"id": 3, "name": "Edit User: Agent Position ID and Switch mapping",
         "weight": 15, "priority": "High", "note": "Next step in the ccs59crds/ccs78crds case"},
        {"id": 4, "name": "Credential model: AD (domain) vs. AQM app admin (Set Password)",
         "weight": 10, "priority": "Medium", "note": "Critical distinction already documented"},
        {"id": 5, "name": "MDC (Mentor Desktop Client) — TLS / Schannel / cipher suites",
         "weight": 20, "priority": "High", "note": "Active in current troubleshooting"},
        {"id": 6, "name": "IMON registration flow (\"process unknown to primary server\")",
         "weight": 15, "priority": "High", "note": "Specific error under investigation now"},
        {"id": 7, "name": "Evaluation forms / Quality scoring (Admin Guide chapters 8-11)",
         "weight": 10, "priority": "Low", "note": "Functional side, not just infrastructure"},
        {"id": 8, "name": "Recording flags and retention policy",
         "weight": 10, "priority": "Medium", "note": "Relevant for compliance in a banking environment"},
    ],
}

PHASES = [
    {"name": "Phase 1 — Foundation", "weight": 25,
     "deliverable": "Consolidated architecture diagram",
     "checklist": ["Architecture diagram drafted (UIP → ALM → AQM topology)",
                   "Diagram validated against documented sources (not inference)"]},
    {"name": "Phase 2 — Deep dive", "weight": 45,
     "deliverable": "Technical notes + DEV/QA testing (one session per 15-20% item)",
     "checklist": None},  # populated dynamically from high-weight items
    {"name": "Phase 3 — Application", "weight": 30,
     "deliverable": "Living documentation updated from real cases",
     "checklist": ["PRB0068431 (HA / storage-SAN)", "URM 01607749 (certificates)",
                   "MDC/IMON active troubleshooting", "ccs59crds/ccs78crds (Edit User mapping)"]},
]

STATUS_OPTIONS = ["Not started", "In progress", "Done"]
STATUS_VALUE = {"Not started": 0, "In progress": 50, "Done": 100}
PRIORITY_COLOR = {"Base": BMO_GRAY, "High": BMO_RED, "Medium": BMO_BLUE, "Low": BMO_LIGHT_BLUE}

ENTRY_TYPES = ["General", "INC", "PRB", "Task"]
TYPE_COLOR = {"General": BMO_GRAY, "INC": BMO_RED, "PRB": "#D68910", "Task": BMO_BLUE}
TAG_OPTIONS = ["UIP", "ALM", "AQM", "Dev", "QA", "PRO"]


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


def checklist_key(phase_name, label):
    return f"phase::{phase_name}::{label}"


def get_check(phase_name, label):
    return st.session_state.progress.get(checklist_key(phase_name, label), False)


def set_check(phase_name, label, value):
    st.session_state.progress[checklist_key(phase_name, label)] = value
    save_progress(st.session_state.progress)


def date_key(platform, item_id, which):
    return f"date:{platform}:{item_id}:{which}"


def get_item_date(platform, item_id, which):
    raw = st.session_state.progress.get(date_key(platform, item_id, which))
    if raw:
        try:
            return date.fromisoformat(raw)
        except Exception:
            return None
    return None


def set_item_date(platform, item_id, which, value):
    key = date_key(platform, item_id, which)
    if value is None:
        st.session_state.progress.pop(key, None)
    else:
        st.session_state.progress[key] = value.isoformat()
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


def notes_key(item_key):
    return f"notes:{item_key}"


def get_notes(item_key):
    return st.session_state.progress.get(notes_key(item_key), [])


def add_note(item_key, note_date, text, note_type="General", tags=None):
    notes = get_notes(item_key)
    notes.append({
        "date": note_date.isoformat() if note_date else "",
        "text": text,
        "type": note_type,
        "tags": tags or [],
    })
    st.session_state.progress[notes_key(item_key)] = notes
    save_progress(st.session_state.progress)


def delete_note(item_key, idx):
    notes = get_notes(item_key)
    if 0 <= idx < len(notes):
        notes.pop(idx)
        st.session_state.progress[notes_key(item_key)] = notes
        save_progress(st.session_state.progress)


def get_logbook_text():
    return st.session_state.progress.get("logbook_text", "")


def set_logbook_text(value):
    st.session_state.progress["logbook_text"] = value
    st.session_state.progress["logbook_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_progress(st.session_state.progress)


def get_logbook_updated():
    return st.session_state.progress.get("logbook_updated")


def all_items_done():
    for platform, items in PLATFORM_ITEMS.items():
        for i in items:
            if get_status(platform, i["id"]) != "Done":
                return False
    return True


def general_end_date():
    """Latest end date across all items — only meaningful once all items are Done."""
    end_dates = []
    for platform, items in PLATFORM_ITEMS.items():
        for i in items:
            d = get_item_date(platform, i["id"], "end")
            if d:
                end_dates.append(d)
    return max(end_dates) if end_dates else None


# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------

def platform_progress(platform):
    items = PLATFORM_ITEMS[platform]
    total_weight = sum(i["weight"] for i in items)
    earned = sum(i["weight"] * STATUS_VALUE[get_status(platform, i["id"])] / 100 for i in items)
    return round(earned / total_weight * 100, 1) if total_weight else 0.0


def overall_progress():
    total = 0.0
    for platform, w in PLATFORM_WEIGHTS.items():
        total += platform_progress(platform) * w / 100
    return round(total, 1)


def high_weight_items():
    """Items weighted 15-20% across all platforms → Phase 2 dedicated sessions."""
    result = []
    for platform, items in PLATFORM_ITEMS.items():
        for i in items:
            if i["weight"] >= 15:
                result.append((platform, i))
    return result


def phase_progress(phase):
    if phase["name"] == "Phase 2 — Deep dive":
        items = high_weight_items()
        if not items:
            return 0.0
        done = sum(1 for p, i in items if get_status(p, i["id"]) == "Done")
        in_prog = sum(1 for p, i in items if get_status(p, i["id"]) == "In progress")
        return round((done * 100 + in_prog * 50) / len(items), 1)
    else:
        checks = phase["checklist"]
        if not checks:
            return 0.0
        done = sum(1 for c in checks if get_check(phase["name"], c))
        return round(done / len(checks) * 100, 1)


def overall_track_progress():
    total = 0.0
    for phase in PHASES:
        total += phase_progress(phase) * phase["weight"] / 100
    return round(total, 1)


def render_notes_section(item_key, form_prefix):
    notes = get_notes(item_key)
    if notes:
        for idx, n in enumerate(notes):
            with st.container(border=True):
                top = st.columns([1, 1, 3.3, 0.5])
                with top[0]:
                    st.caption(n.get("date") or "—")
                with top[1]:
                    ntype = n.get("type", "General")
                    color = TYPE_COLOR.get(ntype, BMO_GRAY)
                    st.markdown(
                        f"<span class='priority-badge' style='background-color:{color}22;color:{color};'>"
                        f"{ntype}</span>",
                        unsafe_allow_html=True,
                    )
                with top[2]:
                    tags = n.get("tags", [])
                    if tags:
                        st.markdown(
                            "".join(f"<span class='tag-badge'>{t}</span>" for t in tags),
                            unsafe_allow_html=True,
                        )
                with top[3]:
                    if st.button("🗑", key=f"del_{form_prefix}_{idx}"):
                        delete_note(item_key, idx)
                        st.rerun()
                st.write(n.get("text", ""))
    else:
        st.caption("No experience or case notes logged yet.")

    with st.form(key=f"form_{form_prefix}", clear_on_submit=True):
        fcols = st.columns([1, 1, 3, 1.5])
        with fcols[0]:
            note_date = st.date_input("Date", value=date.today(), key=f"date_{form_prefix}",
                                       label_visibility="collapsed")
        with fcols[1]:
            note_type = st.selectbox("Type", ENTRY_TYPES, key=f"type_{form_prefix}",
                                      label_visibility="collapsed")
        with fcols[2]:
            note_text = st.text_input(
                "Note", key=f"text_{form_prefix}", label_visibility="collapsed",
                placeholder="Case, ticket #, or hands-on experience related to this topic...",
            )
        with fcols[3]:
            note_tags = st.multiselect(
                "Tags", TAG_OPTIONS, key=f"tags_{form_prefix}", label_visibility="collapsed",
                placeholder="Tags",
            )
        submitted = st.form_submit_button("Add entry")
        if submitted and note_text.strip():
            add_note(item_key, note_date, note_text.strip(), note_type, note_tags)
            st.rerun()


def kpi_tile(label, value, bg_color, text_color="#FFFFFF"):
    return f"""
    <div style='background-color:{bg_color};padding:1.1rem 1.3rem;
                border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,0.15);height:100%;'>
        <div style='color:{text_color};font-size:0.75rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.04em;opacity:0.9;'>{label}</div>
        <div style='color:{text_color};font-size:2.1rem;font-weight:800;margin-top:0.3rem;'>{value}</div>
    </div>
    """


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

def render_platform_tab(platform):
    items = PLATFORM_ITEMS[platform]
    prog = platform_progress(platform)
    st.subheader(f"{platform} — {PLATFORM_WEIGHTS[platform]}% of overall track")
    st.progress(prog / 100, text=f"{prog}% complete")

    for i in items:
        with st.container(border=True):
            st.markdown(f"<div class='item-name'>{i['id']}. {i['name']}</div>", unsafe_allow_html=True)
            st.caption(i["note"])

            ccols = st.columns([1, 1.1, 1.8, 1.3, 1.3])
            with ccols[0]:
                st.markdown("<span class='col-header'>Weight</span>", unsafe_allow_html=True)
                st.markdown(f"<span class='item-weight'>{i['weight']}%</span>", unsafe_allow_html=True)
            with ccols[1]:
                st.markdown("<span class='col-header'>Priority</span>", unsafe_allow_html=True)
                color = PRIORITY_COLOR.get(i["priority"], "#999")
                st.markdown(
                    f"<span class='priority-badge' style='background-color:{color}22;color:{color};'>"
                    f"{i['priority']}</span>",
                    unsafe_allow_html=True,
                )
            with ccols[2]:
                st.markdown("<span class='col-header'>Status</span>", unsafe_allow_html=True)
                current = get_status(platform, i["id"])
                new_status = st.selectbox(
                    "Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current),
                    key=f"sel_{platform}_{i['id']}", label_visibility="collapsed",
                )
                if new_status != current:
                    set_status(platform, i["id"], new_status)
                    st.rerun()
            with ccols[3]:
                st.markdown("<span class='col-header'>Start date</span>", unsafe_allow_html=True)
                cur_start = get_item_date(platform, i["id"], "start")
                new_start = st.date_input(
                    "Start", value=cur_start, key=f"start_{platform}_{i['id']}",
                    label_visibility="collapsed",
                )
                if new_start != cur_start:
                    set_item_date(platform, i["id"], "start", new_start)
            with ccols[4]:
                st.markdown("<span class='col-header'>End date</span>", unsafe_allow_html=True)
                cur_end = get_item_date(platform, i["id"], "end")
                new_end = st.date_input(
                    "End", value=cur_end, key=f"end_{platform}_{i['id']}",
                    label_visibility="collapsed",
                )
                if new_end != cur_end:
                    set_item_date(platform, i["id"], "end", new_end)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

st.title("UIP · ALM · AQM — Training Track Dashboard")
st.caption("BMO / Connexservice · Aspect / Alvaria Unified IP 7.4 SP2 · Fabio — Technical Support")

tab_overview, tab_uip, tab_alm, tab_aqm, tab_phases = st.tabs(
    ["Overview", "UIP", "ALM", "AQM", "Logbook_staging"]
)

with tab_overview:
    overall = overall_progress()
    track = overall_track_progress()

    with st.container(border=True):
        gcol1, gcol2, gcol3 = st.columns([1, 1, 2])
        with gcol1:
            st.markdown("<span class='col-header'>General start</span>", unsafe_allow_html=True)
            g_start = st.date_input("General start", value=get_general_start(),
                                     key="general_start_input", label_visibility="collapsed")
            if g_start != get_general_start():
                set_general_start(g_start)
        with gcol2:
            st.markdown("<span class='col-header'>General end</span>", unsafe_allow_html=True)
            if all_items_done() and general_end_date():
                g_end = general_end_date()
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
                "General end auto-fills with the latest item end date once every "
                "item across UIP / ALM / AQM is marked Done."
            )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_tile("Overall (platform weight)", f"{overall}%", BMO_BLUE_DARK), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_tile("Overall (phase weight)", f"{track}%", BMO_RED_DEEP), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_tile("UIP", f"{platform_progress('UIP')}%", BMO_BLUE), unsafe_allow_html=True)
    with k4:
        st.markdown(
            kpi_tile("ALM / AQM", f"{platform_progress('ALM')}% / {platform_progress('AQM')}%", BMO_GRAY_DEEP),
            unsafe_allow_html=True,
        )

    pcol, phcol = st.columns(2)
    with pcol, st.container(border=True):
        st.markdown("<div class='progress-card-marker'></div>", unsafe_allow_html=True)
        st.markdown("<div class='progress-title'>Progress by platform</div>", unsafe_allow_html=True)
        gcols = st.columns(3)
        for gc, (platform, w) in zip(gcols, PLATFORM_WEIGHTS.items()):
            p = platform_progress(platform)
            with gc:
                st.plotly_chart(
                    make_gauge(p, platform, bar_color="#FFFFFF", bg_color=BMO_BLUE_DARK),
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"gauge_platform_{platform}",
                )
    with phcol, st.container(border=True):
        st.markdown("<div class='progress-card-marker'></div>", unsafe_allow_html=True)
        st.markdown("<div class='progress-title'>Progress by phase</div>", unsafe_allow_html=True)
        gcols = st.columns(3)
        for gc, phase in zip(gcols, PHASES):
            p = phase_progress(phase)
            short_name = phase["name"].split("—")[-1].strip()
            with gc:
                st.plotly_chart(
                    make_gauge(p, short_name, bar_color="#FFFFFF", bg_color=BMO_RED_DEEP),
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"gauge_phase_{phase['name']}",
                )

    st.markdown(
        f"""
        <div style='background-color:{BMO_BLUE_DARK};padding:1.2rem 1.5rem;
                    border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,0.15);margin-bottom:1.3rem;'>
            <div style='color:#FFFFFF;font-size:1.05rem;font-weight:700;margin-bottom:0.7rem;'>Topology</div>
            <div style='color:#EAF4FB;font-family:Consolas,monospace;font-size:0.88rem;line-height:1.8;'>
                UIP (Core) → AOD Interface → ALM (Dialing/Lists)<br>
                UIP (Core) → Switch/Agent Position → AQM (Recording/Quality)
            </div>
            <div style='color:#EAF4FB;font-size:0.82rem;margin-top:0.8rem;opacity:0.85;'>
                UIP is the foundation for the other two systems — starting point of the track.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab_uip:
    render_platform_tab("UIP")

with tab_alm:
    render_platform_tab("ALM")

with tab_aqm:
    render_platform_tab("AQM")

with tab_phases:
    with st.container(border=True):
        top = st.columns([3, 1])
        with top[0]:
            st.markdown("<div class='progress-title'>Logbook</div>", unsafe_allow_html=True)
        with top[1]:
            last_updated = get_logbook_updated()
            if last_updated:
                st.caption(f"Last edited: {last_updated}")

        current_text = get_logbook_text()
        new_text = st.text_area(
            "Logbook",
            value=current_text,
            height=560,
            key="logbook_textarea",
            label_visibility="collapsed",
            placeholder="Write freely here — daily notes, case details, anything worth remembering...",
        )
        if new_text != current_text:
            set_logbook_text(new_text)
            st.rerun()

st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
st.caption(f"Last saved: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Progress stored in {PROGRESS_FILE}")