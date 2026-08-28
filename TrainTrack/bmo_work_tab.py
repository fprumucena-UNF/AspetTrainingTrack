"""
Fabio Prumucena — BMO / Connext Work Portfolio (drop-in section)
==================================================================
Same dashboard data as before, redesigned 2026-08-28 for a more modern,
"executive/marketing" look — Fabio felt the original was hard to read and
too plain. This version does two things differently on purpose:

  1. LESS ON SCREEN AT ONCE. The old Overview sub-tab showed 3 charts side
     by side (timeline + bar + donut). This one leads with one hero chart
     (the timeline) plus 4 big KPI cards, then a single "workstream pulse"
     panel replaces the old bar+donut pair — same information, one visual
     instead of two.
  2. BOLDER VISUAL LANGUAGE. Custom gradient KPI cards, a vivid saturated
     palette (from data.py), bigger numbers, and a "headline insight" line
     that calls out the busiest workstream — the kind of one-glance framing
     an exec deck uses instead of a dashboard.

Same public function, same integration path as before — nothing in
trainingtrak.py needs to change:

    from bmo_work_tab import render_bmo_work_tab
    render_bmo_work_tab()

HOW TO INTEGRATE INTO YOUR EXISTING app.py (unchanged from before)
-------------------------------------------------------------------
1. Copy `bmo_work_tab.py` and `data.py` into the same folder as your app.py.
2. In your app.py:  from bmo_work_tab import render_bmo_work_tab
3. Call it wherever you want it to show up — as one more st.tabs() tab, as
   its own page in a `pages/` folder, or as a plain section.

Notes:
- This file does NOT call st.set_page_config() — your existing app already
  owns that.
- All widget keys are prefixed `bmo_` and all CSS classes are prefixed
  `.bmo-` to avoid colliding with anything else in your app.
"""

from datetime import datetime, timedelta

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import (
    JOIN_DATE, STATUS_COLORS, TODAY, TYPE_EMOJI, WORK_ITEMS, WORKSTREAM_ICONS,
    WORKSTREAMS,
)

MUTED = "#9E9E9E"

# ---------------------------------------------------------------------------
# Vibrant/marketing palette for this tab only. Deliberately its own thing —
# separate from the BMO navy/blue corporate palette the rest of the app
# uses — since this tab is the one Fabio asked to feel bolder and more
# "executive/marketing" than the training tabs.
# ---------------------------------------------------------------------------
INK = "#161221"
HERO_GRADIENT = "linear-gradient(135deg, #1C1533 0%, #3A1C71 55%, #7A2FBF 100%)"
CARD_BG = "#FFFFFF"
PAGE_TINT = "#FAF9FE"
GRID_TINT = "#ECE8F7"
ICE_WHITE = "#EAF2FF"  # soft ice-white for text on the KPI cards' dark gradients — less stark than pure #FFF

# Deepened 2026-08-28 — the first version used bright mid-tone gradients
# (e.g. orange→pink, teal→green) that looked bold but left white text at
# poor contrast on the lighter end of each gradient (Fabio flagged this as
# "hard to read"). These are darker/deeper jewel tones instead — still
# saturated and vivid, but every stop keeps white text clearly readable.
KPI_GRADIENTS = [
    "linear-gradient(135deg, #4C1D95 0%, #6D28D9 100%)",   # Total items — deep violet
    "linear-gradient(135deg, #9A3412 0%, #BE123C 100%)",   # Active now — deep orange/rose (urgency)
    "linear-gradient(135deg, #065F46 0%, #0F766E 100%)",   # Resolved % — deep emerald/teal
    "linear-gradient(135deg, #1E3A8A 0%, #4338CA 100%)",   # Workstreams touched — deep blue/indigo
]


def _darken(hex_color, factor=0.6):
    """Darken a hex color for use as text on a pale tint of that same color.
    Needed because some WORKSTREAMS colors (the yellow, the teal) are bright
    enough that white text on a solid fill — or the color itself on a pale
    tint of itself — is hard to read. Darkening keeps the same hue (so it
    still reads as "that workstream's color") while guaranteeing contrast,
    regardless of how light the original color is."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, int(c * factor)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _kpi_card(icon, value, label, gradient):
    return f"""
        <div class="bmo-kpi-card" style="background:{gradient};">
            <div class="bmo-kpi-icon">{icon}</div>
            <div class="bmo-kpi-value">{value}</div>
            <div class="bmo-kpi-label">{label}</div>
        </div>
    """


def render_bmo_work_tab() -> None:
    """Render the full work-portfolio section (hero + 3 sub-tabs) in place."""

    st.markdown(
        f"""
        <style>
            .bmo-hero {{
                background: {HERO_GRADIENT};
                border-radius: 20px;
                padding: 28px 32px 24px 32px;
                margin-bottom: 18px;
                box-shadow: 0 12px 30px rgba(58,28,113,0.25);
            }}
            .bmo-hero-title {{
                font-size: 2rem !important;
                font-weight: 800 !important;
                color: #FFFFFF !important;
                margin: 0 !important;
                letter-spacing: -0.01em;
            }}
            .bmo-hero-sub {{
                font-size: 0.98rem !important;
                color: rgba(255,255,255,0.78) !important;
                margin-top: 6px !important;
            }}
            .bmo-kpi-card {{
                border-radius: 16px;
                padding: 16px 18px 14px 18px;
                color: {ICE_WHITE} !important;
                min-height: 108px;
                box-shadow: 0 8px 20px rgba(20,10,40,0.18);
            }}
            /* !important on each child too, not just the card: the host app
               (trainingtrak.py) sets a blanket dark-text rule on every div,
               span, p and label for its own dark-on-light design. A rule
               that matches an element directly always beats one inherited
               from a parent, no matter which is more specific or which was
               declared later -- so without !important here, every one of
               these divs/spans came out dark instead of inheriting the
               card's ice-white. */
            .bmo-kpi-icon {{
                font-size: 1.5rem; line-height: 1; text-shadow: 0 1px 3px rgba(0,0,0,0.25);
                color: {ICE_WHITE} !important;
            }}
            .bmo-kpi-value {{
                font-size: 2.15rem; font-weight: 800; line-height: 1.15;
                margin-top: 8px; letter-spacing: -0.01em;
                text-shadow: 0 1px 3px rgba(0,0,0,0.25);
                color: {ICE_WHITE} !important;
            }}
            .bmo-kpi-label {{
                font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
                letter-spacing: 0.06em; opacity: 0.95; margin-top: 3px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.2);
                color: {ICE_WHITE} !important;
            }}
            .bmo-insight {{
                background: #FFF3EC;
                border: 1px solid #FFD9C2;
                border-left: 5px solid #FF6A3D;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 0.92rem;
                color: {INK};
                margin: 4px 0 22px 0;
            }}
            .bmo-insight b {{ color: #C2410C; }}
            .bmo-section-title {{
                font-size: 1.25rem !important;
                font-weight: 800 !important;
                color: {INK} !important;
                margin: 6px 0 2px 0 !important;
            }}
            .bmo-section-sub {{
                font-size: 0.85rem !important;
                color: #6B6478 !important;
                margin-bottom: 10px !important;
            }}
            .bmo-ws-row {{
                display: flex; align-items: center; gap: 14px;
                background: {CARD_BG}; border-radius: 12px;
                padding: 10px 16px; margin-bottom: 8px;
                box-shadow: 0 2px 10px rgba(30,20,60,0.06);
            }}
            .bmo-ws-icon {{ font-size: 1.25rem; width: 26px; text-align:center; }}
            .bmo-ws-name {{ font-weight: 700; color: {INK}; min-width: 240px; font-size: 0.92rem; }}
            .bmo-ws-track {{ flex: 1; height: 10px; background: {GRID_TINT}; border-radius: 6px; overflow: hidden; }}
            .bmo-ws-fill {{ height: 100%; border-radius: 6px; }}
            .bmo-ws-count {{ font-weight: 800; color: {INK}; min-width: 34px; text-align: right; font-size: 0.95rem; }}
            .bmo-ws-pct {{ font-weight: 600; color: #8A8395; min-width: 44px; text-align: right; font-size: 0.8rem; }}
            .bmo-ring-caption {{ text-align:center; font-weight:700; color:{INK}; font-size:0.95rem; margin-top:-8px; }}
            .bmo-tl-wrap {{
                max-height: 460px; overflow-y: auto;
                padding: 6px 10px 6px 0; margin-top: 6px;
            }}
            .bmo-tl-track {{ position: relative; padding-left: 26px; }}
            .bmo-tl-track::before {{
                content: ""; position: absolute; left: 8px; top: 4px; bottom: 4px;
                width: 2px; background: linear-gradient(180deg, #D9D0F0, #F3F0FB);
            }}
            .bmo-tl-node {{ position: relative; margin-bottom: 10px; }}
            .bmo-tl-dot {{
                position: absolute; left: -26px; top: 14px; width: 12px; height: 12px;
                border-radius: 50%; background: #FFFFFF; border: 2px solid currentColor;
                box-shadow: 0 0 0 3px #FFFFFF;
            }}
            .bmo-tl-card {{
                background: {CARD_BG}; border-radius: 12px; padding: 10px 16px;
                box-shadow: 0 2px 8px rgba(30,20,60,0.07);
            }}
            .bmo-tl-date {{
                font-size: 0.68rem; font-weight: 800; letter-spacing: 0.05em;
                text-transform: uppercase; color: #8A8395;
            }}
            .bmo-tl-title {{ font-weight: 700; color: {INK}; font-size: 0.94rem; margin: 3px 0 7px 0; }}
            .bmo-tl-tags {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
            .bmo-tl-tag {{
                font-size: 0.7rem; font-weight: 700; padding: 3px 11px; border-radius: 999px;
            }}
            .bmo-tl-tag-muted {{
                font-size: 0.7rem; font-weight: 700; padding: 3px 11px; border-radius: 999px;
                background: {GRID_TINT}; color: #6B6478;
            }}
            .bmo-tl-status {{ font-size: 0.78rem; font-weight: 600; color: {INK}; }}
            .bmo-tl-divider {{
                font-size: 0.72rem; font-weight: 700; color: #8A8395;
                text-transform: uppercase; letter-spacing: 0.05em;
                margin: 4px 0 10px 0;
            }}
            .bmo-legend-chip {{
                display:inline-flex; align-items:center; gap:6px;
                font-size:0.8rem; font-weight:600; color:{INK};
                background:{CARD_BG}; border-radius:999px; padding:5px 12px;
                margin:3px 6px 3px 0; box-shadow: 0 1px 6px rgba(30,20,60,0.08);
            }}
            .bmo-legend-dot {{ width:9px; height:9px; border-radius:50%; display:inline-block; }}
            .bmo-unverified {{ color:#C2410C; font-weight:700; font-size:0.78rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- data prep ----
    df = pd.DataFrame(WORK_ITEMS)
    df["start_dt"] = pd.to_datetime(df["start"])
    df["end_dt"] = df["end"].replace("", pd.NaT)
    df["end_dt"] = pd.to_datetime(df["end_dt"])
    df["end_dt"] = df["end_dt"].fillna(df["start_dt"])
    df["finish_dt"] = df[["start_dt", "end_dt"]].apply(
        lambda r: max(r["end_dt"], r["start_dt"] + timedelta(days=1)), axis=1
    )
    df["people_str"] = df["people"].apply(lambda p: ", ".join(p) if p else "—")
    df["status_dot"] = df["status"].map(
        {"Resolved": "🟢", "In Progress": "🟡", "Active": "🟡", "Unknown": "⚪"}
    )
    df["verified"] = df["confirmed"].map({True: "✅", False: "⚠️ unverified"})
    df["type_icon"] = df["type"].map(TYPE_EMOJI).fillna("")

    # ---- sidebar filters (namespaced so they don't clash with your app's own) ----
    st.sidebar.markdown("### 📊 My BMO Work")
    all_workstreams = list(WORKSTREAMS.keys())
    sel_workstreams = st.sidebar.multiselect(
        "Workstream", all_workstreams, default=all_workstreams, key="bmo_ws_filter"
    )
    all_types = sorted(df["type"].unique().tolist())
    sel_types = st.sidebar.multiselect(
        "Item type", all_types, default=all_types, key="bmo_type_filter"
    )
    min_d, max_d = df["start_dt"].min().date(), df["start_dt"].max().date()
    date_range = st.sidebar.slider(
        "Date range", min_value=min_d, max_value=max_d, value=(min_d, max_d),
        key="bmo_date_filter",
    )
    confirmed_only = st.sidebar.checkbox(
        "Confirmed items only", value=False, key="bmo_confirmed_filter"
    )
    st.sidebar.caption(
        f"Source: Outlook + Teams scan since {JOIN_DATE}. ⚠️ = not fully confirmed."
    )

    mask = (
        df["workstream"].isin(sel_workstreams)
        & df["type"].isin(sel_types)
        & (df["start_dt"].dt.date >= date_range[0])
        & (df["start_dt"].dt.date <= date_range[1])
    )
    if confirmed_only:
        mask &= df["confirmed"]
    fdf = df[mask].copy()

    # ---- hero header ----
    days_active = (
        datetime.strptime(TODAY, "%Y-%m-%d") - datetime.strptime(JOIN_DATE, "%Y-%m-%d")
    ).days
    st.markdown(
        f"""
        <div class="bmo-hero">
            <div class="bmo-hero-title">📊 Fabio Prumucena — Work Portfolio</div>
            <div class="bmo-hero-sub">
                BMO · CCS / Alvaria–Aspect Contact Center Infrastructure · allocated via Connext
                · active since {JOIN_DATE} ({days_active} days)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if fdf.empty:
        st.info("No items match the current filters.")
        return

    # ---- KPI hero row ----
    # Redesigned 2026-08-28 (executive pass, Fabio's request): the previous
    # 4 KPIs were "Total items" and "Workstreams touched" — activity-volume
    # numbers that read fine to Fabio but tell a director skimming this for
    # 30 seconds nothing about what needs THEIR attention. Two changes:
    #   1. Recurring meetings no longer count toward any KPI below — they're
    #      cadence, not delivered work, and were inflating the numbers.
    #   2. Two of the four cards are now genuinely decision-relevant: how
    #      many things have been sitting open too long, and how many are
    #      stuck waiting on the vendor (Alvaria) rather than on Fabio.
    today_ts = pd.Timestamp(TODAY)
    work_df = fdf[fdf["type"] != "Meeting"].copy()
    work_df["days_open"] = work_df.apply(
        lambda r: (r["end_dt"] - r["start_dt"]).days
        if r["status"] == "Resolved"
        else (today_ts - r["start_dt"]).days,
        axis=1,
    )
    ATTENTION_THRESHOLD_DAYS = 7
    total_work_items = len(work_df)
    needs_attention_df = work_df[(work_df["status"] != "Resolved") & (work_df["days_open"] > ATTENTION_THRESHOLD_DAYS)]
    waiting_alvaria_df = work_df[(work_df["status"] != "Resolved") & (work_df["people"].apply(lambda p: "Alvaria" in p))]
    needs_attention = len(needs_attention_df)
    waiting_alvaria = len(waiting_alvaria_df)
    active_now = int(work_df["status"].isin(["Active", "In Progress"]).sum())
    resolved_pct = round(100 * (work_df["status"] == "Resolved").sum() / total_work_items) if total_work_items else 0

    k1, k2, k3, k4 = st.columns(4)
    for col, html in zip(
        [k1, k2, k3, k4],
        [
            _kpi_card("🔥", needs_attention, f"Needs attention (>{ATTENTION_THRESHOLD_DAYS}d open)", KPI_GRADIENTS[1]),
            _kpi_card("🤝", waiting_alvaria, "Waiting on Alvaria", KPI_GRADIENTS[0]),
            _kpi_card("⏳", active_now, "Active right now", KPI_GRADIENTS[3]),
            _kpi_card("✅", f"{resolved_pct}%", "Resolved", KPI_GRADIENTS[2]),
        ],
    ):
        with col:
            st.markdown(html, unsafe_allow_html=True)

    # ---- headline insight ----
    # Replaced "busiest workstream" (interesting to Fabio, not actionable
    # for a director) with the same attention signal as the KPI row above,
    # spelled out as a sentence — the one line a director actually needs.
    if needs_attention > 0:
        names = ", ".join(needs_attention_df.sort_values("days_open", ascending=False)["title"].head(3))
        extra = f" Longest-open: {names}." if names else ""
        # "of those" only counts correctly when it's a true subset of the
        # needs-attention group — a case could be waiting on Alvaria but
        # still under the 7-day threshold, so the two counts aren't nested.
        overlap = len(needs_attention_df[needs_attention_df["people"].apply(lambda p: "Alvaria" in p)])
        if overlap:
            alvaria_note = f" {overlap} of those are waiting on Alvaria."
        elif waiting_alvaria:
            alvaria_note = f" Separately, {waiting_alvaria} active item(s) are waiting on Alvaria."
        else:
            alvaria_note = ""
        st.markdown(
            f"""<div class="bmo-insight">
                ⚠️&nbsp; <b>{needs_attention} item(s)</b> have been open more than
                {ATTENTION_THRESHOLD_DAYS} days.{alvaria_note}{extra}
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div class="bmo-insight" style="border-left-color:#0F766E; background:#ECFDF5; border-color:#A7F3D0;">
                ✅&nbsp; Nothing open more than a week right now — no items need escalation.
            </div>""",
            unsafe_allow_html=True,
        )

    # Reordered 2026-08-28 (executive pass): Detail Log first. It's the one
    # plain, scannable table in this whole tab — the thing a director opens
    # this page to actually use — so it shouldn't be buried behind a
    # narrative timeline and a network graph. Overview (the story, useful in
    # a 1:1 with Fabio) comes second; Connections (interesting, not
    # decision-relevant) moves last.
    tab_detail, tab_overview, tab_connections = st.tabs(
        ["📋 Detail Log", "🚀 Overview", "🕸️ Connections"]
    )

    # ================= TAB 1 — Overview =================
    with tab_overview:
        st.markdown('<div class="bmo-section-title">How the work unfolded</div>', unsafe_allow_html=True)
        st.markdown('<div class="bmo-section-sub">Tasks first, oldest to newest — recurring meetings are grouped at the end.</div>', unsafe_allow_html=True)

        # A vertical "milestone" timeline instead of a Gantt chart. Gantt bars
        # look great when items run for a while, but most items here are
        # single-day cases/incidents — as bars they render as barely-visible
        # slivers of very uneven width, which is exactly the "hard to read"
        # complaint. A chronological card list reads cleanly regardless of
        # how long an item took, and doubles as a compact activity feed.
        #
        # Sort order (2026-08-28): actual work (Case/Incident/Initiative/
        # Event) always comes before recurring Meetings, regardless of date.
        # Fabio's recurring CCS meetings all start on day one, so a pure
        # chronological sort buried the real case/incident work under a wall
        # of meetings at the very top — the opposite of what matters most.
        # Meetings still show up (grouped, muted, at the bottom), just not
        # first.
        story_df = fdf.copy()
        story_df["is_meeting"] = story_df["type"] == "Meeting"
        story_df = story_df.sort_values(["is_meeting", "start_dt"])

        rows_html = []
        meetings_intro_added = False
        for _, row in story_df.iterrows():
            is_meeting = row["is_meeting"]
            if is_meeting and not meetings_intro_added:
                rows_html.append(
                    '<div class="bmo-tl-divider">🔁 Recurring meetings (ongoing cadence, not one-off work)</div>'
                )
                meetings_intro_added = True

            color = WORKSTREAMS.get(row["workstream"], MUTED)
            date_label = row["start_dt"].strftime("%b %d")
            if pd.notna(row["end_dt"]) and row["end_dt"] > row["start_dt"]:
                date_label += f" – {row['end_dt'].strftime('%b %d')}"
            status_icon = {"Resolved": "🟢", "In Progress": "🟡", "Active": "🟡", "Unknown": "⚪"}.get(row["status"], "⚪")
            unverified = "" if row["confirmed"] else " <span class='bmo-unverified'>⚠️ unverified</span>"
            # Built as one continuous line with no line breaks or leading
            # whitespace on purpose: Streamlit's markdown renderer follows
            # CommonMark's HTML-block rule, where a blank/whitespace-only
            # line ends a raw-HTML block. An indented multi-line template
            # here previously left whitespace-only gaps between cards,
            # which broke the block after the first card and made every
            # card after it show up as literal text instead of rendering.
            if is_meeting:
                # Muted on purpose — same reasoning as the sort order above:
                # recurring meetings are real but secondary, so they read as
                # background context rather than competing with real work
                # for attention.
                dot_color = MUTED
                tag_html = '<span class="bmo-tl-tag-muted">🔁 Recurring meeting</span>'
            else:
                dot_color = color
                # Text uses a darkened version of the workstream color, not
                # the color itself, on a pale tint of the original — plain
                # white-on-color failed badly for the brighter hues (the
                # yellow and teal workstreams were nearly unreadable).
                text_color = _darken(color)
                tag_label = f"{WORKSTREAM_ICONS.get(row['workstream'], '')} {row['workstream']}"
                tag_html = f'<span class="bmo-tl-tag" style="background:{color}20; color:{text_color};">{tag_label}</span>'
            rows_html.append(
                '<div class="bmo-tl-node">'
                f'<div class="bmo-tl-dot" style="color:{dot_color};"></div>'
                '<div class="bmo-tl-card">'
                f'<div class="bmo-tl-date">{date_label}</div>'
                f'<div class="bmo-tl-title">{row["type_icon"]} {row["title"]}</div>'
                '<div class="bmo-tl-tags">'
                f'{tag_html}'
                f'<span class="bmo-tl-status">{status_icon} {row["status"]}</span>{unverified}'
                '</div></div></div>'
            )
        st.markdown(
            '<div class="bmo-tl-wrap"><div class="bmo-tl-track">' + "".join(rows_html) + "</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        left, right = st.columns([3, 2])
        with left:
            st.markdown('<div class="bmo-section-title">Where the work concentrated</div>', unsafe_allow_html=True)
            st.markdown('<div class="bmo-section-sub">Share of actual work items by workstream — meetings excluded, biggest first.</div>', unsafe_allow_html=True)
            counts = work_df.groupby("workstream").size().sort_values(ascending=False)
            max_count = int(counts.max()) if not counts.empty else 1
            for ws, n in counts.items():
                pct = round(100 * n / total_work_items) if total_work_items else 0
                width_pct = round(100 * n / max_count)
                color = WORKSTREAMS.get(ws, MUTED)
                icon = WORKSTREAM_ICONS.get(ws, "🔎")
                st.markdown(
                    f"""
                    <div class="bmo-ws-row">
                        <div class="bmo-ws-icon">{icon}</div>
                        <div class="bmo-ws-name">{ws}</div>
                        <div class="bmo-ws-track">
                            <div class="bmo-ws-fill" style="width:{width_pct}%; background:{color};"></div>
                        </div>
                        <div class="bmo-ws-count">{n}</div>
                        <div class="bmo-ws-pct">{pct}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with right:
            st.markdown('<div class="bmo-section-title">Status mix</div>', unsafe_allow_html=True)
            st.markdown('<div class="bmo-section-sub">Overall completion at a glance.</div>', unsafe_allow_html=True)
            fig_ring = go.Figure(go.Pie(
                values=[resolved_pct, 100 - resolved_pct],
                hole=0.74,
                sort=False,
                direction="clockwise",
                marker=dict(colors=[STATUS_COLORS["Resolved"], GRID_TINT], line=dict(width=0)),
                textinfo="none",
                hoverinfo="skip",
            ))
            fig_ring.update_layout(
                height=210, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                font={"family": "Segoe UI, sans-serif"},
                annotations=[dict(
                    text=f"<b style='font-size:30px;color:{INK}'>{resolved_pct}%</b>"
                         f"<br><span style='font-size:12px;color:#8A8395'>Resolved</span>",
                    x=0.5, y=0.5, showarrow=False,
                )],
            )
            st.plotly_chart(fig_ring, width="stretch", config={"displayModeBar": False}, key="bmo_chart_ring")

            status_counts = work_df["status"].value_counts()
            chips = "".join(
                f"""<span class="bmo-legend-chip">
                        <span class="bmo-legend-dot" style="background:{STATUS_COLORS.get(s, MUTED)};"></span>
                        {s} · {c}
                    </span>"""
                for s, c in status_counts.items()
            )
            st.markdown(f"<div style='margin-top:10px;'>{chips}</div>", unsafe_allow_html=True)

        st.caption(
            "🟢 Resolved · 🟡 Active / In Progress · ⚪ Unknown (edit `data.py` to correct)."
        )

    # ================= TAB 2 — Connections =================
    with tab_connections:
        st.markdown('<div class="bmo-section-title">How it all connects</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="bmo-section-sub">Fabio → workstream → individual case/incident/initiative → the people involved. '
            'Hover any node for detail; drag to rearrange.</div>',
            unsafe_allow_html=True,
        )

        G = nx.Graph()
        G.add_node("Fabio", kind="center")
        for ws in sorted(fdf["workstream"].unique()):
            G.add_node(ws, kind="workstream")
            G.add_edge("Fabio", ws)
        for _, row in fdf.iterrows():
            item_label = f"{row['ref'] or row['id']}"
            G.add_node(
                item_label, kind="item", workstream=row["workstream"],
                title=row["title"], status=row["status"], itype=row["type"],
            )
            G.add_edge(row["workstream"], item_label)
            for person in row["people"]:
                if not person:
                    continue
                G.add_node(person, kind="person")
                G.add_edge(item_label, person)

        pos = nx.spring_layout(G, seed=7, k=0.6)
        edge_x, edge_y = [], []
        for a, b in G.edges():
            edge_x += [pos[a][0], pos[b][0], None]
            edge_y += [pos[a][1], pos[b][1], None]
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(width=1.2, color="#D9D0F0"), hoverinfo="none",
            showlegend=False,
        )

        node_traces = []
        kind_style = {
            "center": dict(size=36, color="#FF3D6E", symbol="star"),
            "workstream": dict(size=28, color=None, symbol="square"),
            "item": dict(size=15, color=None, symbol="circle"),
            "person": dict(size=13, color="#3A1C71", symbol="diamond"),
        }
        for kind in ["item", "person", "workstream", "center"]:
            nodes = [n for n, d in G.nodes(data=True) if d.get("kind") == kind]
            if not nodes:
                continue
            xs = [pos[n][0] for n in nodes]
            ys = [pos[n][1] for n in nodes]
            style = kind_style[kind]
            if kind == "workstream":
                colors = [WORKSTREAMS.get(n, MUTED) for n in nodes]
            elif kind == "item":
                colors = [WORKSTREAMS.get(G.nodes[n].get("workstream"), MUTED) for n in nodes]
            else:
                colors = style["color"]

            hover = []
            for n in nodes:
                d = G.nodes[n]
                if kind == "item":
                    hover.append(
                        f"<b>{d.get('title')}</b><br>{d.get('itype')} · {n}<br>Status: {d.get('status')}"
                    )
                elif kind == "workstream":
                    hover.append(f"<b>{n}</b><br>Workstream")
                elif kind == "person":
                    hover.append(f"<b>{n}</b>")
                else:
                    hover.append("Fabio Prumucena")

            node_traces.append(
                go.Scatter(
                    x=xs, y=ys,
                    mode="markers" + ("+text" if kind in ("center", "workstream") else ""),
                    text=nodes if kind in ("center", "workstream") else None,
                    textposition="top center",
                    textfont=dict(color=INK, size=11),
                    hovertext=hover, hoverinfo="text",
                    marker=dict(
                        size=style["size"], color=colors, symbol=style["symbol"],
                        line=dict(width=1.5, color="white"),
                    ),
                    name=kind, showlegend=False,
                )
            )

        fig_net = go.Figure(data=[edge_trace] + node_traces)
        fig_net.update_layout(
            plot_bgcolor=PAGE_TINT, paper_bgcolor=PAGE_TINT,
            margin=dict(l=10, r=10, t=10, b=10), height=540,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            font=dict(color=INK, family="Segoe UI, sans-serif"),
            showlegend=False,
        )
        st.plotly_chart(fig_net, width="stretch", key="bmo_chart_network")

        st.markdown('<div class="bmo-section-title" style="margin-top:1.2rem;">Top collaborators</div>', unsafe_allow_html=True)
        people_flat = [p for plist in fdf["people"] for p in plist if p]
        if people_flat:
            people_counts = pd.Series(people_flat).value_counts().sort_values()
            fig_people = go.Figure(
                go.Bar(
                    x=people_counts.values, y=people_counts.index, orientation="h",
                    marker_color="#7C3AED", marker_line_width=0,
                )
            )
            fig_people.update_layout(
                plot_bgcolor=PAGE_TINT, paper_bgcolor=PAGE_TINT,
                margin=dict(l=10, r=10, t=10, b=10), height=260,
                xaxis=dict(title="Items together", gridcolor=GRID_TINT),
                font=dict(color=INK, family="Segoe UI, sans-serif"),
            )
            st.plotly_chart(fig_people, width="stretch", key="bmo_chart_people")
        else:
            st.info("No named collaborators in the current filter.")

    # ================= TAB — Detail Log =================
    with tab_detail:
        st.markdown('<div class="bmo-section-title">Full detail log</div>', unsafe_allow_html=True)
        search = st.text_input(
            "Search (title, ref, people, evidence)", "", key="bmo_search"
        )
        show_df = fdf.copy()
        if search:
            s = search.lower()
            show_df = show_df[
                show_df.apply(
                    lambda r: s in str(r["title"]).lower()
                    or s in str(r["ref"]).lower()
                    or s in str(r["people_str"]).lower()
                    or s in str(r["evidence"]).lower(),
                    axis=1,
                )
            ]
        show_df = show_df.sort_values("start_dt", ascending=False)
        show_df["type_display"] = show_df["type_icon"] + " " + show_df["type"]
        # "Days Open" — the same aging signal behind the KPI row above, but
        # per row so a director can see exactly which items are the old
        # ones, not just the count. Meetings are ongoing by nature, so they
        # show a dash instead of a (meaningless) day count.
        show_df["days_open_display"] = show_df.apply(
            lambda r: "—" if r["type"] == "Meeting"
            else f"{(r['end_dt'] - r['start_dt']).days}d" if r["status"] == "Resolved"
            else f"{(today_ts - r['start_dt']).days}d",
            axis=1,
        )
        display_cols = {
            "start": "Date", "type_display": "Type", "ref": "Ref", "title": "Title",
            "workstream": "Workstream", "status_dot": "Status", "days_open_display": "Days Open", "role": "Role",
            "people_str": "People", "verified": "Verified", "evidence": "Evidence",
        }
        st.dataframe(
            show_df[list(display_cols.keys())].rename(columns=display_cols),
            width="stretch", hide_index=True, height=560, key="bmo_detail_table",
        )
        csv = show_df[list(display_cols.keys())].rename(columns=display_cols).to_csv(index=False)
        st.download_button(
            "⬇ Download filtered log as CSV", data=csv,
            file_name="fabio_bmo_work_log.csv", mime="text/csv", key="bmo_download",
        )

    with st.expander("About this section"):
        st.markdown(
            f"""
- **Source data:** Outlook + Teams activity scan (Microsoft Copilot), {JOIN_DATE} through {TODAY}.
- **Confidence:** items flagged **⚠️ unverified** were referenced but not fully confirmed —
  check before quoting in a formal review.
- **Keeping it current:** all data lives in `data.py` — add an entry there for each new
  case/incident/initiative and it appears here automatically.
            """
        )
