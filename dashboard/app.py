"""
T12: Migration Dashboard & Cutover Tracker (Streamlit App)
Visualizes object inventory, wave sequence, path breakdown, and CSN code preview.
"""

import streamlit as st
import json
import pandas as pd
from repository.db_manager import RepositoryManager
from graph.t1_dependency_builder import DependencyGraphBuilder
from graph.t2_classifier import ObjectClassifier
from generators.t5_master_data import MasterDataMigrator
from generators.t6_transformation import TransformationTranslator

st.set_page_config(
    page_title="BW/4HANA -> Datasphere Migration Accelerator",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ SAP BW/4HANA to SAP Datasphere Migration Accelerator")
st.caption("Modular Tool Suite (T0 - T12) | Shared Metadata Repository & CSN Code Generator")

# Initialize Repository
repo = RepositoryManager(db_path="metadata_repo.db", use_duckdb=False)
classifier = ObjectClassifier(repo)
graph_builder = DependencyGraphBuilder(repo)
master_migrator = MasterDataMigrator(repo)
tran_translator = TransformationTranslator(repo)

# Sidebar
st.sidebar.header("Migration Control Center")
page = st.sidebar.radio("Navigation", ["Dashboard & Inventory", "Dependency Graph & Waves", "Path 2: InfoObjects Migrator", "Path 3: Transformations Transpiler"])

objects = repo.get_all_objects()
df_objs = pd.DataFrame(objects)

if page == "Dashboard & Inventory":
    st.subheader("📊 Executive Overview & Object Inventory")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total In-Scope Objects", len(objects))
    c2.metric("InfoObjects (Path 2)", len(df_objs[df_objs["migration_path"] == "Path 2"]) if not df_objs.empty else 0)
    c3.metric("Transformations (Path 3)", len(df_objs[df_objs["migration_path"] == "Path 3"]) if not df_objs.empty else 0)
    c4.metric("Avg Complexity Score", f"{df_objs['complexity_score'].mean():.1f}/5.0" if not df_objs.empty else "N/A")

    st.write("---")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### Object Inventory Table")
        if not df_objs.empty:
            st.dataframe(df_objs[["tech_name", "object_type", "migration_path", "complexity_score", "status", "description"]], use_container_width=True)

    with col_right:
        st.markdown("### Path Breakdown")
        if not df_objs.empty:
            path_counts = df_objs["migration_path"].value_counts().reset_index()
            path_counts.columns = ["Migration Path", "Count"]
            st.bar_chart(path_counts.set_index("Migration Path"))

elif page == "Dependency Graph & Waves":
    st.subheader("🕸️ Object Dependency Graph & Migration Waves")

    waves = graph_builder.get_topological_waves()
    for wave in waves:
        with st.expander(f"📌 {wave['wave_name']} ({len(wave['objects'])} objects)", expanded=True):
            st.write(", ".join([f"`{obj}`" for obj in wave["objects"]]))

    st.markdown("### DOT Graph Format")
    st.code(graph_builder.generate_dot_string(), language="dot")

elif page == "Path 2: InfoObjects Migrator":
    st.subheader("🧬 Path 2: Master Data & InfoObject Generator (T5)")
    st.markdown("Converts Characteristics, Key Figures, Attributes, Texts, and Compounding into SAP Datasphere CSN / Local Tables.")

    io_objs = df_objs[df_objs["migration_path"] == "Path 2"]["tech_name"].tolist() if not df_objs.empty else []
    selected_io = st.selectbox("Select InfoObject to Migrating:", io_objs if io_objs else ["0CUSTOMER"])

    if st.button("Generate CSN for InfoObject"):
        try:
            csn = master_migrator.convert_infoobject(selected_io)
            st.success(f"Generated Datasphere CSN JSON for {selected_io}")
            st.json(csn)
        except Exception as e:
            st.error(f"Error generating CSN: {e}")

elif page == "Path 3: Transformations Transpiler":
    st.subheader("🔄 Path 3: Transformation & ABAP Routine Translator (T6)")
    st.markdown("Transpiles direct rules, formulas, and ABAP Start/Field routines into Datasphere SQL Views.")

    tr_objs = df_objs[df_objs["migration_path"] == "Path 3"]["tech_name"].tolist() if not df_objs.empty else []
    selected_tr = st.selectbox("Select Transformation:", tr_objs if tr_objs else ["TR_STG_TO_CUBE"])

    if st.button("Transpile Transformation to SQL View"):
        try:
            res = tran_translator.translate_transformation(selected_tr)
            st.success(f"Transpiled {selected_tr} successfully!")

            st.markdown("#### Transpiled SQL View Query:")
            st.code(res["sql"], language="sql")

            if res["warnings"]:
                st.warning("⚠️ Review Warnings Flagged for AI/Human Inspection:")
                for w in res["warnings"]:
                    st.write(f"- {w}")

            st.markdown("#### Complete Target CSN JSON:")
            st.json(res["csn"])
        except Exception as e:
            st.error(f"Error transpiling transformation: {e}")
