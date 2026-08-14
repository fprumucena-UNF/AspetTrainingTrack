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
    /* Compact status slider (fillable "iniciado / em andamento / concluído" bar) */
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

PROGRESS_FILE = "progress.json"
GENERAL_START_DEFAULT = date(2026, 8, 1)

# ---------------------------------------------------------------------------
# Data model — training curriculum: 3 products × 4 tracks (trilhas)
#
# Each item: id (unique within the platform), track, a *compact* name,
# a short desc (shown smaller/lighter under the name), and hours.
# There is no manual "weight" to keep in sync anymore — progress is
# weighted by `hours` automatically, so nothing can drift out of 100%.
# ---------------------------------------------------------------------------

TRACKS = ["Usuário", "Supervisor", "Administrador", "Engenheiro de Suporte"]

PLATFORM_ITEMS = {
    "UIP": [
        # Usuário — 7h
        {"id": 1, "track": "Usuário", "name": "Interface do Agente",
         "desc": "Login, status, transferência e conferência de chamadas", "hours": 2},
        {"id": 2, "track": "Usuário", "name": "Atendimento Multicanal",
         "desc": "Voz, chat e callback num único fluxo de atendimento", "hours": 3},
        {"id": 3, "track": "Usuário", "name": "Unified Director",
         "desc": "Uso do softphone no dia a dia do agente", "hours": 2},
        # Supervisor — 8h
        {"id": 4, "track": "Supervisor", "name": "URM Dashboard",
         "desc": "Painel de tempo real — filas, agentes e SLAs", "hours": 3},
        {"id": 5, "track": "Supervisor", "name": "Gestão de Equipe",
         "desc": "Escalonamento, barge-in/whisper e relatórios operacionais", "hours": 3},
        {"id": 6, "track": "Supervisor", "name": "UCC-Admin Rápido",
         "desc": "Ajustes rápidos de rotas e filas", "hours": 2},
        # Administrador — 22h
        {"id": 7, "track": "Administrador", "name": "Arquitetura Geral",
         "desc": "Core Server, DCP/TMS, Broker, URM e fluxo de chamada", "hours": 3},
        {"id": 8, "track": "Administrador", "name": "Roteamento (ACD)",
         "desc": "Configuração de ACD e planos de discagem", "hours": 3},
        {"id": 9, "track": "Administrador", "name": "M3 Designer — Fundamentos",
         "desc": "Fundamentos de IVR com M3 Designer", "hours": 3},
        {"id": 10, "track": "Administrador", "name": "M3 Avançado",
         "desc": "Scripts multi-documento e integração com banco de dados", "hours": 3},
        {"id": 11, "track": "Administrador", "name": "Chat e Web Callback",
         "desc": "Configuração de canais de chat e callback web", "hours": 2},
        {"id": 12, "track": "Administrador", "name": "Enterprise Routing",
         "desc": "IPNIQ, Broker e roteamento entre sites", "hours": 3},
        {"id": 13, "track": "Administrador", "name": "UCC-Admin e URM",
         "desc": "Administração via UCC-Admin e Unified Resource Manager", "hours": 3},
        {"id": 14, "track": "Administrador", "name": "Segurança e Licenciamento",
         "desc": "Segurança, licenciamento e gestão de usuários", "hours": 2},
        # Engenheiro de Suporte — 17h
        {"id": 15, "track": "Engenheiro de Suporte", "name": "Infraestrutura e Rede",
         "desc": "Arquitetura de infraestrutura e rede do UIP", "hours": 3},
        {"id": 16, "track": "Engenheiro de Suporte", "name": "Instalação",
         "desc": "Instalação e uso do Server Configurator", "hours": 3},
        {"id": 17, "track": "Engenheiro de Suporte", "name": "Processo de Upgrade",
         "desc": "Pré-requisitos e troubleshooting de upgrade", "hours": 3},
        {"id": 18, "track": "Engenheiro de Suporte", "name": "Diagnóstico",
         "desc": "Logs, Performance Monitor e ferramentas de rede", "hours": 3},
        {"id": 19, "track": "Engenheiro de Suporte", "name": "HA e DR/Failover",
         "desc": "Alta disponibilidade e disaster recovery/failover", "hours": 2},
        {"id": 20, "track": "Engenheiro de Suporte", "name": "Integração Enterprise",
         "desc": "Visão integrada UIP + ALM + AQM + UCC-Admin", "hours": 3},
    ],
    "ALM": [
        # Usuário — 2h
        {"id": 1, "track": "Usuário", "name": "Operação Outbound",
         "desc": "Contatos e disposições em campanhas outbound", "hours": 2},
        # Supervisor — 4h
        {"id": 2, "track": "Supervisor", "name": "Monitoramento em Tempo Real",
         "desc": "CPS e filas de campanhas outbound", "hours": 2},
        {"id": 3, "track": "Supervisor", "name": "Gestão de Listas",
         "desc": "Listas de contatos e regras de disposição", "hours": 2},
        # Administrador — 8h
        {"id": 4, "track": "Administrador", "name": "Conceitos de Campanha",
         "desc": "Listas, discadores e Optimizer", "hours": 3},
        {"id": 5, "track": "Administrador", "name": "Configuração de Campanhas",
         "desc": "Regras de contato e compliance (DNC)", "hours": 3},
        {"id": 6, "track": "Administrador", "name": "Integração ALM ↔ UIP",
         "desc": "Integração com UIP e bancos de dados", "hours": 2},
        # Engenheiro de Suporte — 9h
        {"id": 7, "track": "Engenheiro de Suporte", "name": "Arquitetura de Serviços",
         "desc": "Filas QLE, QOP, QHD e Watchdog", "hours": 3},
        {"id": 8, "track": "Engenheiro de Suporte", "name": "Instalação e HA",
         "desc": "Instalação, DFS Replication e alta disponibilidade", "hours": 3},
        {"id": 9, "track": "Engenheiro de Suporte", "name": "Troubleshooting",
         "desc": "sqlcmd, contadores de performance e logs", "hours": 3},
    ],
    "AQM": [
        # Usuário — 2h
        {"id": 1, "track": "Usuário", "name": "Desktop Client",
         "desc": "Gravação sob demanda e autoavaliação", "hours": 2},
        # Supervisor/Mentor — 9h
        {"id": 2, "track": "Supervisor", "name": "Live Monitor",
         "desc": "Monitoramento e avaliações em tempo real", "hours": 2},
        {"id": 3, "track": "Supervisor", "name": "Scorecards",
         "desc": "Busca, reprodução e pontuação de gravações", "hours": 3},
        {"id": 4, "track": "Supervisor", "name": "Calibração entre Mentores",
         "desc": "Calibração e revisão por pares", "hours": 2},
        {"id": 5, "track": "Supervisor", "name": "Relatórios e Tendências",
         "desc": "Relatórios e análise de tendências", "hours": 2},
        # Administrador — 11h
        {"id": 6, "track": "Administrador", "name": "Fundamentos e Ciclo de Vida",
         "desc": "Planejar → gravar → revisar → reportar", "hours": 2},
        {"id": 7, "track": "Administrador", "name": "Usuários e Acessos",
         "desc": "Direitos e memberships — Agent/Skill Group, Team", "hours": 2},
        {"id": 8, "track": "Administrador", "name": "Regras de Gravação",
         "desc": "Regras de gravação e templates de scorecard", "hours": 3},
        {"id": 9, "track": "Administrador", "name": "CMQ",
         "desc": "Customer Measured Quality — pesquisas e convites", "hours": 2},
        {"id": 10, "track": "Administrador", "name": "Integração AQM ↔ UIP",
         "desc": "Sync de dados e estatísticas de gravação", "hours": 2},
        # Engenheiro de Suporte — 10h
        {"id": 11, "track": "Engenheiro de Suporte", "name": "Arquitetura e Config Utility",
         "desc": "Arquitetura e Desktop Client Configuration Utility", "hours": 3},
        {"id": 12, "track": "Engenheiro de Suporte", "name": "Instalação DTC",
         "desc": "Instalação do Desktop Client (DTC Install)", "hours": 2},
        {"id": 13, "track": "Engenheiro de Suporte", "name": "Troubleshooting",
         "desc": "Storage paths, transcodificação e performance", "hours": 3},
        {"id": 14, "track": "Engenheiro de Suporte", "name": "Manutenção e Patches",
         "desc": "Manutenção e aplicação de hotfixes", "hours": 2},
    ],
}

STATUS_OPTIONS = ["Not started", "In progress", "Done"]
STATUS_VALUE = {"Not started": 0, "In progress": 50, "Done": 100}
STATUS_EN_TO_PT = {"Not started": "Não iniciado", "In progress": "Em andamento", "Done": "Concluído"}
STATUS_PT_TO_EN = {v: k for k, v in STATUS_EN_TO_PT.items()}
STATUS_OPTIONS_PT = ["Não iniciado", "Em andamento", "Concluído"]


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
    st.session_state.progress["logbook_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_progress(st.session_state.progress)


def get_logbook_updated():
    return st.session_state.progress.get("logbook_updated")


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


def track_matrix():
    """{platform: {track: (module_count, hours)}} — used by the 'Trilhas por produto' table."""
    m = {}
    for platform, items in PLATFORM_ITEMS.items():
        m[platform] = {}
        for t in TRACKS:
            sub = [i for i in items if i["track"] == t]
            m[platform][t] = (len(sub), sum(i["hours"] for i in sub))
    return m


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
    prog = platform_progress(platform)
    p_hours = total_hours(platform)
    grand_total = total_hours()
    share = round(p_hours / grand_total * 100, 1) if grand_total else 0.0

    st.subheader(f"{platform} — {p_hours}h ({share}% do treinamento total)")
    st.progress(prog / 100, text=f"{prog}% concluído")

    grouped = items_by_track(platform)
    for track in TRACKS:
        t_items = grouped.get(track, [])
        if not t_items:
            continue
        t_hours = sum(i["hours"] for i in t_items)
        t_prog = weighted_progress(t_items, platform)

        st.markdown(f"<div class='progress-title' style='margin-top:1.1rem;'>{track}</div>", unsafe_allow_html=True)
        st.caption(f"{len(t_items)} módulos · {t_hours}h")
        st.progress(t_prog / 100, text=f"{t_prog}%")

        for i in t_items:
            with st.container(border=True):
                ccols = st.columns([3, 2])
                with ccols[0]:
                    st.markdown(f"<div class='item-name'>{i['name']}</div>", unsafe_allow_html=True)
                    st.caption(i["desc"])
                with ccols[1]:
                    st.markdown(
                        f"<div style='text-align:right;'><span class='item-weight'>{i['hours']}h</span></div>",
                        unsafe_allow_html=True,
                    )
                    current_en = get_status(platform, i["id"])
                    current_pt = STATUS_EN_TO_PT[current_en]
                    new_pt = st.select_slider(
                        "Status", options=STATUS_OPTIONS_PT, value=current_pt,
                        key=f"stat_{platform}_{i['id']}", label_visibility="collapsed",
                    )
                    if new_pt != current_pt:
                        set_status(platform, i["id"], STATUS_PT_TO_EN[new_pt])
                        st.rerun()


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

st.title("UIP · ALM · AQM — Training Track Dashboard")
st.caption("BMO / Connexservice · Aspect / Alvaria Unified IP 7.4 SP2 · Fabio — Technical Support")

tab_overview, tab_uip, tab_alm, tab_aqm, tab_logbook = st.tabs(
    ["Overview", "UIP", "ALM", "AQM", "Logbook_staging"]
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
                                     key="general_start_input", label_visibility="collapsed")
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

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_tile("Overall", f"{overall}%", BMO_BLUE_DARK), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_tile("UIP", f"{platform_progress('UIP')}%", BMO_BLUE), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_tile("ALM", f"{platform_progress('ALM')}%", BMO_GRAY_DEEP), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_tile("AQM", f"{platform_progress('AQM')}%", BMO_RED_DEEP), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='progress-card-marker'></div>", unsafe_allow_html=True)
        st.markdown("<div class='progress-title'>Progress by platform</div>", unsafe_allow_html=True)
        gcols = st.columns(3)
        for gc, platform in zip(gcols, PLATFORM_ITEMS.keys()):
            p = platform_progress(platform)
            with gc:
                st.plotly_chart(
                    make_gauge(p, platform, bar_color="#FFFFFF", bg_color=BMO_BLUE_DARK),
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"gauge_platform_{platform}",
                )

    st.markdown(
        f"""
        <div style='background-color:{BMO_BLUE_DARK};padding:1.2rem 1.5rem;
                    border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,0.15);margin-bottom:1.3rem;'>
            <div style='color:#FFFFFF;font-size:1.05rem;font-weight:700;margin-bottom:0.7rem;'>Topology</div>
            <div style='color:#EAF4FB;font-family:Consolas,monospace;font-size:0.85rem;line-height:1.75;white-space:pre;'>
      Outbound ──►  ┌─────────────┐  ◄── Gravação / Qualidade
        (ALM)       │     UIP     │        (AQM)
                     │ ACD·IVR·Rot.│
                     └─────────────┘
                            │
                Voz · Chat · Callback
                            │
                      Agente / Cliente
            </div>
            <div style='color:#EAF4FB;font-size:0.85rem;margin-top:0.9rem;line-height:1.55;opacity:0.92;'>
                UIP é a plataforma central (ACD, roteamento, IVR/M3, chat, callback). ALM injeta contatos
                outbound nas filas do UIP; AQM escuta as chamadas que passam pelo UIP para gravar e avaliar.
                Ordem recomendada: <b>UIP primeiro</b>, depois ALM/AQM em paralelo. Dentro de cada produto,
                a profundidade sobe: Usuário → Supervisor → Administrador → Engenheiro de Suporte.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("<div class='progress-title'>Trilhas por produto</div>", unsafe_allow_html=True)
        m = track_matrix()
        header_cells = "".join(
            f"<th style='padding:8px 10px;text-align:center;color:{BMO_GRAY};text-transform:uppercase;"
            f"font-size:0.72rem;letter-spacing:0.03em;'>{t}</th>"
            for t in TRACKS
        )
        rows_html = ""
        for platform in PLATFORM_ITEMS:
            cells = "".join(
                f"<td style='padding:8px 10px;text-align:center;'>{m[platform][t][1]}h "
                f"<span style='color:{BMO_GRAY};font-size:0.76rem;'>({m[platform][t][0]}m)</span></td>"
                for t in TRACKS
            )
            rows_html += (
                f"<tr><td style='padding:8px 10px;font-weight:700;color:{BMO_BLUE_DARK};'>{platform}</td>"
                f"{cells}</tr>"
            )
        st.markdown(
            f"""
            <table style='width:100%;border-collapse:collapse;'>
                <thead><tr><th></th>{header_cells}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            """,
            unsafe_allow_html=True,
        )

with tab_uip:
    render_platform_tab("UIP")

with tab_alm:
    render_platform_tab("ALM")

with tab_aqm:
    render_platform_tab("AQM")

with tab_logbook:
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