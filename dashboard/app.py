"""
T12: BW Morph Migration Suite (SAP Fiori Horizon Launchpad + Unified 8-Stage Studio)
Decoupled Streamlit frontend communicating exclusively with FastAPI (localhost:8001).
Flow:
  1. BW Morph Home: SAP S21 Connection & Live Sync Acceptance -> Clean Fiori Studio Tile Box
  2. Unified BW Migration Studio: Single centralized page with Object Selector + 8-Stage Workflow
"""

import json
import os
from typing import Any, Dict, List, Optional
import pandas as pd
import requests
import streamlit as st

API_BASE = os.getenv("BW_MORPH_API_URL", "http://127.0.0.1:8001/api/v1")

st.set_page_config(
    page_title="BWMorph | SAP Datasphere Migration Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------------------
# SAP Fiori Horizon (sap_horizon) Design System CSS
# ------------------------------------------------------------------------------
st.markdown(
    """
    <style>
    header[data-testid="stHeader"], #MainMenu, footer {
        display: none !important;
    }
    html, body, .stApp, [class*="css"] {
        background-color: #F5F6F7 !important;
        color: #131E29 !important;
        font-family: "72", "72full", "Segoe UI", Arial, Helvetica, sans-serif !important;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1400px !important;
    }
    .fiori-shell {
        background-color: #FFFFFF;
        border: 1px solid #D9E0E6;
        padding: 1rem 1.4rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(34, 53, 72, 0.08);
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.1rem;
    }
    .fiori-shell-title {
        font-size: 1.18rem;
        font-weight: 700;
        color: #131E29;
        margin: 0;
    }
    .fiori-shell-sub {
        font-size: 0.82rem;
        color: #556B82;
        margin: 0;
    }
    .status-pill-ok {
        display: inline-block;
        background-color: #EBF5EB;
        color: #188918;
        border: 1px solid #B7E0B7;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .status-pill-info {
        display: inline-block;
        background-color: #EBF3FE;
        color: #0070F2;
        border: 1px solid #B3D4FC;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .fiori-tile {
        background-color: #FFFFFF;
        border: 1px solid #E5E9ED;
        border-radius: 16px;
        box-shadow: 0 0 2px rgba(34, 53, 72, 0.20), 0 2px 4px rgba(34, 53, 72, 0.20);
        padding: 1.35rem 1.5rem;
        min-height: 145px;
        margin-bottom: 0.65rem;
    }
    .fiori-tile-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #131E29;
        margin-bottom: 0.45rem;
    }
    .fiori-tile-desc {
        font-size: 0.88rem;
        color: #556B82;
        line-height: 1.4;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid #DCE2E8 !important;
        box-shadow: 0 1px 3px rgba(34, 53, 72, 0.08) !important;
        padding: 0.85rem 1rem !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #0070F2 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #0057D2 !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #0070F2 !important;
        border: 1px solid #0070F2 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        st.error(f"API GET Error ({path}): {exc}")
        return None


def api_post(path: str, payload: Dict[str, Any], timeout: int = 30) -> Optional[Dict[str, Any]]:
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        st.error(f"API POST Error ({path}): {exc}")
        return None


def _build_columns_df(obj: Dict[str, Any]) -> pd.DataFrame:
    meta = obj.get("raw_metadata", {})
    obj_type = obj.get("object_type", "")
    rows: List[Dict[str, Any]] = []

    if obj_type == "INFOOBJECT":
        rows.append({
            "Include": True,
            "Source Field": obj["tech_name"],
            "Target Column": obj["tech_name"],
            "CSN Type": "cds.String",
            "Length": int(meta.get("length", 20) or 20),
            "Scale": 0,
            "Key": True,
            "Business Label": obj.get("description", obj["tech_name"])[:60],
        })
        for comp in meta.get("compounding", []):
            rows.append({
                "Include": True,
                "Source Field": comp,
                "Target Column": comp,
                "CSN Type": "cds.String",
                "Length": 10,
                "Scale": 0,
                "Key": True,
                "Business Label": f"Compounded {comp}",
            })
        for f in meta.get("fields", []):
            fname = f.get("name", "")
            if fname and fname != obj["tech_name"]:
                rows.append({
                    "Include": True,
                    "Source Field": fname,
                    "Target Column": fname,
                    "CSN Type": "cds.Decimal" if f.get("type") in ("CURR", "DEC", "QUAN") else "cds.String",
                    "Length": int(f.get("length", 30) or 30),
                    "Scale": int(f.get("decimals", 0) or 0),
                    "Key": bool(f.get("is_key", False)),
                    "Business Label": fname,
                })
    elif obj_type == "TRANSFORMATION":
        for m in meta.get("field_mappings", []):
            tgt = str(m.get("target", ""))
            is_amt = any(tok in tgt.upper() for tok in ("AMOUNT", "NET", "VAL", "QTY"))
            rows.append({
                "Include": True,
                "Source Field": m.get("source", ""),
                "Target Column": tgt,
                "CSN Type": "cds.Decimal" if is_amt else "cds.String",
                "Length": 17 if is_amt else 30,
                "Scale": 2 if is_amt else 0,
                "Key": False,
                "Business Label": f"{m.get('rule', 'DIRECT')}: {tgt}",
            })
    else:
        for k in meta.get("keys", []):
            rows.append({
                "Include": True,
                "Source Field": k,
                "Target Column": k,
                "CSN Type": "cds.String",
                "Length": 30,
                "Scale": 0,
                "Key": True,
                "Business Label": f"Key {k}",
            })
        for f in meta.get("fields", []):
            fname = f.get("name") if isinstance(f, dict) else str(f)
            if fname and not any(r["Target Column"] == fname for r in rows):
                is_amt = any(tok in fname.upper() for tok in ("AMOUNT", "NET", "VAL", "QTY"))
                rows.append({
                    "Include": True,
                    "Source Field": fname,
                    "Target Column": fname,
                    "CSN Type": "cds.Decimal" if is_amt else "cds.String",
                    "Length": 17 if is_amt else 30,
                    "Scale": 2 if is_amt else 0,
                    "Key": bool(f.get("is_key", False)) if isinstance(f, dict) else False,
                    "Business Label": fname,
                })

    if not rows:
        rows.append({
            "Include": True,
            "Source Field": "OBJECT_ID",
            "Target Column": "OBJECT_ID",
            "CSN Type": "cds.String",
            "Length": 30,
            "Scale": 0,
            "Key": True,
            "Business Label": obj["tech_name"],
        })
    return pd.DataFrame(rows)


def _reset_object_workspace(obj: Dict[str, Any]) -> None:
    """Initialize per-object editable state when user selects a new BW object."""
    st.session_state.active_tech_name = obj["tech_name"]
    st.session_state.map_columns_df = _build_columns_df(obj)
    st.session_state.map_space = st.session_state.get("default_ns", "")
    st.session_state.map_target_name = obj["tech_name"]
    st.session_state.map_label = obj.get("description", obj["tech_name"])
    cat_map = {
        "INFOOBJECT": "#DIMENSION",
        "TRANSFORMATION": "#CUBE",
        "COMPOSITE_PROVIDER": "#CUBE",
        "BEX_QUERY": "#CUBE",
        "ADSO": "#FACT",
    }
    st.session_state.map_category = cat_map.get(obj["object_type"], "#FACT")
    st.session_state.map_sql_where = ""
    st.session_state.compiled_artifact = None
    st.session_state.validation_result = None
    st.session_state.delivery_result = None


# ------------------------------------------------------------------------------
# Session State Defaults
# ------------------------------------------------------------------------------
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "home"  # home | studio
if "connection_accepted" not in st.session_state:
    st.session_state.connection_accepted = False
if "stage_idx" not in st.session_state:
    st.session_state.stage_idx = 1  # 1..8
if "active_tech_name" not in st.session_state:
    st.session_state.active_tech_name = None
if "default_ns" not in st.session_state:
    st.session_state.default_ns = ""

health = api_get("/health", timeout=5)
stats = api_get("/repository/stats") or {}
sap_sid = health.get("sap_sid", "S21") if health else "S21"
sap_host = health.get("sap_host", "192.168.1.55") if health else "192.168.1.55"
sap_ok = bool(health and health.get("sap_reachable"))
conn_label = f"● SAP BW/S4: Connected ({sap_sid} · Read-Only)" if sap_ok else "● SAP S21: Offline"
validated_cnt = stats.get("by_status", {}).get("VALIDATED", 0)
total_cnt = stats.get("total_objects", 0)

# ------------------------------------------------------------------------------
# Persistent SAP Fiori Shell Header
# ------------------------------------------------------------------------------
subtitle = (
    "SAP Datasphere Migration Cockpit — Connect, Sync & Launch Studio"
    if st.session_state.view_mode == "home"
    else "Unified 8-Stage Workspace: Discover · Analyze · Explore Lineage · Assess · Map · Transform · Validate · Deliver"
)
st.markdown(
    f"""
    <div class="fiori-shell">
        <div>
            <p class="fiori-shell-title">⚡ BW Morph Migration Suite</p>
            <p class="fiori-shell-sub">{subtitle}</p>
        </div>
        <div>
            <span class="status-pill-ok">{conn_label}</span>
            <span class="status-pill-info">Migration Progress: {validated_cnt} / {total_cnt} Validated</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not health:
    st.error("FastAPI backend is not reachable at http://127.0.0.1:8001. Start it first.")
    st.stop()


# ==============================================================================
# VIEW 1: BW MORPH HOME (S21 Connection/Sync Acceptance + Launchpad Box)
# ==============================================================================
if st.session_state.view_mode == "home":
    st.subheader("SAP Datasphere Migration Cockpit")
    st.caption("Verify your SAP BW / S/4HANA connection details, sync live metadata from S21, and open the Unified BW Migration Studio.")

    with st.container(border=True):
        st.markdown("#### Step 1 — SAP S21 Connection Details & Live Sync")
        c1, c2, c3, c4, c5 = st.columns([1.4, 0.7, 0.7, 1.1, 1.4])
        with c1:
            st.text_input("SAP Host / IP", value=sap_host, key="conn_host")
        with c2:
            st.text_input("System ID", value=sap_sid, key="conn_sid")
        with c3:
            st.text_input("Client", value="200", key="conn_client")
        with c4:
            st.text_input("SAP User (Read-Only)", value="INT_SAMARTH", key="conn_user")
        with c5:
            st.session_state.default_ns = st.text_input(
                "Target CSN Namespace",
                value=st.session_state.default_ns,
                placeholder="Blank = Active Space (no SAP_*)",
            )

        if st.button("✓ Accept Details & Sync Live S21", type="primary"):
            with st.spinner("Testing S21 connection, syncing live OData metadata, classifying & building lineage..."):
                scan_res = api_get("/scan/start?mode=live&limit=30", timeout=60)
                api_get("/classify/run")
                api_get("/graph/build")
            if scan_res:
                st.session_state.connection_accepted = True
                st.session_state.sync_banner = (
                    f"Connection accepted! Synced {scan_res.get('total_scanned', 0)} live objects from {sap_sid} (Client 200)."
                )
                st.rerun()

        if st.session_state.get("sync_banner"):
            st.success(st.session_state.sync_banner)

    st.write("")
    box_col1, box_col2 = st.columns(2)
    ready_to_open = st.session_state.connection_accepted or total_cnt > 0

    with box_col1:
        st.markdown(
            f"""
            <div class="fiori-tile">
                <div class="fiori-tile-title">🚀 BW Migration Studio (Unified 8-Stage Workspace)</div>
                <div class="fiori-tile-desc">
                    Single centralized studio for all BW object types (InfoObjects, ADSOs, DataSources, Transformations,
                    CompositeProviders, BEx Queries & Process Chains).<br/><br/>
                    <strong>Cataloged Objects:</strong> {total_cnt} &nbsp;|&nbsp;
                    <strong>Lineage Edges:</strong> {stats.get('total_dependencies', 0)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Open BW Migration Studio",
            type="primary",
            use_container_width=True,
            disabled=not ready_to_open,
            help="Click '✓ Accept Details & Sync Live S21' above first" if not ready_to_open else "Launch Unified 8-Stage Studio",
        ):
            st.session_state.view_mode = "studio"
            st.session_state.stage_idx = 1
            st.rerun()

    with box_col2:
        st.markdown(
            f"""
            <div class="fiori-tile">
                <div class="fiori-tile-title">📊 Live Repository & Wave Summary</div>
                <div class="fiori-tile-desc">
                    Avg Complexity: <strong>{stats.get('avg_complexity', 0)} / 5.0</strong> &nbsp;|&nbsp;
                    Validated: <strong>{validated_cnt} / {total_cnt}</strong><br/><br/>
                    All CSN outputs use Active Space naming (no reserved <code>SAP_*</code> namespace) and Pure SQL Views.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("View Path 1–7 Breakdown", expanded=False):
            if stats.get("by_path"):
                st.bar_chart(pd.DataFrame(list(stats["by_path"].items()), columns=["Path", "Count"]).set_index("Path"))


# ==============================================================================
# VIEW 2: UNIFIED 8-STAGE BW MIGRATION STUDIO
# ==============================================================================
else:
    if st.button("← Back to BW Morph Home", key="back_home", type="secondary"):
        st.session_state.view_mode = "home"
        st.rerun()

    # Single Clean Object Selector Card (Native bordered container — zero empty divs)
    with st.container(border=True):
        sel_c1, sel_c2, sel_c3, sel_c4 = st.columns([1.1, 1.5, 2.0, 0.9])
        type_options = [
            "All Types",
            "INFOOBJECT",
            "ADSO",
            "DATASOURCE",
            "TRANSFORMATION",
            "COMPOSITE_PROVIDER",
            "BEX_QUERY",
            "PROCESS_CHAIN",
            "SOURCE_SYSTEM",
        ]
        with sel_c1:
            filter_type = st.selectbox("BW Object Type", type_options, key="unified_type_filter")
        with sel_c2:
            search_text = st.text_input("Search Objects", placeholder="Filter by technical name or description...", key="unified_search")
        with sel_c4:
            st.write("")
            st.write("")
            if st.button("⟳ Sync Live S21", use_container_width=True, type="secondary"):
                with st.spinner("Syncing live SAP S21 OData objects..."):
                    api_get("/scan/start?mode=live&limit=30", timeout=60)
                    api_get("/classify/run")
                    api_get("/graph/build")
                st.rerun()

        query_url = "/repository/objects?limit=250"
        if filter_type != "All Types":
            query_url += f"&object_type={filter_type}"
        objs_resp = api_get(query_url) or {"items": []}
        all_items: List[Dict[str, Any]] = objs_resp.get("items", [])

        if search_text.strip():
            q = search_text.strip().lower()
            all_items = [o for o in all_items if q in o["tech_name"].lower() or q in o.get("description", "").lower()]

        if not all_items:
            st.warning("No BW objects match your filter. Click '⟳ Sync Live S21' or clear the search filter.")
            st.stop()

        tech_names = [o["tech_name"] for o in all_items]
        default_pos = tech_names.index(st.session_state.active_tech_name) if st.session_state.active_tech_name in tech_names else 0
        with sel_c3:
            chosen_tech = st.selectbox("Select BW Object to Migrate", tech_names, index=default_pos, key="unified_object_select")

        selected_obj = next(o for o in all_items if o["tech_name"] == chosen_tech)
        if st.session_state.active_tech_name != chosen_tech:
            _reset_object_workspace(selected_obj)

        st.caption(
            f"**Active Object:** `{selected_obj['tech_name']}` &nbsp;|&nbsp; "
            f"**Type:** `{selected_obj['object_type']}` &nbsp;|&nbsp; "
            f"**Path:** `{selected_obj.get('migration_path', 'N/A')}` &nbsp;|&nbsp; "
            f"**Complexity:** `{selected_obj.get('complexity_score', 1)}/5` &nbsp;|&nbsp; "
            f"**Status:** `{selected_obj.get('status', 'PENDING')}`"
        )

    # SINGLE Clean 8-Stage Horizontal Stepper (No duplicate HTML bar!)
    STAGES = [
        "1. Discover",
        "2. Analyze",
        "3. Explore Lineage",
        "4. Assess",
        "5. Map",
        "6. Transform",
        "7. Validate",
        "8. Deliver",
    ]
    cur_stage: int = st.session_state.stage_idx

    jmp_cols = st.columns(len(STAGES))
    for idx, lbl in enumerate(STAGES, start=1):
        btn_type = "primary" if idx == cur_stage else "secondary"
        if jmp_cols[idx - 1].button(lbl, key=f"jmp_{idx}", use_container_width=True, type=btn_type):
            st.session_state.stage_idx = idx
            st.rerun()

    st.write("")

    # Stage Workspace Content inside a native bordered card
    with st.container(border=True):
        if cur_stage == 1:
            st.markdown(f"### Stage 1: Discover — `{selected_obj['tech_name']}`")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("BW Object Type", selected_obj["object_type"])
            d2.metric("Source System", sap_sid)
            d3.metric("Repository Status", selected_obj.get("status", "PENDING"))
            d4.metric("Total Cataloged Objects", total_cnt)

            if st.button("Refresh Metadata from SAP S21 (Read-Only)", type="secondary"):
                with st.spinner("Refreshing live S21 OData metadata..."):
                    api_get("/scan/start?mode=live&limit=30", timeout=60)
                st.success("Live S21 metadata refreshed.")

            with st.expander("Raw Discovered SAP Metadata (JSON)", expanded=True):
                st.json(selected_obj.get("raw_metadata", {}))

        elif cur_stage == 2:
            st.markdown(f"### Stage 2: Analyze Structure & Properties — `{selected_obj['tech_name']}`")
            meta = selected_obj.get("raw_metadata", {})

            a1, a2 = st.columns(2)
            with a1:
                st.markdown("#### Technical Properties")
                st.write(f"- **Technical Name:** `{selected_obj['tech_name']}`")
                st.write(f"- **Description:** {selected_obj.get('description', 'N/A')}")
                st.write(f"- **Object Type:** `{selected_obj['object_type']}`")
                if meta.get("service_url"):
                    st.write(f"- **OData Service URL:** `{meta['service_url']}`")
                if meta.get("compounding"):
                    st.write(f"- **Compounding Keys:** `{', '.join(meta['compounding'])}`")
                if meta.get("attributes"):
                    st.write(f"- **Attributes:** `{', '.join(meta['attributes'])}`")

            with a2:
                st.markdown("#### Fields & Schema Structure")
                df_preview = _build_columns_df(selected_obj)[["Source Field", "CSN Type", "Length", "Scale", "Key"]]
                st.dataframe(df_preview, use_container_width=True)

            if meta.get("routines_abap"):
                st.markdown("#### ABAP Routines Detected")
                st.json(meta["routines_abap"])

        elif cur_stage == 3:
            st.markdown(f"### Stage 3: Explore Lineage — `{selected_obj['tech_name']}`")
            lineage = api_get(f"/graph/lineage/{selected_obj['tech_name']}") or {}

            l1, l2, l3 = st.columns(3)
            l1.metric("Assigned Topological Wave", f"Wave {lineage.get('wave_id', 'N/A')}")
            l2.metric("Upstream Sources", len(lineage.get("upstream", [])))
            l3.metric("Downstream Consumers", len(lineage.get("downstream", [])))

            if lineage.get("in_cycle"):
                st.warning("Circular dependency detected — Tarjan's SCC isolates non-fatal back-edges for wave ordering.")

            col_up, col_dn = st.columns(2)
            with col_up:
                st.markdown("#### ⬅ Upstream Dependencies (Feeds Into This Object)")
                if lineage.get("upstream"):
                    st.dataframe(pd.DataFrame(lineage["upstream"]), use_container_width=True)
                else:
                    st.info("No upstream dependencies (root/source layer object).")
            with col_dn:
                st.markdown("#### ➡ Downstream Impact (Consumes This Object)")
                if lineage.get("downstream"):
                    st.dataframe(pd.DataFrame(lineage["downstream"]), use_container_width=True)
                else:
                    st.info("No downstream dependents (consumption/leaf object).")

        elif cur_stage == 4:
            st.markdown(f"### Stage 4: Assess Compatibility & Migration Approach — `{selected_obj['tech_name']}`")
            assess = api_get(f"/classify/assess/{selected_obj['tech_name']}")

            if assess:
                s1, s2, s3 = st.columns(3)
                s1.metric("Migration Path", assess.get("migration_path", "Path 1"))
                s2.metric("Complexity Score", f"{assess.get('complexity_score', 1)} / 5")
                s3.metric("Datasphere Compatibility", "Compatible" if assess.get("compatible") else "Needs Review")

                st.info(f"**Recommended SAP Datasphere Target:** {assess.get('recommended_target')}")
                st.success(f"**Migration Approach:** {assess.get('migration_approach')}")

                if assess.get("risks"):
                    st.markdown("#### Architectural Risk Flags")
                    for r in assess["risks"]:
                        st.warning(r)
                else:
                    st.success("Zero structural risks detected (no circular blocks, no unhandled ABAP routines).")

        elif cur_stage == 5:
            st.markdown(f"### Stage 5: Map to SAP Datasphere Targets — `{selected_obj['tech_name']}`")
            st.caption("Edit target columns, CSN data types, lengths, scales, primary keys, target entity name, and SQL filters directly.")

            m1, m2 = st.columns(2)
            with m1:
                st.session_state.map_space = st.text_input(
                    "Target CSN Namespace (Leave blank for Active Space)",
                    value=st.session_state.get("map_space", ""),
                    placeholder="Blank = Active Datasphere Space (never use SAP_*)",
                )
                st.session_state.map_target_name = st.text_input(
                    "Target Entity / View Name",
                    value=st.session_state.get("map_target_name", selected_obj["tech_name"]),
                )
            with m2:
                st.session_state.map_label = st.text_input(
                    "Business Label (@EndUserText.label)",
                    value=st.session_state.get("map_label", selected_obj.get("description", selected_obj["tech_name"])),
                )
                cats = ["#DIMENSION", "#FACT", "#STAGING", "#CUBE", "#TEXT"]
                cur_cat = st.session_state.get("map_category", "#FACT")
                st.session_state.map_category = st.selectbox(
                    "Analytics Data Category",
                    cats,
                    index=cats.index(cur_cat) if cur_cat in cats else 0,
                )

            c_opt1, c_opt2 = st.columns(2)
            with c_opt1:
                st.session_state.map_inc_text = st.checkbox(
                    "Include _TEXT Entity (#TEXT)",
                    value=bool(selected_obj["object_type"] == "INFOOBJECT"),
                )
            with c_opt2:
                st.session_state.map_inc_cl = st.checkbox(
                    "Include _CHANGELOG Audit Entity",
                    value=bool(selected_obj["object_type"] == "ADSO"),
                )

            st.markdown("#### Editable Field & Column Mapping Grid")
            edited_df = st.data_editor(
                st.session_state.map_columns_df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Include": st.column_config.CheckboxColumn("Include", default=True),
                    "Source Field": st.column_config.TextColumn("Source BW Field"),
                    "Target Column": st.column_config.TextColumn("Target Datasphere Column"),
                    "CSN Type": st.column_config.SelectboxColumn(
                        "CSN Data Type",
                        options=["cds.String", "cds.Decimal", "cds.Date", "cds.Time", "cds.Integer", "cds.Double", "cds.Boolean", "cds.Binary", "cds.LargeString"],
                        default="cds.String",
                    ),
                    "Length": st.column_config.NumberColumn("Length / Precision", min_value=0, max_value=5000, step=1),
                    "Scale": st.column_config.NumberColumn("Scale", min_value=0, max_value=10, step=1),
                    "Key": st.column_config.CheckboxColumn("Primary Key", default=False),
                    "Business Label": st.column_config.TextColumn("Business Label"),
                },
                key="unified_col_editor",
            )
            st.session_state.map_columns_df = edited_df

            st.session_state.map_sql_where = st.text_area(
                "Optional SQL WHERE Filter / Transformation Logic",
                value=st.session_state.get("map_sql_where", ""),
                placeholder="e.g. AMOUNT > 0",
                height=80,
            )

        elif cur_stage == 6:
            st.markdown(f"### Stage 6: Transform & Generate Datasphere Artifacts — `{selected_obj['tech_name']}`")

            df_cols = st.session_state.map_columns_df
            col_payload = [
                {
                    "include": bool(row.get("Include", True)),
                    "source_field": str(row.get("Source Field", "")),
                    "target_column": str(row.get("Target Column", "")),
                    "csn_type": str(row.get("CSN Type", "cds.String")),
                    "length": int(row.get("Length", 30) or 30),
                    "scale": int(row.get("Scale", 0) or 0),
                    "is_key": bool(row.get("Key", False)),
                    "label": str(row.get("Business Label", "")),
                }
                for _, row in df_cols.iterrows()
            ] if df_cols is not None else []

            compile_req = {
                "space_name": st.session_state.get("map_space", ""),
                "target_name": st.session_state.get("map_target_name", selected_obj["tech_name"]),
                "source_name": selected_obj["tech_name"],
                "description": st.session_state.get("map_label", ""),
                "analytics_category": st.session_state.get("map_category", "#FACT"),
                "include_text_entity": bool(st.session_state.get("map_inc_text", False)),
                "include_changelog_entity": bool(st.session_state.get("map_inc_cl", False)),
                "sql_where": st.session_state.get("map_sql_where", ""),
                "columns": col_payload,
            }

            compiled = api_post("/generate/compile", compile_req)
            if compiled:
                st.session_state.compiled_artifact = compiled
                if compiled.get("warnings"):
                    for w in compiled["warnings"]:
                        st.warning(w)
                tab_csn, tab_sql = st.tabs(["📄 SAP CSN v1.0 JSON", "🗄️ Pure Datasphere SQL View"])
                with tab_csn:
                    st.code(json.dumps(compiled["csn"], indent=2), language="json")
                with tab_sql:
                    st.code(compiled["sql"], language="sql")

        elif cur_stage == 7:
            st.markdown(f"### Stage 7: Validate Mappings, Schema & Dependencies — `{selected_obj['tech_name']}`")
            compiled = st.session_state.get("compiled_artifact")
            if not compiled:
                df_cols = st.session_state.map_columns_df
                col_payload = [
                    {
                        "include": bool(r.get("Include", True)),
                        "source_field": str(r.get("Source Field", "")),
                        "target_column": str(r.get("Target Column", "")),
                        "csn_type": str(r.get("CSN Type", "cds.String")),
                        "length": int(r.get("Length", 30) or 30),
                        "scale": int(r.get("Scale", 0) or 0),
                        "is_key": bool(r.get("Key", False)),
                        "label": str(r.get("Business Label", "")),
                    }
                    for _, r in df_cols.iterrows()
                ]
                compiled = api_post("/generate/compile", {
                    "space_name": st.session_state.get("map_space", ""),
                    "target_name": st.session_state.get("map_target_name", selected_obj["tech_name"]),
                    "source_name": selected_obj["tech_name"],
                    "description": st.session_state.get("map_label", ""),
                    "analytics_category": st.session_state.get("map_category", "#FACT"),
                    "include_text_entity": bool(st.session_state.get("map_inc_text", False)),
                    "include_changelog_entity": bool(st.session_state.get("map_inc_cl", False)),
                    "sql_where": st.session_state.get("map_sql_where", ""),
                    "columns": col_payload,
                })
                st.session_state.compiled_artifact = compiled

            if compiled:
                val_res = api_post("/generate/validate", {
                    "tech_name": selected_obj["tech_name"],
                    "csn": compiled["csn"],
                    "sql": compiled["sql"],
                })
                if val_res:
                    st.session_state.validation_result = val_res
                    if val_res["valid"]:
                        st.success("All Pre-Import Validation Gates PASSED! Ready for Datasphere delivery.")
                    else:
                        st.error("Validation detected issues — review failed checks below.")
                    for chk in val_res["checks"]:
                        icon = "✅" if chk["passed"] else "❌"
                        st.write(f"{icon} **{chk['name']}**: {chk['message']}")

        elif cur_stage == 8:
            st.markdown(f"### Stage 8: Deliver Artifacts & Track Progress — `{selected_obj['tech_name']}`")
            compiled = st.session_state.get("compiled_artifact")
            target_name = st.session_state.get("map_target_name", selected_obj["tech_name"])

            if not compiled:
                st.warning("Run Stage 6 (Transform) or Stage 7 (Validate) before delivering artifacts.")
            else:
                csn_str = json.dumps(compiled["csn"], indent=2)
                sql_str = compiled["sql"]

                d_c1, d_c2, d_c3 = st.columns(3)
                with d_c1:
                    st.download_button(
                        label="⬇ Download CSN (.csn.json)",
                        data=csn_str,
                        file_name=f"{target_name}.csn.json",
                        mime="application/json",
                        use_container_width=True,
                    )
                with d_c2:
                    st.download_button(
                        label="⬇ Download SQL View (.sql)",
                        data=sql_str,
                        file_name=f"{target_name}.sql",
                        mime="text/plain",
                        use_container_width=True,
                    )
                with d_c3:
                    if st.button("🚀 Save to Output & Mark Validated", type="primary", use_container_width=True):
                        deliv = api_post("/generate/deliver", {
                            "tech_name": selected_obj["tech_name"],
                            "target_name": target_name,
                            "csn": compiled["csn"],
                            "sql": sql_str,
                        })
                        if deliv:
                            st.session_state.delivery_result = deliv
                            st.success(f"Delivered `{deliv['csn_file']}` and marked `{selected_obj['tech_name']}` as VALIDATED!")

                if st.session_state.get("delivery_result"):
                    st.json(st.session_state.delivery_result)

            st.divider()
            st.markdown("#### Overall Repository Migration Progress")
            fresh_stats = api_get("/repository/stats") or {}
            st.write(fresh_stats.get("by_status", {}))

    # Bottom Sequential Stage Navigation
    st.write("")
    nav_l, nav_r = st.columns([1, 1])
    with nav_l:
        if cur_stage > 1:
            if st.button(f"← Previous: {STAGES[cur_stage - 2]}", key="nav_prev", type="secondary"):
                st.session_state.stage_idx = cur_stage - 1
                st.rerun()
    with nav_r:
        if cur_stage < len(STAGES):
            if st.button(f"Next: {STAGES[cur_stage]} →", key="nav_next", type="primary"):
                st.session_state.stage_idx = cur_stage + 1
                st.rerun()
