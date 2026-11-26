"""
Generates:
1. BW_Morph_Architecture_Horizontal.drawio
2. BW_Morph_Architecture_Horizontal.svg
3. BW_Morph_Architecture_Horizontal.png (via headless Chrome 2x scale)

Clean code folder for easy disposal if requested by user.
"""

import html
import os
import subprocess

def generate_svg():
    # 1920x1080 SVG with 5 Horizontal Swimlanes, right Notes panel & Legend
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" style="background:#FFFFFF; font-family:'Segoe UI', Inter, -apple-system, BlinkMacSystemFont, sans-serif;">
  <defs>
    <!-- Markers for Arrows -->
    <marker id="arrow-solid" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2563EB"/>
    </marker>
    <marker id="arrow-solid-teal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0D9488"/>
    </marker>
    <marker id="arrow-dashed" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#EA580C"/>
    </marker>
    <marker id="arrow-control" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#6B7280"/>
    </marker>
  </defs>

  <!-- ================= TOP HEADER ================= -->
  <rect x="40" y="20" width="1840" height="55" rx="8" fill="#1E293B"/>
  <text x="70" y="55" font-size="22" font-weight="700" fill="#FFFFFF">BW Morph: End-to-End Migration Pipeline (T0 to T12)</text>
  <text x="1800" y="54" font-size="13" font-weight="500" fill="#94A3B8" text-anchor="end">Enterprise Solution Architecture | SAP BW/4HANA → SAP Datasphere</text>

  <!-- ================= 5 HORIZONTAL SWIMLANES ================= -->

  <!-- LANE 1: SOURCE (SAP BW/4HANA) -->
  <g id="lane-source">
    <rect x="40" y="90" width="1380" height="155" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
    <rect x="40" y="90" width="220" height="30" rx="8" fill="#E2E8F0"/>
    <text x="55" y="110" font-size="13" font-weight="700" fill="#334155">1. Source: SAP BW/4HANA</text>

    <!-- 4 Sub-boxes -->
    <!-- Box 1 -->
    <rect x="65" y="130" width="310" height="48" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1"/>
    <text x="80" y="150" font-size="13" font-weight="700" fill="#1E293B">DataSources</text>
    <text x="80" y="167" font-size="11" fill="#64748B">ROOSOURCE, ODP, delta queues</text>

    <!-- Box 2 -->
    <rect x="395" y="130" width="310" height="48" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1"/>
    <text x="410" y="150" font-size="13" font-weight="700" fill="#1E293B">InfoObjects</text>
    <text x="410" y="167" font-size="11" fill="#64748B">Attributes, texts, surrogate SIDs</text>

    <!-- Box 3 -->
    <rect x="725" y="130" width="310" height="48" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1"/>
    <text x="740" y="150" font-size="13" font-weight="700" fill="#1E293B">ADSO &amp; HCPR</text>
    <text x="740" y="167" font-size="11" fill="#64748B">Tables, active facts, join models</text>

    <!-- Box 4 -->
    <rect x="1055" y="130" width="345" height="48" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1"/>
    <text x="1070" y="150" font-size="13" font-weight="700" fill="#1E293B">Logic Layer</text>
    <text x="1070" y="167" font-size="11" fill="#64748B">Transformations, BEx, process chains</text>

    <!-- Extraction Bar -->
    <rect x="65" y="190" width="1335" height="42" rx="6" fill="#F1F5F9" stroke="#64748B" stroke-width="1.2"/>
    <text x="732" y="216" font-size="12" font-weight="700" fill="#334155" text-anchor="middle">Extraction Interface: RFC (pyrfc) | BAPIs | SAP Cloud Connector | OData DDL</text>
  </g>

  <!-- Solid Arrow: Source -> F1 -->
  <line x1="732" y1="232" x2="732" y2="260" stroke="#2563EB" stroke-width="2.5" marker-end="url(#arrow-solid)"/>
  <rect x="670" y="238" width="124" height="18" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
  <text x="732" y="251" font-size="10.5" font-weight="600" fill="#1D4ED8" text-anchor="middle">Raw metadata feed</text>

  <!-- LANE 2: F1 FOUNDATION (TEAL) -->
  <g id="lane-f1">
    <rect x="40" y="260" width="1380" height="195" rx="8" fill="#F0FDFA" stroke="#0D9488" stroke-width="1.5"/>
    <rect x="40" y="260" width="280" height="30" rx="8" fill="#CCFBF1"/>
    <text x="55" y="280" font-size="13" font-weight="700" fill="#0F766E">2. F1 Foundation: scan, graph, plan</text>

    <!-- 4 T-boxes in row -->
    <!-- T0 -->
    <rect x="65" y="298" width="310" height="48" rx="6" fill="#FFFFFF" stroke="#0D9488" stroke-width="1.2"/>
    <text x="80" y="318" font-size="13" font-weight="700" fill="#0F766E">T0: BW Inventory Scanner</text>
    <text x="80" y="335" font-size="11" fill="#115E59">RFC extraction to JSON dictionary</text>

    <!-- T1 -->
    <rect x="395" y="298" width="310" height="48" rx="6" fill="#FFFFFF" stroke="#0D9488" stroke-width="1.2"/>
    <text x="410" y="318" font-size="13" font-weight="700" fill="#0F766E">T1: Wave Planner</text>
    <text x="410" y="335" font-size="11" fill="#115E59">NetworkX DAG, SCC, topological waves</text>

    <!-- T2 -->
    <rect x="725" y="298" width="310" height="48" rx="6" fill="#FFFFFF" stroke="#0D9488" stroke-width="1.2"/>
    <text x="740" y="318" font-size="13" font-weight="700" fill="#0F766E">T2: Classifier &amp; Scorer</text>
    <text x="740" y="335" font-size="11" fill="#115E59">Complexity score 1–5, Paths 1 to 7</text>

    <!-- T3 -->
    <rect x="1055" y="298" width="345" height="48" rx="6" fill="#FFFFFF" stroke="#0D9488" stroke-width="1.2"/>
    <text x="1070" y="318" font-size="13" font-weight="700" fill="#0F766E">T3: Traffic Controller</text>
    <text x="1070" y="335" font-size="11" fill="#115E59">Batches, locking &amp; wave handover</text>

    <!-- Connectors between T0 -> T1 -> T2 -> T3 -->
    <line x1="375" y1="322" x2="395" y2="322" stroke="#0D9488" stroke-width="1.5" marker-end="url(#arrow-solid-teal)"/>
    <line x1="705" y1="322" x2="725" y2="322" stroke="#0D9488" stroke-width="1.5" marker-end="url(#arrow-solid-teal)"/>
    <line x1="1035" y1="322" x2="1055" y2="322" stroke="#0D9488" stroke-width="1.5" marker-end="url(#arrow-solid-teal)"/>

    <!-- Wide Cylinder Bar: Shared metadata repo -->
    <rect x="65" y="358" width="1335" height="44" rx="6" fill="#CCFBF1" stroke="#0F766E" stroke-width="1.5"/>
    <text x="732" y="377" font-size="12" font-weight="700" fill="#0F766E" text-anchor="middle">Shared Metadata Repository (DuckDB / SQLite)</text>
    <text x="732" y="393" font-size="11" fill="#115E59" text-anchor="middle">Persists: objects | dependencies | transformations | wave_schedule | reconciliation_results</text>

    <!-- Dashed links from T0-T3 to DuckDB -->
    <line x1="220" y1="346" x2="220" y2="358" stroke="#0F766E" stroke-width="1" stroke-dasharray="3,3"/>
    <line x1="550" y1="346" x2="550" y2="358" stroke="#0F766E" stroke-width="1" stroke-dasharray="3,3"/>
    <line x1="880" y1="346" x2="880" y2="358" stroke="#0F766E" stroke-width="1" stroke-dasharray="3,3"/>
    <line x1="1225" y1="346" x2="1225" y2="358" stroke="#0F766E" stroke-width="1" stroke-dasharray="3,3"/>

    <!-- Gate Badge at bottom -->
    <rect x="532" y="415" width="400" height="26" rx="13" fill="#0D9488"/>
    <text x="732" y="432" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">✔ GATE: Waves ready | Graph resolved | Objects staged</text>
  </g>

  <!-- Solid Arrow: F1 (T3) -> F2 -->
  <line x1="1225" y1="346" x2="1225" y2="470" stroke="#2563EB" stroke-width="2.5" marker-end="url(#arrow-solid)"/>
  <rect x="1140" y="445" width="170" height="18" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
  <text x="1225" y="458" font-size="10.5" font-weight="600" fill="#1D4ED8" text-anchor="middle">Wave batches + path tags</text>

  <!-- LANE 3: F2 GENERATORS (PURPLE) -->
  <g id="lane-f2">
    <rect x="40" y="470" width="1380" height="205" rx="8" fill="#FAF5FF" stroke="#805AD5" stroke-width="1.5"/>
    <rect x="40" y="470" width="370" height="30" rx="8" fill="#E9D8FD"/>
    <text x="55" y="490" font-size="13" font-weight="700" fill="#553C9E">3. F2 Generators: CSN synthesis &amp; transpilation</text>

    <!-- 3x2 Grid -->
    <!-- Row 1 -->
    <rect x="65" y="508" width="430" height="44" rx="6" fill="#FFFFFF" stroke="#805AD5" stroke-width="1.2"/>
    <text x="80" y="526" font-size="12.5" font-weight="700" fill="#44337A">T4: Source Systems (Path 1)</text>
    <text x="80" y="542" font-size="11" fill="#6B46C1">DSP Space connections &amp; remote stubs</text>

    <rect x="515" y="508" width="430" height="44" rx="6" fill="#FFFFFF" stroke="#805AD5" stroke-width="1.2"/>
    <text x="530" y="526" font-size="12.5" font-weight="700" fill="#44337A">T5: InfoObjects (Path 2)</text>
    <text x="530" y="542" font-size="11" fill="#6B46C1">Dimensions, texts, surrogate SIDs, CSN</text>

    <rect x="965" y="508" width="435" height="44" rx="6" fill="#FFFFFF" stroke="#805AD5" stroke-width="1.2"/>
    <text x="980" y="526" font-size="12.5" font-weight="700" fill="#44337A">T6: Transformations (Path 3)</text>
    <text x="980" y="542" font-size="11" fill="#6B46C1">SQL Views, ABAP AST regex transpiler</text>

    <!-- Row 2 -->
    <rect x="65" y="562" width="430" height="44" rx="6" fill="#FFFFFF" stroke="#805AD5" stroke-width="1.2"/>
    <text x="80" y="580" font-size="12.5" font-weight="700" fill="#44337A">T7: ADSO Converter (Path 4)</text>
    <text x="80" y="596" font-size="11" fill="#6B46C1">Inbound, Active facts &amp; Change log CSN</text>

    <rect x="515" y="562" width="430" height="44" rx="6" fill="#FFFFFF" stroke="#805AD5" stroke-width="1.2"/>
    <text x="530" y="580" font-size="12.5" font-weight="700" fill="#44337A">T8: CompositeProvider (Path 5)</text>
    <text x="530" y="596" font-size="11" fill="#6B46C1">Analytical joins, unions, star schema CSN</text>

    <rect x="965" y="562" width="435" height="44" rx="6" fill="#FFFFFF" stroke="#805AD5" stroke-width="1.2"/>
    <text x="980" y="580" font-size="12.5" font-weight="700" fill="#44337A">T9: BEx Queries (Path 6)</text>
    <text x="980" y="596" font-size="11" fill="#6B46C1">Analytic models, RKF/CKF, variables</text>

    <!-- Wide Bar: Compiled CSN Bundle -->
    <rect x="65" y="618" width="1335" height="42" rx="6" fill="#E9D8FD" stroke="#6B46C1" stroke-width="1.5"/>
    <text x="732" y="636" font-size="12" font-weight="700" fill="#44337A" text-anchor="middle">Compiled CSN Artifact Bundle (JSON Format)</text>
    <text x="732" y="652" font-size="11" fill="#553C9E" text-anchor="middle">path2_infoobjects_csn.json | path3_transformations_csn.json | path4_adsos_csn.json (Validated vs CSN v1.0 Spec)</text>
  </g>

  <!-- Solid Arrow: F2 -> F3 -->
  <line x1="1245" y1="660" x2="1245" y2="690" stroke="#2563EB" stroke-width="2.5" marker-end="url(#arrow-solid)"/>
  <rect x="1190" y="668" width="110" height="18" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
  <text x="1245" y="681" font-size="10.5" font-weight="600" fill="#1D4ED8" text-anchor="middle">CSN artifacts</text>

  <!-- LANE 4: F3 GOVERNANCE (CORAL) -->
  <g id="lane-f3">
    <rect x="40" y="690" width="1380" height="150" rx="8" fill="#FFF7ED" stroke="#EA580C" stroke-width="1.5"/>
    <rect x="40" y="690" width="310" height="30" rx="8" fill="#FFEDD5"/>
    <text x="55" y="710" font-size="13" font-weight="700" fill="#C2410C">4. F3 Governance &amp; deployment</text>

    <!-- 4 boxes side-by-side -->
    <!-- T10 -->
    <rect x="65" y="728" width="310" height="48" rx="6" fill="#FFFFFF" stroke="#EA580C" stroke-width="1.2"/>
    <text x="80" y="748" font-size="13" font-weight="700" fill="#9A3412">T10: Security &amp; Chains (Path 7)</text>
    <text x="80" y="765" font-size="11" fill="#C2410C">Task chains &amp; DAC row-level policies</text>

    <!-- T11 -->
    <rect x="395" y="728" width="310" height="48" rx="6" fill="#FFFFFF" stroke="#EA580C" stroke-width="1.2"/>
    <text x="410" y="748" font-size="13" font-weight="700" fill="#9A3412">T11: Reconciliation Engine</text>
    <text x="410" y="765" font-size="11" fill="#C2410C">Counts, SHA-256 hash, tolerance check</text>

    <!-- T12 Dashboard -->
    <rect x="725" y="728" width="310" height="48" rx="6" fill="#FFFFFF" stroke="#EA580C" stroke-width="1.2"/>
    <text x="740" y="748" font-size="13" font-weight="700" fill="#9A3412">T12: Streamlit Dashboard</text>
    <text x="740" y="765" font-size="11" fill="#C2410C">KPI control plane, wave graph, SQL diff</text>

    <!-- Deploy Agent -->
    <rect x="1055" y="728" width="345" height="48" rx="6" fill="#FFFFFF" stroke="#EA580C" stroke-width="1.2"/>
    <text x="1070" y="748" font-size="13" font-weight="700" fill="#9A3412">Deployment Agent</text>
    <text x="1070" y="765" font-size="11" fill="#C2410C">@sap/datasphere-cli &amp; REST Ingestion</text>

    <!-- Audit Log Bar -->
    <rect x="65" y="788" width="1335" height="38" rx="6" fill="#FFEDD5" stroke="#C2410C" stroke-width="1"/>
    <text x="732" y="812" font-size="11.5" font-weight="600" fill="#9A3412" text-anchor="middle">Audit and Cutover Log: Automated artifact deployment timestamps, warning logs &amp; cutover tracking</text>
  </g>

  <!-- Solid Arrow: Deploy Agent -> Target -->
  <line x1="1225" y1="776" x2="1225" y2="855" stroke="#2563EB" stroke-width="2.5" marker-end="url(#arrow-solid)"/>
  <rect x="1165" y="810" width="120" height="18" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
  <text x="1225" y="823" font-size="10.5" font-weight="600" fill="#1D4ED8" text-anchor="middle">Import definitions</text>

  <!-- LANE 5: TARGET (SAP DATASPHERE) -->
  <g id="lane-target">
    <rect x="40" y="855" width="1380" height="175" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
    <rect x="40" y="855" width="220" height="30" rx="8" fill="#E2E8F0"/>
    <text x="55" y="875" font-size="13" font-weight="700" fill="#334155">5. Target: SAP Datasphere</text>

    <!-- 5 boxes side-by-side -->
    <rect x="65" y="895" width="245" height="48" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1"/>
    <text x="80" y="915" font-size="13" font-weight="700" fill="#1E293B">Space</text>
    <text x="80" y="932" font-size="11" fill="#64748B">Target space quota, users &amp; roles</text>

    <rect x="330" y="895" width="245" height="48" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1"/>
    <text x="345" y="915" font-size="13" font-weight="700" fill="#1E293B">Local Tables</text>
    <text x="345" y="932" font-size="11" fill="#64748B">Dimensions, texts, E-R associations</text>

    <rect x="595" y="895" width="255" height="48" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1"/>
    <text x="610" y="915" font-size="13" font-weight="700" fill="#1E293B">Fact &amp; Analytic Views</text>
    <text x="610" y="932" font-size="11" fill="#64748B">SQL Views, staging &amp; fact persistence</text>

    <rect x="870" y="895" width="255" height="48" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1"/>
    <text x="885" y="915" font-size="13" font-weight="700" fill="#1E293B">Analytic Models</text>
    <text x="885" y="932" font-size="11" fill="#64748B">Consumption models for SAC / Power BI</text>

    <rect x="1145" y="895" width="255" height="48" rx="6" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1"/>
    <text x="1160" y="915" font-size="13" font-weight="700" fill="#1E293B">Task Chains &amp; DAC</text>
    <text x="1160" y="932" font-size="11" fill="#64748B">Scheduled flows + row-level security</text>

    <!-- Ingestion Bar -->
    <rect x="65" y="955" width="1335" height="42" rx="6" fill="#F1F5F9" stroke="#64748B" stroke-width="1.2"/>
    <text x="732" y="981" font-size="12" font-weight="700" fill="#334155" text-anchor="middle">Ingestion Interface: POST /api/v1/spaces/.../definitions | @sap/datasphere-cli import | DP Agent</text>
  </g>

  <!-- ================= CONTROL FLOWS & RECONCILIATION ================= -->

  <!-- T11 Reconciliation Loop (Dashed Orange) -->
  <!-- Left Side: T11 up to Source Lane -->
  <path d="M 430 728 L 430 154 L 375 154" fill="none" stroke="#EA580C" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrow-dashed)"/>
  <!-- Left Side: T11 down to Target Lane -->
  <path d="M 470 776 L 470 919 L 575 919" fill="none" stroke="#EA580C" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrow-dashed)"/>
  <rect x="420" y="445" width="95" height="18" rx="4" fill="#FFF7ED" stroke="#FFEDD5" stroke-width="1"/>
  <text x="467" y="458" font-size="10" font-weight="700" fill="#C2410C" text-anchor="middle">Reconciliation</text>

  <!-- T12 Dashboard Control Plane (Dashed Gray) -->
  <!-- T12 -> T3 (Upward) -->
  <path d="M 880 728 L 880 346" fill="none" stroke="#6B7280" stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arrow-control)"/>
  <!-- T12 -> Deploy Agent (Rightward) -->
  <line x1="1035" y1="752" x2="1055" y2="752" stroke="#6B7280" stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arrow-control)"/>

  <!-- ================= RIGHT-SIDE NOTES PANEL ================= -->
  <g id="notes-panel">
    <rect x="1440" y="90" width="440" height="740" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
    <rect x="1440" y="90" width="440" height="38" rx="8" fill="#0F172A"/>
    <text x="1455" y="115" font-size="14" font-weight="700" fill="#FFFFFF">Architecture &amp; Migration Details</text>

    <!-- Source Notes -->
    <text x="1455" y="150" font-size="12" font-weight="700" fill="#1E293B">1. Source: SAP BW/4HANA</text>
    <text x="1455" y="168" font-size="10.5" fill="#475569">• Tables: ROOSOURCE, ODQMON, RSDIOBJ, RSDATTR</text>
    <text x="1455" y="184" font-size="10.5" fill="#475569">• Active /BIC/A*2 facts &amp; Change log /BIC/A*3 history</text>
    <text x="1455" y="200" font-size="10.5" fill="#475569">• InfoObject SIDs (/BI0/S*, /BI0/X*, /BI0/Y*) resolved to keys</text>

    <line x1="1455" y1="215" x2="1860" y2="215" stroke="#E2E8F0" stroke-width="1"/>

    <!-- F1 Notes -->
    <text x="1455" y="235" font-size="12" font-weight="700" fill="#0F766E">2. F1 Foundation Layer</text>
    <text x="1455" y="253" font-size="10.5" fill="#475569">• T0 loads metadata dictionary snapshots into DuckDB</text>
    <text x="1455" y="269" font-size="10.5" fill="#475569">• T1 uses NetworkX DiGraph + Tarjan's SCC for cycles</text>
    <text x="1455" y="285" font-size="10.5" fill="#475569">• T2 scores 1–5 (compounding, ABAP routines, hierarchy)</text>
    <text x="1455" y="301" font-size="10.5" fill="#475569">• T3 stages wave batches and manages prerequisite locks</text>

    <line x1="1455" y1="316" x2="1860" y2="316" stroke="#E2E8F0" stroke-width="1"/>

    <!-- F2 Notes -->
    <text x="1455" y="336" font-size="12" font-weight="700" fill="#553C9E">3. F2 Generators &amp; Transpilation</text>
    <text x="1455" y="354" font-size="10.5" fill="#475569">• T4 maps BW source systems to DSP Space Connections</text>
    <text x="1455" y="370" font-size="10.5" fill="#475569">• T5 converts characteristics &amp; texts to #DIMENSION CSN</text>
    <text x="1455" y="386" font-size="10.5" fill="#475569">• T6 transpiles ABAP Start/End/Field routines to SQL Views</text>
    <text x="1455" y="402" font-size="10.5" fill="#475569">• T7 maps ADSOs to #FACT &amp; staging local tables</text>
    <text x="1455" y="418" font-size="10.5" fill="#475569">• T8 translates CompositeProviders into Relational Views</text>
    <text x="1455" y="434" font-size="10.5" fill="#475569">• T9 translates BEx queries to DSP Analytic Models</text>

    <line x1="1455" y1="449" x2="1860" y2="449" stroke="#E2E8F0" stroke-width="1"/>

    <!-- F3 Notes -->
    <text x="1455" y="469" font-size="12" font-weight="700" fill="#C2410C">4. F3 Governance &amp; Controls</text>
    <text x="1455" y="487" font-size="10.5" fill="#475569">• T10 translates RSPC chains to Datasphere Task Chains</text>
    <text x="1455" y="503" font-size="10.5" fill="#475569">• T10 converts Analysis Authorizations into DAC policies</text>
    <text x="1455" y="519" font-size="10.5" fill="#475569">• T11 reconciles record counts &amp; SHA-256 metric sums</text>
    <text x="1455" y="535" font-size="10.5" fill="#475569">• T12 Streamlit dashboard acts as master control cockpit</text>

    <line x1="1455" y1="550" x2="1860" y2="550" stroke="#E2E8F0" stroke-width="1"/>

    <!-- Target Notes -->
    <text x="1455" y="570" font-size="12" font-weight="700" fill="#1E293B">5. Target: SAP Datasphere</text>
    <text x="1455" y="588" font-size="10.5" fill="#475569">• Space-level schema isolation and user role governance</text>
    <text x="1455" y="604" font-size="10.5" fill="#475569">• Core CSN v1.0 schema notation for dimensions and facts</text>
    <text x="1455" y="620" font-size="10.5" fill="#475569">• Multidimensional Analytic Models exposed for SAC &amp; Power BI</text>
    <text x="1455" y="636" font-size="10.5" fill="#475569">• Automated Delta Replication via DP Agent &amp; Cloud Connector</text>

    <line x1="1455" y1="651" x2="1860" y2="651" stroke="#E2E8F0" stroke-width="1"/>

    <!-- Cutover Notes -->
    <text x="1455" y="671" font-size="12" font-weight="700" fill="#0F172A">Cutover Guardrails</text>
    <text x="1455" y="689" font-size="10.5" fill="#475569">• Strict wave dependency locking: No Wave N+1 without Wave N</text>
    <text x="1455" y="705" font-size="10.5" fill="#475569">• 0.01% reconciliation tolerance threshold on numerical sums</text>
    <text x="1455" y="721" font-size="10.5" fill="#475569">• Fallback manual review queue for unparsed complex ABAP</text>
  </g>

  <!-- ================= RIGHT-BOTTOM LEGEND ================= -->
  <g id="legend">
    <rect x="1440" y="855" width="440" height="175" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
    <rect x="1440" y="855" width="440" height="28" rx="8" fill="#E2E8F0"/>
    <text x="1455" y="874" font-size="12" font-weight="700" fill="#334155">Legend &amp; Visual Conventions</text>

    <!-- Arrow 1: Solid Data Flow -->
    <line x1="1460" y1="900" x2="1520" y2="900" stroke="#2563EB" stroke-width="2.5" marker-end="url(#arrow-solid)"/>
    <text x="1535" y="904" font-size="11" font-weight="600" fill="#1E293B">Primary Data / Metadata Flow (Solid, 2.5px)</text>

    <!-- Arrow 2: Dashed Control -->
    <line x1="1460" y1="925" x2="1520" y2="925" stroke="#EA580C" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrow-dashed)"/>
    <text x="1535" y="929" font-size="11" font-weight="600" fill="#1E293B">Reconciliation Loop (Dashed Orange, 1.8px)</text>

    <!-- Arrow 3: Gray Control -->
    <line x1="1460" y1="950" x2="1520" y2="950" stroke="#6B7280" stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arrow-control)"/>
    <text x="1535" y="954" font-size="11" font-weight="600" fill="#1E293B">Control Plane / Dashboard Trigger (Dashed Gray)</text>

    <!-- Lane Color Swatches -->
    <rect x="1460" y="972" width="14" height="14" rx="3" fill="#F8FAFC" stroke="#94A3B8"/>
    <text x="1480" y="983" font-size="10.5" fill="#475569">Source / Target</text>

    <rect x="1575" y="972" width="14" height="14" rx="3" fill="#F0FDFA" stroke="#0D9488"/>
    <text x="1595" y="983" font-size="10.5" fill="#475569">F1 Foundation</text>

    <rect x="1685" y="972" width="14" height="14" rx="3" fill="#FAF5FF" stroke="#805AD5"/>
    <text x="1705" y="983" font-size="10.5" fill="#475569">F2 Generator</text>

    <rect x="1785" y="972" width="14" height="14" rx="3" fill="#FFF7ED" stroke="#EA580C"/>
    <text x="1805" y="983" font-size="10.5" fill="#475569">F3 Governance</text>

    <text x="1460" y="1015" font-size="10" font-style="italic" fill="#64748B">Canvas: 1920×1080 Landscape | Snap-to-Grid: 10px | Inter / Segoe UI</text>
  </g>

</svg>"""
    return svg

def generate_drawio():
    # Corresponding drawio XML for the horizontal architecture
    # Building cleanly structured mxfile
    return """<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2026-11-26T10:40:00.000Z" agent="BW-Morph-Architect" version="22.1.0" type="device">
  <diagram id="bw-morph-horizontal" name="BW Morph Horizontal Pipeline">
    <mxGraphModel dx="1920" dy="1080" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1920" pageHeight="1080" background="#FFFFFF" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Header -->
        <mxCell id="hdr" value="&lt;b&gt;BW Morph: End-to-End Migration Pipeline (T0 to T12)&lt;/b&gt;&lt;br/&gt;&lt;i&gt;Enterprise Solution Architecture | SAP BW/4HANA → SAP Datasphere&lt;/i&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#0F172A;fontColor=#FFFFFF;fontSize=18;align=left;spacingLeft=25;" vertex="1" parent="1">
          <mxGeometry x="40" y="20" width="1840" height="55" as="geometry"/>
        </mxCell>

        <!-- Lane 1: Source -->
        <mxCell id="lane1" value="&lt;b&gt;1. Source: SAP BW/4HANA&lt;/b&gt;" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontColor=#334155;fontSize=13;fontStyle=1;startSize=28;rounded=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="90" width="1380" height="155" as="geometry"/>
        </mxCell>
        <mxCell id="s1" value="&lt;b&gt;DataSources&lt;/b&gt;&lt;br/&gt;ROOSOURCE, ODP" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;fontSize=11;" vertex="1" parent="lane1">
          <mxGeometry x="25" y="40" width="310" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="s2" value="&lt;b&gt;InfoObjects&lt;/b&gt;&lt;br/&gt;Attrs, texts, SIDs" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;fontSize=11;" vertex="1" parent="lane1">
          <mxGeometry x="355" y="40" width="310" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="s3" value="&lt;b&gt;ADSO, HCPR&lt;/b&gt;&lt;br/&gt;Tables and joins" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;fontSize=11;" vertex="1" parent="lane1">
          <mxGeometry x="685" y="40" width="310" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="s4" value="&lt;b&gt;Logic Layer&lt;/b&gt;&lt;br/&gt;TRFN, BEx, chains" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;fontSize=11;" vertex="1" parent="lane1">
          <mxGeometry x="1015" y="40" width="345" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="s_bar" value="&lt;b&gt;Extraction Interface: RFC (pyrfc) | BAPIs | SAP Cloud Connector | OData DDL&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor=#64748B;fontSize=12;" vertex="1" parent="lane1">
          <mxGeometry x="25" y="100" width="1335" height="42" as="geometry"/>
        </mxCell>

        <!-- Lane 2: F1 Foundation -->
        <mxCell id="lane2" value="&lt;b&gt;2. F1 Foundation: scan, graph, plan&lt;/b&gt;" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F0FDFA;strokeColor=#0D9488;fontColor=#0F766E;fontSize=13;fontStyle=1;startSize=28;rounded=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="260" width="1380" height="195" as="geometry"/>
        </mxCell>
        <mxCell id="f1_t0" value="&lt;b&gt;T0 Scanner&lt;/b&gt;&lt;br/&gt;RFC to JSON" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0D9488;fontSize=11;" vertex="1" parent="lane2">
          <mxGeometry x="25" y="38" width="310" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="f1_t1" value="&lt;b&gt;T1 Wave Planner&lt;/b&gt;&lt;br/&gt;SCC, topo waves" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0D9488;fontSize=11;" vertex="1" parent="lane2">
          <mxGeometry x="355" y="38" width="310" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="f1_t2" value="&lt;b&gt;T2 Classifier&lt;/b&gt;&lt;br/&gt;Score 1–5, 7 paths" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0D9488;fontSize=11;" vertex="1" parent="lane2">
          <mxGeometry x="685" y="38" width="310" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="f1_t3" value="&lt;b&gt;T3 Controller&lt;/b&gt;&lt;br/&gt;Batches, locking" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0D9488;fontSize=11;" vertex="1" parent="lane2">
          <mxGeometry x="1015" y="38" width="345" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="f1_repo" value="&lt;b&gt;Shared Metadata Repository (DuckDB)&lt;/b&gt;&lt;br/&gt;objects, dependencies, transformations, wave_schedule" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=10;fillColor=#CCFBF1;strokeColor=#0F766E;fontSize=11;" vertex="1" parent="lane2">
          <mxGeometry x="25" y="98" width="1335" height="44" as="geometry"/>
        </mxCell>
        <mxCell id="f1_gate" value="✔ Waves ready | Graph resolved | Objects staged" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0D9488;strokeColor=#0F766E;fontColor=#FFFFFF;fontSize=11;fontStyle=1;" vertex="1" parent="lane2">
          <mxGeometry x="492" y="155" width="400" height="26" as="geometry"/>
        </mxCell>

        <!-- Lane 3: F2 Generators -->
        <mxCell id="lane3" value="&lt;b&gt;3. F2 Generators: CSN synthesis and transpilation&lt;/b&gt;" style="swimlane;whiteSpace=wrap;html=1;fillColor=#FAF5FF;strokeColor=#805AD5;fontColor=#553C9E;fontSize=13;fontStyle=1;startSize=28;rounded=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="470" width="1380" height="205" as="geometry"/>
        </mxCell>
        <mxCell id="f2_t4" value="&lt;b&gt;T4 Source Systems&lt;/b&gt;&lt;br/&gt;Path 1: connections" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#805AD5;fontSize=11;" vertex="1" parent="lane3">
          <mxGeometry x="25" y="38" width="430" height="44" as="geometry"/>
        </mxCell>
        <mxCell id="f2_t5" value="&lt;b&gt;T5 InfoObjects&lt;/b&gt;&lt;br/&gt;Path 2: dims, texts" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#805AD5;fontSize=11;" vertex="1" parent="lane3">
          <mxGeometry x="475" y="38" width="430" height="44" as="geometry"/>
        </mxCell>
        <mxCell id="f2_t6" value="&lt;b&gt;T6 Transformations&lt;/b&gt;&lt;br/&gt;Path 3: SQL + ABAP AST" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#805AD5;fontSize=11;" vertex="1" parent="lane3">
          <mxGeometry x="925" y="38" width="435" height="44" as="geometry"/>
        </mxCell>
        <mxCell id="f2_t7" value="&lt;b&gt;T7 ADSO&lt;/b&gt;&lt;br/&gt;Path 4: tables, facts" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#805AD5;fontSize=11;" vertex="1" parent="lane3">
          <mxGeometry x="25" y="92" width="430" height="44" as="geometry"/>
        </mxCell>
        <mxCell id="f2_t8" value="&lt;b&gt;T8 CompositeProvider&lt;/b&gt;&lt;br/&gt;Path 5: semantic views" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#805AD5;fontSize=11;" vertex="1" parent="lane3">
          <mxGeometry x="475" y="92" width="430" height="44" as="geometry"/>
        </mxCell>
        <mxCell id="f2_t9" value="&lt;b&gt;T9 BEx Queries&lt;/b&gt;&lt;br/&gt;Path 6: analytic models" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#805AD5;fontSize=11;" vertex="1" parent="lane3">
          <mxGeometry x="925" y="92" width="435" height="44" as="geometry"/>
        </mxCell>
        <mxCell id="f2_csn" value="&lt;b&gt;Compiled CSN Bundle (JSON)&lt;/b&gt;&lt;br/&gt;Validated against CSN v1.0 spec" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E9D8FD;strokeColor=#6B46C1;fontSize=11;" vertex="1" parent="lane3">
          <mxGeometry x="25" y="148" width="1335" height="42" as="geometry"/>
        </mxCell>

        <!-- Lane 4: F3 Governance -->
        <mxCell id="lane4" value="&lt;b&gt;4. F3 Governance and deployment&lt;/b&gt;" style="swimlane;whiteSpace=wrap;html=1;fillColor=#FFF7ED;strokeColor=#EA580C;fontColor=#C2410C;fontSize=13;fontStyle=1;startSize=28;rounded=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="690" width="1380" height="150" as="geometry"/>
        </mxCell>
        <mxCell id="f3_t10" value="&lt;b&gt;T10 Security&lt;/b&gt;&lt;br/&gt;Chains to DAC" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#EA580C;fontSize=11;" vertex="1" parent="lane4">
          <mxGeometry x="25" y="38" width="310" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="f3_t11" value="&lt;b&gt;T11 Recon&lt;/b&gt;&lt;br/&gt;Counts, SHA-256" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#EA580C;fontSize=11;" vertex="1" parent="lane4">
          <mxGeometry x="355" y="38" width="310" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="f3_t12" value="&lt;b&gt;T12 Dashboard&lt;/b&gt;&lt;br/&gt;Streamlit control" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#EA580C;fontSize=11;" vertex="1" parent="lane4">
          <mxGeometry x="685" y="38" width="310" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="f3_deploy" value="&lt;b&gt;Deploy Agent&lt;/b&gt;&lt;br/&gt;CLI + REST APIs" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#EA580C;fontSize=11;" vertex="1" parent="lane4">
          <mxGeometry x="1015" y="38" width="345" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="f3_audit" value="&lt;b&gt;Audit and Cutover Log&lt;/b&gt;: Automated artifact deployment timestamps, warnings &amp;amp; backlog tracker" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFEDD5;strokeColor=#C2410C;fontSize=11;" vertex="1" parent="lane4">
          <mxGeometry x="25" y="98" width="1335" height="38" as="geometry"/>
        </mxCell>

        <!-- Lane 5: Target -->
        <mxCell id="lane5" value="&lt;b&gt;5. Target: SAP Datasphere&lt;/b&gt;" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontColor=#334155;fontSize=13;fontStyle=1;startSize=28;rounded=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="855" width="1380" height="175" as="geometry"/>
        </mxCell>
        <mxCell id="t_space" value="&lt;b&gt;Space&lt;/b&gt;&lt;br/&gt;Quota, roles" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;fontSize=11;" vertex="1" parent="lane5">
          <mxGeometry x="25" y="40" width="245" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="t_tbl" value="&lt;b&gt;Tables&lt;/b&gt;&lt;br/&gt;Dims, texts" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;fontSize=11;" vertex="1" parent="lane5">
          <mxGeometry x="290" y="40" width="245" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="t_view" value="&lt;b&gt;Views&lt;/b&gt;&lt;br/&gt;Fact, SQL" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;fontSize=11;" vertex="1" parent="lane5">
          <mxGeometry x="555" y="40" width="255" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="t_am" value="&lt;b&gt;Models&lt;/b&gt;&lt;br/&gt;SAC, Power BI" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;fontSize=11;" vertex="1" parent="lane5">
          <mxGeometry x="830" y="40" width="255" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="t_tc" value="&lt;b&gt;Task Chains&lt;/b&gt;&lt;br/&gt;Plus DAC" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;fontSize=11;" vertex="1" parent="lane5">
          <mxGeometry x="1105" y="40" width="255" height="48" as="geometry"/>
        </mxCell>
        <mxCell id="t_bar" value="&lt;b&gt;Ingestion Interface: REST Definitions | Task Chains | OData | CLI Import&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor=#64748B;fontSize=12;" vertex="1" parent="lane5">
          <mxGeometry x="25" y="100" width="1335" height="42" as="geometry"/>
        </mxCell>

        <!-- Right Notes Panel -->
        <mxCell id="notes" value="&lt;b&gt;Architecture &amp;amp; Migration Details&lt;/b&gt;&lt;hr/&gt;&lt;br/&gt;&lt;b&gt;1. Source: SAP BW/4HANA&lt;/b&gt;&lt;br/&gt;• Tables: ROOSOURCE, ODQMON, RSDIOBJ, RSDATTR&lt;br/&gt;• Inbound *1, Active *2 &amp;amp; Change log *3 delta tables&lt;br/&gt;• SIDs (/BI0/S*, /BI0/X*, /BI0/Y*) resolved to natural keys&lt;br/&gt;&lt;br/&gt;&lt;b&gt;2. F1 Foundation Layer&lt;/b&gt;&lt;br/&gt;• T0 loads metadata dictionary snapshots into DuckDB&lt;br/&gt;• T1 uses NetworkX DiGraph + Tarjan's SCC for cycles&lt;br/&gt;• T2 scores 1–5 (compounding, ABAP routines, hierarchy)&lt;br/&gt;• T3 stages wave batches and manages prerequisite locks&lt;br/&gt;&lt;br/&gt;&lt;b&gt;3. F2 Generators &amp;amp; Transpilation&lt;/b&gt;&lt;br/&gt;• T4 maps BW source systems to DSP Space Connections&lt;br/&gt;• T5 converts characteristics &amp;amp; texts to #DIMENSION CSN&lt;br/&gt;• T6 transpiles ABAP Start/End/Field routines to SQL Views&lt;br/&gt;• T7 maps ADSOs to #FACT &amp;amp; staging local tables&lt;br/&gt;• T8 translates CompositeProviders into Relational Views&lt;br/&gt;• T9 translates BEx queries to DSP Analytic Models&lt;br/&gt;&lt;br/&gt;&lt;b&gt;4. F3 Governance &amp;amp; Controls&lt;/b&gt;&lt;br/&gt;• T10 translates RSPC chains to Datasphere Task Chains&lt;br/&gt;• T10 converts Analysis Authorizations into DAC policies&lt;br/&gt;• T11 reconciles record counts &amp;amp; SHA-256 metric sums&lt;br/&gt;• T12 Streamlit dashboard acts as master control cockpit&lt;br/&gt;&lt;br/&gt;&lt;b&gt;5. Target: SAP Datasphere&lt;/b&gt;&lt;br/&gt;• Space-level schema isolation and user role governance&lt;br/&gt;• Core CSN v1.0 schema notation for dimensions and facts&lt;br/&gt;• Multidimensional Analytic Models for SAC &amp;amp; Power BI&lt;br/&gt;• Automated Delta Replication via DP Agent &amp;amp; SCC" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontSize=10.5;align=left;valign=top;spacing=12;" vertex="1" parent="1">
          <mxGeometry x="1440" y="90" width="440" height="740" as="geometry"/>
        </mxCell>

        <!-- Right Legend -->
        <mxCell id="legend" value="&lt;b&gt;Legend &amp;amp; Visual Conventions&lt;/b&gt;&lt;hr/&gt;&lt;br/&gt;&lt;b&gt;Solid Blue Arrow (2px)&lt;/b&gt;: Primary Data &amp;amp; Metadata Flow&lt;br/&gt;&lt;b&gt;Dashed Orange Arrow (1.5px)&lt;/b&gt;: Reconciliation Loop (T11)&lt;br/&gt;&lt;b&gt;Dashed Gray Arrow (1px)&lt;/b&gt;: Control Plane / Dashboard Trigger&lt;br/&gt;&lt;br/&gt;Canvas: 1920×1080 Landscape | Snap-to-Grid: 10px | Inter / Segoe UI" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontSize=10.5;align=left;valign=top;spacing=12;" vertex="1" parent="1">
          <mxGeometry x="1440" y="855" width="440" height="175" as="geometry"/>
        </mxCell>

        <!-- Solid Connectors -->
        <mxCell id="e_src_f1" value="Raw metadata" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2.5;strokeColor=#2563EB;fontSize=10;fontColor=#1D4ED8;" edge="1" parent="1" source="s_bar" target="f1_t0">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_f1_t3_f2" value="Wave batches + path tags" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2.5;strokeColor=#2563EB;fontSize=10;fontColor=#1D4ED8;" edge="1" parent="1" source="f1_t3" target="f2_t6">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_f2_f3" value="CSN artifacts" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2.5;strokeColor=#2563EB;fontSize=10;fontColor=#1D4ED8;" edge="1" parent="1" source="f2_csn" target="f3_deploy">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_f3_target" value="Import definitions" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2.5;strokeColor=#2563EB;fontSize=10;fontColor=#1D4ED8;" edge="1" parent="1" source="f3_deploy" target="t_bar">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <!-- Dashed Reconciliation Arrows -->
        <mxCell id="e_recon_src" value="Reconciliation" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;dashed=1;strokeColor=#EA580C;fontSize=10;fontColor=#C2410C;" edge="1" parent="1" source="f3_t11" target="s2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_recon_tgt" value="Reconciliation" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;dashed=1;strokeColor=#EA580C;fontSize=10;fontColor=#C2410C;" edge="1" parent="1" source="f3_t11" target="t_tbl">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

        <!-- Control Plane Arrows -->
        <mxCell id="e_ctrl_t3" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.2;dashed=1;strokeColor=#6B7280;" edge="1" parent="1" source="f3_t12" target="f1_t3">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_ctrl_deploy" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.2;dashed=1;strokeColor=#6B7280;" edge="1" parent="1" source="f3_t12" target="f3_deploy">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

def main():
    brain_dir = r"C:\Users\Varad\.gemini\antigravity-cli\brain\fe73ba1d-65f7-4038-9e93-de509c9dc3e1\clean_code"
    os.makedirs(brain_dir, exist_ok=True)
    
    # 1. Generate SVG
    svg_content = generate_svg()
    svg_path = os.path.join(brain_dir, "BW_Morph_Architecture_Horizontal.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated SVG: {svg_path} ({len(svg_content)} bytes)")

    # 2. Generate Draw.io
    drawio_content = generate_drawio()
    drawio_path = os.path.join(brain_dir, "BW_Morph_Architecture_Horizontal.drawio")
    with open(drawio_path, "w", encoding="utf-8") as f:
        f.write(drawio_content)
    print(f"Generated Drawio: {drawio_path} ({len(drawio_content)} bytes)")

    # 3. Export PNG using Chrome Headless (2x scale: 3840x2160)
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    png_path = os.path.join(brain_dir, "BW_Morph_Architecture_Horizontal.png")
    abs_svg = os.path.abspath(svg_path)

    html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  html, body {{
    margin: 0;
    padding: 0;
    width: 1920px;
    height: 1080px;
    background: #FFFFFF;
    overflow: hidden;
  }}
  img {{
    width: 1920px;
    height: 1080px;
    display: block;
  }}
</style>
</head>
<body>
  <img src="file:///{abs_svg.replace(os.sep, '/')}" />
</body>
</html>"""
    html_path = os.path.join(brain_dir, "render_wrapper.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_wrapper)

    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--force-device-scale-factor=2",
        "--window-size=1920,1080",
        f"--screenshot={png_path}",
        f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}"
    ]
    print("Running Chrome headless screenshot...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Chrome exit code: {res.returncode}")
    if os.path.exists(png_path):
        print(f"Generated PNG successfully: {png_path} ({os.path.getsize(png_path)} bytes)")
    else:
        print("PNG generation failed:", res.stderr)

if __name__ == "__main__":
    main()
