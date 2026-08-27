"""
Fabio Prumucena — BMO / Connext Work Portfolio (drop-in section)
==================================================================
Same dashboard as app.py, refactored into ONE function so it can be pasted
into an existing Streamlit app as a tab/section instead of running as its
own app.

HOW TO INTEGRATE INTO YOUR EXISTING app.py
-------------------------------------------
1. Copy `bmo_work_tab.py` and `data.py` into the same folder as your app.py.
2. In your app.py:

    from bmo_work_tab import render_bmo_work_tab

3. Call it wherever you want it to show up. Three common cases:

   A) You already have `st.tabs([...])` in your app — just add one more tab:

        tab_a, tab_b, tab_bmo = st.tabs(["Existing 1", "Existing 2", "📊 My BMO Work"])
        with tab_bmo:
            render_bmo_work_tab()

   B) Your app is multipage (a `pages/` folder) — create a new file
      `pages/BMO_Work.py` with just:

        from bmo_work_tab import render_bmo_work_tab
        render_bmo_work_tab()

      Streamlit auto-adds it to the sidebar page nav.

   C) You just want it as a section on your existing single page —
      call it directly, anywhere after your other content:

        render_bmo_work_tab()

Notes:
- This file does NOT call st.set_page_config() or st.sidebar.header("Filters")
  at the top level — your existing app already owns those. Filters render in
  the sidebar under a "📊 My BMO Work" label so they don't clash with yours.
- All widget keys are prefixed `bmo_` to avoid colliding with widget keys/
  labels you already use elsewhere in your app.
"""

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data import JOIN_DATE, STATUS_COLORS, TODAY, WORK_ITEMS, WORKSTREAMS

MUTED = "#898781"


def render_bmo_work_tab() -> None:
    """Render the full work-portfolio section (KPIs + 3 sub-tabs) in place."""

    st.markdown(
        """
        <style>
            div[data-testid="stMetric"] {
                background: #ffffff;
                border: 1px solid rgba(11,11,11,0.08);
                border-radius: 10px;
                padding: 14px 16px 8px 16px;
            }
            div[data-testid="stMetricValue"] {font-size: 1.6rem;}
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

    # ---- header ----
    days_active = (
        datetime.strptime(TODAY, "%Y-%m-%d") - datetime.strptime(JOIN_DATE, "%Y-%m-%d")
    ).days
    st.header("📊 Fabio Prumucena — Work Portfolio")
    st.caption(
        f"BMO · CCS / Alvaria–Aspect Contact Center Infrastructure · allocated via Connext · "
        f"active since {JOIN_DATE} ({days_active} days)"
    )

    # ---- KPI row ----
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total items", len(fdf))
    k2.metric("Support cases", int((fdf["type"] == "Case").sum()))
    k3.metric("Incidents", int((fdf["type"] == "Incident").sum()))
    k4.metric("Initiatives / events", int(fdf["type"].isin(["Initiative", "Event"]).sum()))
    k5.metric("Workstreams touched", fdf["workstream"].nunique())
    k6.metric("Recurring meetings", int((fdf["type"] == "Meeting").sum()))

    st.markdown("")
    tab_overview, tab_connections, tab_detail = st.tabs(
        ["📊 Overview", "🕸️ Connections", "📋 Detail Log"]
    )

    # ================= TAB 1 — Overview =================
    with tab_overview:
        st.subheader("Timeline — how the work unfolded")
        if fdf.empty:
            st.info("No items match the current filters.")
        else:
            timeline_df = fdf.sort_values("start_dt")
            fig_tl = px.timeline(
                timeline_df,
                x_start="start_dt",
                x_end="finish_dt",
                y="workstream",
                color="workstream",
                color_discrete_map=WORKSTREAMS,
                category_orders={"workstream": all_workstreams},
                hover_name="title",
                hover_data={
                    "ref": True, "type": True, "status": True, "role": True,
                    "people_str": True, "start_dt": False, "end_dt": False,
                    "finish_dt": False, "workstream": False,
                },
                labels={"people_str": "People", "ref": "Ref", "role": "Role"},
            )
            fig_tl.update_yaxes(autorange="reversed", title=None)
            fig_tl.update_xaxes(title=None, gridcolor="#e1e0d9")
            fig_tl.update_layout(
                plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
                legend_title_text="Workstream", height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(color="#0b0b0b"),
            )
            st.plotly_chart(fig_tl, width="stretch", key="bmo_chart_timeline")

        left, right = st.columns([3, 2])
        with left:
            st.subheader("Where the work concentrated")
            counts = (
                fdf.groupby("workstream").size().reindex(all_workstreams).dropna().sort_values()
            )
            if not counts.empty:
                fig_bar = go.Figure(
                    go.Bar(
                        x=counts.values, y=counts.index, orientation="h",
                        marker_color=[WORKSTREAMS[w] for w in counts.index],
                        text=counts.values, textposition="outside",
                    )
                )
                fig_bar.update_layout(
                    plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
                    margin=dict(l=10, r=10, t=10, b=10), height=320,
                    xaxis=dict(title="Items", gridcolor="#e1e0d9"),
                    font=dict(color="#0b0b0b"),
                )
                st.plotly_chart(fig_bar, width="stretch", key="bmo_chart_bar")

        with right:
            st.subheader("Status mix")
            status_counts = fdf["status"].value_counts()
            if not status_counts.empty:
                fig_status = go.Figure(
                    go.Pie(
                        labels=status_counts.index, values=status_counts.values, hole=0.55,
                        marker_colors=[STATUS_COLORS.get(s, MUTED) for s in status_counts.index],
                        sort=False,
                    )
                )
                fig_status.update_layout(
                    paper_bgcolor="#fcfcfb",
                    margin=dict(l=10, r=10, t=10, b=10), height=320, showlegend=True,
                    font=dict(color="#0b0b0b"),
                )
                st.plotly_chart(fig_status, width="stretch", key="bmo_chart_status")

        st.caption(
            "🟢 Resolved · 🟡 Active / In Progress · ⚪ Unknown (edit `data.py` to correct)."
        )

    # ================= TAB 2 — Connections =================
    with tab_connections:
        st.subheader("How it all connects")
        st.caption(
            "Fabio → workstream → individual case/incident/initiative → the people involved. "
            "Hover any node for detail; drag to rearrange."
        )
        if fdf.empty:
            st.info("No items match the current filters.")
        else:
            # Keep the network visualization dependency-free.  The app only
            # needs nodes, edges, and positions for this Plotly chart.
            nodes = {"Fabio": {"kind": "center"}}
            edges = []
            for ws in sorted(fdf["workstream"].unique()):
                nodes[ws] = {"kind": "workstream"}
                edges.append(("Fabio", ws))
            for _, row in fdf.iterrows():
                item_label = f"{row['ref'] or row['id']}"
                nodes[item_label] = {
                    "kind": "item", "workstream": row["workstream"],
                    "title": row["title"], "status": row["status"],
                    "itype": row["type"],
                }
                edges.append((row["workstream"], item_label))
                for person in row["people"]:
                    if not person:
                        continue
                    nodes.setdefault(person, {"kind": "person"})
                    edges.append((item_label, person))

            # A stable circular layout is sufficient here and avoids requiring
            # an additional package just to position Plotly nodes.
            import math
            pos = {
                node: (math.cos(2 * math.pi * i / max(len(nodes), 1)),
                       math.sin(2 * math.pi * i / max(len(nodes), 1)))
                for i, node in enumerate(nodes)
            }
            edge_x, edge_y = [], []
            for a, b in edges:
                edge_x += [pos[a][0], pos[b][0], None]
                edge_y += [pos[a][1], pos[b][1], None]
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y, mode="lines",
                line=dict(width=1, color="#c3c2b7"), hoverinfo="none",
            )

            node_traces = []
            kind_style = {
                "center": dict(size=34, color="#0b0b0b", symbol="star"),
                "workstream": dict(size=26, color=None, symbol="square"),
                "item": dict(size=14, color=None, symbol="circle"),
                "person": dict(size=12, color="#c3c2b7", symbol="diamond"),
            }
            for kind in ["item", "person", "workstream", "center"]:
                kind_nodes = [n for n, d in nodes.items() if d.get("kind") == kind]
                if not kind_nodes:
                    continue
                xs = [pos[n][0] for n in kind_nodes]
                ys = [pos[n][1] for n in kind_nodes]
                style = kind_style[kind]
                if kind == "workstream":
                    colors = [WORKSTREAMS.get(n, MUTED) for n in kind_nodes]
                elif kind == "item":
                    colors = [WORKSTREAMS.get(nodes[n].get("workstream"), MUTED) for n in kind_nodes]
                else:
                    colors = style["color"]

                hover = []
                for n in kind_nodes:
                    d = nodes[n]
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
                        text=kind_nodes if kind in ("center", "workstream") else None,
                        textposition="top center",
                        hovertext=hover, hoverinfo="text",
                        marker=dict(
                            size=style["size"], color=colors, symbol=style["symbol"],
                            line=dict(width=1, color="white"),
                        ),
                        name=kind, showlegend=False,
                    )
                )

            fig_net = go.Figure(data=[edge_trace] + node_traces)
            fig_net.update_layout(
                plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
                margin=dict(l=10, r=10, t=10, b=10), height=560,
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                font=dict(color="#0b0b0b"),
            )
            st.plotly_chart(fig_net, width="stretch", key="bmo_chart_network")

        st.subheader("Top collaborators")
        people_flat = [p for plist in fdf["people"] for p in plist if p]
        if people_flat:
            people_counts = pd.Series(people_flat).value_counts().sort_values()
            fig_people = go.Figure(
                go.Bar(x=people_counts.values, y=people_counts.index, orientation="h",
                       marker_color="#2a78d6")
            )
            fig_people.update_layout(
                plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
                margin=dict(l=10, r=10, t=10, b=10), height=280,
                xaxis=dict(title="Items together", gridcolor="#e1e0d9"),
                font=dict(color="#0b0b0b"),
            )
            st.plotly_chart(fig_people, width="stretch", key="bmo_chart_people")
        else:
            st.info("No named collaborators in the current filter.")

    # ================= TAB 3 — Detail Log =================
    with tab_detail:
        st.subheader("Full detail log")
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
        display_cols = {
            "start": "Date", "type": "Type", "ref": "Ref", "title": "Title",
            "workstream": "Workstream", "status_dot": "Status", "role": "Role",
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