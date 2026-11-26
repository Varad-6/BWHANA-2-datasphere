"""
Generates a comprehensive Draw.io XML file for BW Morph (BW/4HANA to SAP Datasphere Migration Accelerator).
"""

import html
import os

class DrawIOBuilder:
    def __init__(self):
        self.cells = []
        self.id_counter = 10

    def next_id(self):
        self.id_counter += 1
        return str(self.id_counter)

    def add_cell(self, value, style, x, y, w, h, parent="1", is_vertex=True, source=None, target=None):
        cid = self.next_id()
        esc_val = html.escape(value, quote=True)
        esc_style = html.escape(style, quote=True)
        if is_vertex:
            cell = f'<mxCell id="{cid}" value="{esc_val}" style="{esc_style}" vertex="1" parent="{parent}"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        else:
            src_attr = f' source="{source}"' if source else ''
            tgt_attr = f' target="{target}"' if target else ''
            cell = f'<mxCell id="{cid}" value="{esc_val}" style="{esc_style}" edge="1" parent="{parent}"{src_attr}{tgt_attr}><mxGeometry relative="1" as="geometry"/></mxCell>'
        self.cells.append(cell)
        return cid

    def build_xml(self):
        body = "\n      ".join(self.cells)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2026-11-26T10:25:00.000Z" agent="BW-Morph-Architect" version="22.1.0" type="device">
  <diagram id="bw-morph-architecture" name="BW Morph - End-to-End Migration Flow">
    <mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2000" pageHeight="2600" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
      {body}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""

def create_diagram():
    b = DrawIOBuilder()

    # Colors
    c_bw_bg = "#FFF0F5"
    c_bw_stroke = "#C2185B"
    c_f1_bg = "#E8F5E9"
    c_f1_stroke = "#2E7D32"
    c_f2_bg = "#E3F2FD"
    c_f2_stroke = "#1565C0"
    c_f3_bg = "#FFF8E1"
    c_f3_stroke = "#F57F17"
    c_dsp_bg = "#EDE7F6"
    c_dsp_stroke = "#512DA8"
    c_db_bg = "#ECEFF1"
    c_db_stroke = "#37474F"

    # Title Banner
    b.add_cell(
        "<b>BW Morph: End-to-End SAP BW/4HANA to SAP Datasphere Migration Accelerator</b><br/>"
        "<i>Enterprise Architecture, Pipeline Flow &amp; Object Transpilation Lifecycle (T0 – T12)</i>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#1A237E;strokeColor=#0D47A1;fontColor=#FFFFFF;fontSize=18;fontStyle=1;align=center;shadow=1;",
        40, 20, 1880, 70
    )

    # ==========================================
    # CONTAINER 1: SAP BW / BW/4HANA SOURCE SYSTEM
    # ==========================================
    b.add_cell(
        "<b>SOURCE SYSTEM: SAP BW / BW4HANA</b><br/>(ABAP Metadata Dictionary, CDS Views &amp; Data Persistence Layer)",
        f"swimlane;whiteSpace=wrap;html=1;fillColor={c_bw_bg};strokeColor={c_bw_stroke};fontColor=#880e4f;fontSize=14;fontStyle=1;startSize=40;rounded=1;",
        40, 110, 320, 1100
    )

    # BW Objects in Source
    bw_src = b.add_cell(
        "<b>Source Systems &amp; DataSources</b><br/>"
        "• Tables: ROOSOURCE, ROOSATTR, RSDS<br/>"
        "• S/4HANA ERP, ODP, Flat Files<br/>"
        "• Delta queues (ODQMON)",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#C2185B;fontSize=11;align=left;spacingLeft=8;",
        60, 170, 280, 90
    )

    bw_io = b.add_cell(
        "<b>InfoObjects (Master Data)</b><br/>"
        "• Characteristics (CHA) &amp; Key Figures (KYF)<br/>"
        "• Attribute Tables: /BI0/P*, /BI0/Q* (Live)<br/>"
        "• Text Tables: /BI0/T* (Live)<br/>"
        "• SIDs &amp; Surrogate Maps: /BI0/S*, /BI0/X*, /BI0/Y*<br/>"
        "• Dict: RSDIOBJ, RSDCHABAS, RSDATTR",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#C2185B;fontSize=11;align=left;spacingLeft=8;",
        60, 280, 280, 120
    )

    bw_adso = b.add_cell(
        "<b>ADSO Tables (Persistence Layer)</b><br/>"
        "• Inbound Queue: /BIC/A*1 (Unactivated Data)<br/>"
        "• Active Data: /BIC/A*2 (Activated Master/Fact)<br/>"
        "• Change Log: /BIC/A*3 (Store Delta History)<br/>"
        "• Dict: RSOADSO, RSDDSO, RSDODSOIOBJ<br/>"
        "• Staging, Standard &amp; Write-Optimized",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#C2185B;fontSize=11;align=left;spacingLeft=8;",
        60, 420, 280, 120
    )

    bw_trfn = b.add_cell(
        "<b>Transformations &amp; DTPs</b><br/>"
        "• Tables: RSTRAN, RSTRANRULE, RSTRANROUT<br/>"
        "• Direct Rules, Constants, Formulas<br/>"
        "• ABAP Routines (Start, End, Field, Expert)<br/>"
        "• DTP Definitions: RSBKDTP",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#C2185B;fontSize=11;align=left;spacingLeft=8;",
        60, 560, 280, 110
    )

    bw_hcpr = b.add_cell(
        "<b>CompositeProviders &amp; MultiProviders</b><br/>"
        "• Tables: RSDHCPR, RSDHCPRCOMP, RSDHCPRLNK<br/>"
        "• Left Outer Joins, Inner Joins, Unions<br/>"
        "• Navigational Attributes &amp; In-memory bindings",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#C2185B;fontSize=11;align=left;spacingLeft=8;",
        60, 690, 280, 100
    )

    bw_bex = b.add_cell(
        "<b>BEx Queries / Analytic Queries</b><br/>"
        "• Tables: RSZELTDIR, RSZELTTXT, RSZCALC<br/>"
        "• Restricted &amp; Calculated Key Figures (RKF/CKF)<br/>"
        "• Query Variables, Customer Exits, Formulae",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#C2185B;fontSize=11;align=left;spacingLeft=8;",
        60, 810, 280, 100
    )

    bw_sec = b.add_cell(
        "<b>Process Chains &amp; Security Auth</b><br/>"
        "• Process Chains: RSPCPROCESS, RSPCLOGCHAIN<br/>"
        "• Analysis Authorizations: RSECVAL, RSECBIOBJ<br/>"
        "• Authorization Profiles &amp; Role Mappings",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#C2185B;fontSize=11;align=left;spacingLeft=8;",
        60, 930, 280, 100
    )

    bw_api_node = b.add_cell(
        "<b>SAP BW Metadata Extraction Interface</b><br/>"
        "• RFC via Python (pyrfc / SAP NetWeaver RFC SDK)<br/>"
        "• BAPI_MDPROVIDER_GET_DIMENSIONS<br/>"
        "• Custom RFC Scanner / ABAP Dictionary OData<br/>"
        "• SAP Cloud Connector Secure Tunnel",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE082;strokeColor=#FFA000;fontColor=#3E2723;fontSize=11;fontStyle=1;align=center;",
        60, 1050, 280, 90
    )

    # ==========================================
    # CONTAINER 2: F1 FOUNDATION LAYER
    # ==========================================
    b.add_cell(
        "<b>F1: FOUNDATION LAYER (Scan, Dependency Graph &amp; Wave Planner)</b>",
        f"swimlane;whiteSpace=wrap;html=1;fillColor={c_f1_bg};strokeColor={c_f1_stroke};fontColor=#1b5e20;fontSize=14;fontStyle=1;startSize=40;rounded=1;",
        400, 110, 360, 1100
    )

    t0_node = b.add_cell(
        "<b>T0: BW Inventory Scanner</b><br/>"
        "• Connects to BW System via RFC/Dictionary<br/>"
        "• In-scope object filtering &amp; cataloging<br/>"
        "• Parses InfoObjects, ADSOs, HCPR, TRFN, Queries<br/>"
        "• Extracts raw JSON metadata payload",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#2E7D32;fontSize=11;align=left;spacingLeft=8;",
        420, 170, 320, 100
    )

    db_node = b.add_cell(
        "<b>Shared Metadata Repository</b><br/>"
        "<b>(DuckDB / SQLite : metadata_repo.db)</b><br/>"
        "• <code>objects</code> (tech_name, type, complexity, path)<br/>"
        "• <code>dependencies</code> (source_obj, target_obj, type)<br/>"
        "• <code>transformations</code> (rules, AST routines)<br/>"
        "• <code>wave_schedule</code> (wave_id, sequence)",
        "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#CFD8DC;strokeColor=#37474F;fontColor=#263238;fontSize=11;align=center;",
        430, 310, 300, 120
    )

    t1_node = b.add_cell(
        "<b>T1: Graph Analysis &amp; Wave Planner</b><br/>"
        "• NetworkX Directed Graph (DiGraph)<br/>"
        "• Cyclic dependency detection &amp; resolution<br/>"
        "• Tarjan's SCC &amp; cycle-break heuristic<br/>"
        "• Topological generations -&gt; Migration Waves (W1, W2..)",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#2E7D32;fontSize=11;align=left;spacingLeft=8;",
        420, 480, 320, 110
    )

    t2_node = b.add_cell(
        "<b>T2: Automated Scoring &amp; Classifier</b><br/>"
        "• 1 to 5 Complexity Scorer based on heuristics:<br/>"
        "  - Compounding, Hierarchies, ABAP routines<br/>"
        "• Categorizes objects into 7 Target Paths:<br/>"
        "  [P1:SrcSys, P2:IOBJ, P3:TRFN, P4:ADSO, P5:HCPR, P6:BEx, P7:Auth/PC]",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#2E7D32;fontSize=11;align=left;spacingLeft=8;",
        420, 630, 320, 120
    )

    t3_node = b.add_cell(
        "<b>T3: Traffic Controller &amp; Handover Engine</b><br/>"
        "• Merges T1 Wave Topology + T2 Complexity Scores<br/>"
        "• Decomposes large systems into executable Wave Batches<br/>"
        "• Manages prerequisite readiness &amp; locking<br/>"
        "• Dispatches objects to F2 Generator Tools",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#C8E6C9;strokeColor=#2E7D32;fontColor=#1B5E20;fontSize=11;fontStyle=1;align=left;spacingLeft=8;",
        420, 800, 320, 110
    )

    f1_status = b.add_cell(
        "<b>F1 Output &amp; State Gate:</b><br/>"
        "✔ Wave Execution Matrix Prepared<br/>"
        "✔ Dependency Graph Fully Resolved<br/>"
        "✔ Objects Tagged &amp; Staged in DuckDB",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#A5D6A7;strokeColor=#1B5E20;fontColor=#004D40;fontSize=11;align=center;",
        420, 960, 320, 80
    )

    # ==========================================
    # CONTAINER 3: F2 GENERATOR & TRANSLATOR LAYER
    # ==========================================
    b.add_cell(
        "<b>F2: GENERATOR &amp; TRANSLATOR LAYER (CSN Synthesis &amp; Code Transpilation)</b>",
        f"swimlane;whiteSpace=wrap;html=1;fillColor={c_f2_bg};strokeColor={c_f2_stroke};fontColor=#0d47a1;fontSize=14;fontStyle=1;startSize=40;rounded=1;",
        800, 110, 400, 1100
    )

    t4_node = b.add_cell(
        "<b>T4: Source System Converter (Path 1)</b><br/>"
        "• Maps BW Source Systems -&gt; DSP Space Connections<br/>"
        "• S/4HANA, ECC, ODP, ABAP, Ad-hoc File Connections<br/>"
        "• Output: Connection Payload &amp; Remote Table CSN",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1565C0;fontSize=11;align=left;spacingLeft=8;",
        820, 170, 360, 90
    )

    t5_node = b.add_cell(
        "<b>T5: InfoObjects Migrator (Path 2)</b><br/>"
        "• Characteristics -&gt; Local Tables &amp; Dimensions<br/>"
        "• Attributes (/BI0/P*) -&gt; CDS Associations (1:1 / N:1)<br/>"
        "• Texts (/BI0/T*) -&gt; Language-Dependent Text Entities<br/>"
        "• SIDs / Surrogates -&gt; Natural / Surrogate Key Mapping<br/>"
        "• Compounding Keys -&gt; Composite Primary Keys",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1565C0;fontSize=11;align=left;spacingLeft=8;",
        820, 280, 360, 130
    )

    t6_node = b.add_cell(
        "<b>T6: SQL &amp; ABAP Transpiler (Path 3)</b><br/>"
        "• Transpiles BW Transformation Rules -&gt; Datasphere SQL Views<br/>"
        "• Direct &amp; Constant Mappings -&gt; Projected Select Columns<br/>"
        "• Formula Expressions -&gt; SQL CASE WHEN / String functions<br/>"
        "• ABAP Routines (Start/End/Field):<br/>"
        "  - AST Regex Transpiler (e.g., DELETE WHERE -&gt; WHERE NOT)<br/>"
        "  - Flags Complex User Exits for Manual Review",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1565C0;fontSize=11;align=left;spacingLeft=8;",
        820, 430, 360, 140
    )

    t7_node = b.add_cell(
        "<b>T7: ADSO Table Converter (Path 4)</b><br/>"
        "• Generates Local Tables &amp; Fact Views from ADSO Keys &amp; Data<br/>"
        "• Inbound (/BIC/A*1) -&gt; Staging Local Table<br/>"
        "• Active (/BIC/A*2) -&gt; Core Fact Entity (#FACT category)<br/>"
        "• Change Log (/BIC/A*3) -&gt; History Audit View (Delta recordmode)<br/>"
        "• Converts Data Types (DEC, CURR, DATS, TIMS -&gt; cds.*)",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1565C0;fontSize=11;align=left;spacingLeft=8;",
        820, 590, 360, 130
    )

    t8_node = b.add_cell(
        "<b>T8: CompositeProvider Converter (Path 5)</b><br/>"
        "• Maps HCPR Joins &amp; Unions -&gt; DSP Graphical/SQL Views<br/>"
        "• Assembles Fact ADSO + Dimension InfoObjects<br/>"
        "• Preserves join conditions &amp; constant mappings<br/>"
        "• Output: Semantic View CSN Definitions",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1565C0;fontSize=11;align=left;spacingLeft=8;",
        820, 740, 360, 110
    )

    t9_node = b.add_cell(
        "<b>T9: BEx Query Converter (Path 6)</b><br/>"
        "• Translates BEx Queries -&gt; DSP Analytic Models<br/>"
        "• Maps RKF/CKF -&gt; Calculated &amp; Restricted Measures<br/>"
        "• Converts Query Variables -&gt; Analytic Model Parameters<br/>"
        "• Generates Business Consumption Perspectives for SAC",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1565C0;fontSize=11;align=left;spacingLeft=8;",
        820, 870, 360, 120
    )

    csn_bundle = b.add_cell(
        "<b>Compiled CSN Artifact Bundle (JSON)</b><br/>"
        "• <code>path2_infoobjects_csn.json</code><br/>"
        "• <code>path3_transformations_csn.json</code><br/>"
        "• <code>path4_adsos_csn.json</code><br/>"
        "• Validated against SAP CSN v1.0 Spec",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#BBDEFB;strokeColor=#0D47A1;fontColor=#0D47A1;fontSize=11;fontStyle=1;align=center;",
        820, 1010, 360, 80
    )

    # ==========================================
    # CONTAINER 4: F3 CROSS-CUTTING & QUALITY LAYER
    # ==========================================
    b.add_cell(
        "<b>F3: CROSS-CUTTING TOOLS &amp; GOVERNANCE</b>",
        f"swimlane;whiteSpace=wrap;html=1;fillColor={c_f3_bg};strokeColor={c_f3_stroke};fontColor=#e65100;fontSize=14;fontStyle=1;startSize=40;rounded=1;",
        1240, 110, 340, 1100
    )

    t10_node = b.add_cell(
        "<b>T10: Process Chain &amp; Security Converter</b><br/>"
        "• Process Chains (RSPC) -&gt; DSP Task Chains<br/>"
        "  - Maps DTP/Activation sequences to Task Nodes<br/>"
        "• Analysis Authorizations (RSECAUTH) -&gt;<br/>"
        "  Datasphere Data Access Controls (DAC)<br/>"
        "  - Maps authorization criteria to row-level filters",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#F57F17;fontSize=11;align=left;spacingLeft=8;",
        1260, 170, 300, 140
    )

    t11_node = b.add_cell(
        "<b>T11: Data Quality &amp; Reconciliation Engine</b><br/>"
        "• Source-to-Target Row Count Verification<br/>"
        "• SHA-256 Checksum hashing on key business metrics<br/>"
        "• Tolerance threshold evaluation (e.g. 0.01% drift)<br/>"
        "• Auto-logs reconciliation report to <code>reconciliation_results</code>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#F57F17;fontSize=11;align=left;spacingLeft=8;",
        1260, 340, 300, 130
    )

    t12_node = b.add_cell(
        "<b>T12: Web Orchestration Dashboard</b><br/>"
        "<b>(Streamlit Control Center: app.py)</b><br/>"
        "• Real-time Wave Execution Progress<br/>"
        "• Object Complexity &amp; Path KPI Visualizer<br/>"
        "• Interactive Dependency Graph (DOT/Graphviz)<br/>"
        "• Live CSN Code Generator &amp; SQL Diff Viewer<br/>"
        "• Deployment Trigger to SAP Datasphere",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF9C4;strokeColor=#F57F17;fontColor=#F57F17;fontSize=11;fontStyle=1;align=left;spacingLeft=8;",
        1260, 500, 300, 150
    )

    dsp_deployer = b.add_cell(
        "<b>Deployment &amp; Provisioning Agent</b><br/>"
        "• Executes @sap/datasphere-cli commands<br/>"
        "• Calls Datasphere REST Ingestion APIs<br/>"
        "• Triggers DP Agent / Cloud Connector Flows<br/>"
        "• Monitors async deployment status",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE082;strokeColor=#FFA000;fontColor=#3E2723;fontSize=11;fontStyle=1;align=center;",
        1260, 710, 300, 110
    )

    audit_node = b.add_cell(
        "<b>Audit &amp; Cutover Log</b><br/>"
        "• Tracks artifact deployment timestamps<br/>"
        "• Captures manual review warnings<br/>"
        "• Maintains full migration traceability",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#F57F17;fontSize=11;align=left;spacingLeft=8;",
        1260, 880, 300, 80
    )

    # ==========================================
    # CONTAINER 5: TARGET SAP DATASPHERE SYSTEM
    # ==========================================
    b.add_cell(
        "<b>TARGET SYSTEM: SAP DATASPHERE</b><br/>(Business Data Cloud, Semantics &amp; Consumption Layer)",
        f"swimlane;whiteSpace=wrap;html=1;fillColor={c_dsp_bg};strokeColor={c_dsp_stroke};fontColor=#311b92;fontSize=14;fontStyle=1;startSize=40;rounded=1;",
        1620, 110, 300, 1100
    )

    dsp_space = b.add_cell(
        "<b>Target Space (e.g. DEV_SPACE_01)</b><br/>"
        "• Space Memory &amp; Storage Quota<br/>"
        "• User Access &amp; Role Assignments<br/>"
        "• Space-level Schema Management",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#512DA8;fontSize=11;align=left;spacingLeft=8;",
        1640, 170, 260, 90
    )

    dsp_conn = b.add_cell(
        "<b>Space Connections</b><br/>"
        "• Live HANA / S4 / Cloud Connections<br/>"
        "• Data Provisioning Agent Tunnel<br/>"
        "• Remote Tables &amp; Replication Flows",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#512DA8;fontSize=11;align=left;spacingLeft=8;",
        1640, 280, 260, 90
    )

    dsp_dim = b.add_cell(
        "<b>Local Tables &amp; Dimensions</b><br/>"
        "• Master Data Dimension Entities<br/>"
        "• Texts Views with Language Key<br/>"
        "• Semantic Associations (E-R links)",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#512DA8;fontSize=11;align=left;spacingLeft=8;",
        1640, 390, 260, 100
    )

    dsp_fact = b.add_cell(
        "<b>Fact Views &amp; Staging Tables</b><br/>"
        "• Inbound / Active Fact Tables<br/>"
        "• SQL Transformation Views<br/>"
        "• Delta replication flows",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#512DA8;fontSize=11;align=left;spacingLeft=8;",
        1640, 510, 260, 90
    )

    dsp_rel = b.add_cell(
        "<b>Analytical &amp; Relational Views</b><br/>"
        "• Multi-table Star Schema joins<br/>"
        "• Calculated columns &amp; currency conversion<br/>"
        "• Exposed for Consumption",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#512DA8;fontSize=11;align=left;spacingLeft=8;",
        1640, 620, 260, 90
    )

    dsp_am = b.add_cell(
        "<b>Analytic Models &amp; Perspectives</b><br/>"
        "• Rich multidimensional models<br/>"
        "• Variables, restricted/calculated measures<br/>"
        "• Native consumption by SAP SAC &amp; PowerBI",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#512DA8;fontSize=11;align=left;spacingLeft=8;",
        1640, 730, 260, 100
    )

    dsp_tc_dac = b.add_cell(
        "<b>Task Chains &amp; Security (DAC)</b><br/>"
        "• Automated Scheduled Task Chains<br/>"
        "• Data Access Controls (Row-Level Security)<br/>"
        "• User-specific data filtering",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#512DA8;fontSize=11;align=left;spacingLeft=8;",
        1640, 850, 260, 90
    )

    dsp_apis = b.add_cell(
        "<b>Target Ingestion APIs</b><br/>"
        "• <code>POST /api/v1/spaces/{s}/definitions</code><br/>"
        "• <code>POST /api/v1/spaces/{s}/taskchains</code><br/>"
        "• OData v4 Schema Upload<br/>"
        "• CLI: <code>datasphere objects import</code>",
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#D1C4E9;strokeColor=#512DA8;fontColor=#311B92;fontSize=11;fontStyle=1;align=center;",
        1640, 960, 260, 90
    )

    # ==========================================
    # EDGES & CONNECTOR FLOWS (End-to-End Lineage)
    # ==========================================
    e_style_solid = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;"
    e_style_dashed = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;dashed=1;"
    e_style_bold = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=3;"

    # BW Source -> T0
    b.add_cell("Metadata Pull (RFC/OData)", f"{e_style_bold}strokeColor=#C2185B;", 0, 0, 0, 0, is_vertex=False, source=bw_api_node, target=t0_node)
    b.add_cell("Dictionary Read", f"{e_style_solid}strokeColor=#C2185B;", 0, 0, 0, 0, is_vertex=False, source=bw_io, target=bw_api_node)
    b.add_cell("Table Scan", f"{e_style_solid}strokeColor=#C2185B;", 0, 0, 0, 0, is_vertex=False, source=bw_adso, target=bw_api_node)
    b.add_cell("Rules & Routines", f"{e_style_solid}strokeColor=#C2185B;", 0, 0, 0, 0, is_vertex=False, source=bw_trfn, target=bw_api_node)

    # T0 -> DuckDB
    b.add_cell("Ingest Raw Metadata", f"{e_style_bold}strokeColor=#2E7D32;", 0, 0, 0, 0, is_vertex=False, source=t0_node, target=db_node)

    # DuckDB <-> T1 & T2
    b.add_cell("Read Dependencies", f"{e_style_solid}strokeColor=#2E7D32;", 0, 0, 0, 0, is_vertex=False, source=db_node, target=t1_node)
    b.add_cell("Read Object Specs", f"{e_style_solid}strokeColor=#2E7D32;", 0, 0, 0, 0, is_vertex=False, source=db_node, target=t2_node)
    b.add_cell("Store Path & Scores", f"{e_style_dashed}strokeColor=#2E7D32;", 0, 0, 0, 0, is_vertex=False, source=t2_node, target=db_node)

    # T1 & T2 -> T3
    b.add_cell("Topological Waves", f"{e_style_solid}strokeColor=#2E7D32;", 0, 0, 0, 0, is_vertex=False, source=t1_node, target=t3_node)
    b.add_cell("Complexity Ratings", f"{e_style_solid}strokeColor=#2E7D32;", 0, 0, 0, 0, is_vertex=False, source=t2_node, target=t3_node)

    # T3 Handover to F2 Generator Tools
    b.add_cell("Handover Path 1", f"{e_style_solid}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t3_node, target=t4_node)
    b.add_cell("Handover Path 2", f"{e_style_bold}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t3_node, target=t5_node)
    b.add_cell("Handover Path 3", f"{e_style_bold}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t3_node, target=t6_node)
    b.add_cell("Handover Path 4", f"{e_style_bold}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t3_node, target=t7_node)
    b.add_cell("Handover Path 5", f"{e_style_solid}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t3_node, target=t8_node)
    b.add_cell("Handover Path 6", f"{e_style_solid}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t3_node, target=t9_node)

    # F2 Tools -> CSN Bundle
    b.add_cell("", f"{e_style_solid}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t5_node, target=csn_bundle)
    b.add_cell("", f"{e_style_solid}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t6_node, target=csn_bundle)
    b.add_cell("", f"{e_style_solid}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t7_node, target=csn_bundle)
    b.add_cell("", f"{e_style_solid}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t8_node, target=csn_bundle)
    b.add_cell("", f"{e_style_solid}strokeColor=#1565C0;", 0, 0, 0, 0, is_vertex=False, source=t9_node, target=csn_bundle)

    # T3 / Waves -> F3 Tools
    b.add_cell("Path 7 Chains & Auth", f"{e_style_solid}strokeColor=#F57F17;", 0, 0, 0, 0, is_vertex=False, source=t3_node, target=t10_node)
    b.add_cell("Control & Metrics", f"{e_style_dashed}strokeColor=#F57F17;", 0, 0, 0, 0, is_vertex=False, source=db_node, target=t12_node)

    # CSN Bundle & Tools -> Deployment Agent
    b.add_cell("CSN JSON Models", f"{e_style_bold}strokeColor=#0D47A1;", 0, 0, 0, 0, is_vertex=False, source=csn_bundle, target=dsp_deployer)
    b.add_cell("Trigger Deploy", f"{e_style_solid}strokeColor=#F57F17;", 0, 0, 0, 0, is_vertex=False, source=t12_node, target=dsp_deployer)
    b.add_cell("Task Chains & DAC", f"{e_style_solid}strokeColor=#F57F17;", 0, 0, 0, 0, is_vertex=False, source=t10_node, target=dsp_deployer)

    # Deployer -> SAP Datasphere
    b.add_cell("Import CSN & Definitions", f"{e_style_bold}strokeColor=#512DA8;", 0, 0, 0, 0, is_vertex=False, source=dsp_deployer, target=dsp_apis)
    b.add_cell("", f"{e_style_solid}strokeColor=#512DA8;", 0, 0, 0, 0, is_vertex=False, source=dsp_apis, target=dsp_dim)
    b.add_cell("", f"{e_style_solid}strokeColor=#512DA8;", 0, 0, 0, 0, is_vertex=False, source=dsp_apis, target=dsp_fact)
    b.add_cell("", f"{e_style_solid}strokeColor=#512DA8;", 0, 0, 0, 0, is_vertex=False, source=dsp_apis, target=dsp_rel)
    b.add_cell("", f"{e_style_solid}strokeColor=#512DA8;", 0, 0, 0, 0, is_vertex=False, source=dsp_apis, target=dsp_am)
    b.add_cell("", f"{e_style_solid}strokeColor=#512DA8;", 0, 0, 0, 0, is_vertex=False, source=dsp_apis, target=dsp_tc_dac)

    # T11 Reconciliation Verification (Source vs DSP)
    b.add_cell("Source Counts (BW)", f"{e_style_dashed}strokeColor=#C2185B;", 0, 0, 0, 0, is_vertex=False, source=bw_api_node, target=t11_node)
    b.add_cell("Target Counts (DSP)", f"{e_style_dashed}strokeColor=#512DA8;", 0, 0, 0, 0, is_vertex=False, source=dsp_apis, target=t11_node)
    b.add_cell("Reconciliation Status", f"{e_style_solid}strokeColor=#F57F17;", 0, 0, 0, 0, is_vertex=False, source=t11_node, target=t12_node)

    return b.build_xml()

if __name__ == "__main__":
    xml_content = create_diagram()
    output_path = r"C:\Users\Varad\.gemini\antigravity-cli\brain\fe73ba1d-65f7-4038-9e93-de509c9dc3e1\BW_Morph_Architecture_Flow.drawio"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"Successfully generated {output_path} (length: {len(xml_content)} bytes)")
