"""
Generates a comprehensive, professional PDF solution architecture document for BW Morph.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#546E7A"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "BW Morph: SAP BW/4HANA to SAP Datasphere Migration Accelerator")
            self.drawRightString(558, 755, "Solution Architecture Blueprint")
            self.setStrokeColor(colors.HexColor("#CFD8DC"))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)

        # Footer
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 35, text)
        self.drawString(54, 35, "CONFIDENTIAL & PROPRIETARY — PROJECT BW MORPH")
        self.setStrokeColor(colors.HexColor("#CFD8DC"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)

        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1A237E'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0D47A1'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#263238'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#263238'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#455A64')
    )

    table_header_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#263238')
    )

    table_cell_bold = ParagraphStyle(
        'TCB',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("PROJECT BW MORPH", title_style))
    story.append(Paragraph("<b>SAP BW/4HANA to SAP Datasphere Migration Accelerator</b><br/>Enterprise Solution Architecture, Pipeline Flow &amp; Technical Mapping Catalog", subtitle_style))

    meta_text = """
    <b>Document Version:</b> 1.0.0 &nbsp;|&nbsp; <b>Classification:</b> Enterprise Architecture Blueprint<br/>
    <b>Target Platform:</b> SAP Datasphere (Business Data Cloud) &nbsp;|&nbsp; <b>Source:</b> SAP BW 7.x / BW on HANA / BW/4HANA<br/>
    <b>Author / Role:</b> Senior Enterprise Solution Architect
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1A237E'), spaceAfter=12))

    # SECTION 1
    story.append(Paragraph("1. Executive Summary &amp; Architectural Objectives", h1_style))
    story.append(Paragraph(
        "<b>BW Morph</b> is an enterprise migration accelerator designed to automate, de-risk, and significantly compress the timeline for replatforming legacy SAP Business Warehouse (BW/4HANA and BW on HANA) systems into SAP Datasphere. Monolithic on-premise BW systems carry decades of accumulated complexity—compounded InfoObjects, highly custom ABAP routines, multi-level staging ADSOs, and complex join structures. BW Morph decouples and orchestrates this transition via a metadata-driven approach divided into three distinct architectural phases:",
        body_style
    ))
    story.append(Paragraph("• <b>F1: Foundation Layer (T0–T3):</b> Automated inventory scanning, shared metadata persistence in DuckDB, cyclic graph dependency analysis with topological wave planning, complexity scoring (1–5 scale), and traffic dispatching.", bullet_style))
    story.append(Paragraph("• <b>F2: Generator &amp; Translator Layer (T4–T9):</b> Automated transpilation of BW DataSources, InfoObjects, Transformations/ABAP, ADSOs, CompositeProviders, and BEx Queries into native SAP Core Schema Notation (CSN) JSON, SQL Views, and Analytic Models.", bullet_style))
    story.append(Paragraph("• <b>F3: Cross-Cutting &amp; Governance Layer (T10–T12):</b> Process chain-to-task chain orchestration, Analysis Authorizations to Data Access Controls (DAC), data quality row-count and checksum reconciliation, and an executive Streamlit control dashboard.", bullet_style))

    # SECTION 2
    story.append(Spacer(1, 6))
    story.append(Paragraph("2. Repository Architecture &amp; Codebase Inventory", h1_style))
    story.append(Paragraph("The BW Morph codebase implements modular tools mapped directly to the migration taxonomy:", body_style))

    codebase_data = [
        [Paragraph("Component / Script", table_header_style), Paragraph("Architectural Role", table_header_style), Paragraph("Implementation Details &amp; Target Output", table_header_style)],
        [Paragraph("main.py", table_cell_bold), Paragraph("Pipeline Orchestrator", table_cell_style), Paragraph("Main CLI runner executing the full T0–T12 wave execution lifecycle.", table_cell_style)],
        [Paragraph("config/settings.yaml", table_cell_bold), Paragraph("Global Configuration", table_cell_style), Paragraph("Defines target space ('DEV_SPACE_01'), DuckDB repo path, and reconciliation tolerance.", table_cell_style)],
        [Paragraph("repository/db_manager.py", table_cell_bold), Paragraph("Metadata Repository", table_cell_style), Paragraph("DuckDB / SQLite manager persisting objects, dependencies, transformations, and waves.", table_cell_style)],
        [Paragraph("extractors/t0_bw_scanner.py", table_cell_bold), Paragraph("Tool T0 Scanner", table_cell_style), Paragraph("Extracts in-scope inventory from BW Dictionary tables and catalogs raw JSON metadata.", table_cell_style)],
        [Paragraph("graph/t1_dependency_builder.py", table_cell_bold), Paragraph("Tool T1 Wave Planner", table_cell_style), Paragraph("Constructs NetworkX directed graph; breaks cyclic paths; outputs topological waves.", table_cell_style)],
        [Paragraph("graph/t2_classifier.py", table_cell_bold), Paragraph("Tool T2 Complexity Scorer", table_cell_style), Paragraph("Rates objects on a 1–5 scale and tags target taxonomy (Paths 1 through 7).", table_cell_style)],
        [Paragraph("generators/base_generator.py", table_cell_bold), Paragraph("Base CSN Generator", table_cell_style), Paragraph("Standard SAP CSN v1.0 wrapper and data type mapper (CHAR, DEC, DATS -> cds.*).", table_cell_style)],
        [Paragraph("generators/t5_master_data.py", table_cell_bold), Paragraph("Tool T5 InfoObject Migrator", table_cell_style), Paragraph("Converts InfoObjects, Attributes, and Texts into CSN Dimensions & Local Tables.", table_cell_style)],
        [Paragraph("generators/t6_transformation.py", table_cell_bold), Paragraph("Tool T6 Transpiler", table_cell_style), Paragraph("Transpiles formulas and ABAP Start/End/Field routines into Datasphere SQL Views.", table_cell_style)],
        [Paragraph("generators/t7_adso.py", table_cell_bold), Paragraph("Tool T7 ADSO Migrator", table_cell_style), Paragraph("Converts Inbound, Active, and Change Log ADSOs into Local Tables & Fact Views.", table_cell_style)],
        [Paragraph("dashboard/app.py", table_cell_bold), Paragraph("Tool T12 Control Center", table_cell_style), Paragraph("Streamlit dashboard displaying KPIs, dependency graph, wave status, and CSN preview.", table_cell_style)]
    ]

    t_codebase = Table(codebase_data, colWidths=[105, 95, 304])
    t_codebase.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A237E')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F5F7FA')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CFD8DC')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_codebase)

    # PAGE BREAK FOR FLOW
    story.append(PageBreak())

    # SECTION 3
    story.append(Paragraph("3. End-to-End Migration Flow &amp; Tool Lifecycle (T0 to T12)", h1_style))
    story.append(Paragraph(
        "The migration pipeline follows a strictly sequenced, dependency-aware data stream. Metadata enters from SAP BW and progresses sequentially through foundation analysis, code generation, governance validation, and Datasphere deployment:",
        body_style
    ))

    # Flow Table / Lifecycle
    flow_data = [
        [Paragraph("Layer", table_header_style), Paragraph("Tool ID &amp; Name", table_header_style), Paragraph("Input Stream", table_header_style), Paragraph("Core Functionality &amp; Internal Logic", table_header_style), Paragraph("Handover Target", table_header_style)],
        [
            Paragraph("<b>F1: Foundation</b>", table_cell_bold),
            Paragraph("<b>T0:</b> BW Inventory Scanner", table_cell_bold),
            Paragraph("BW Dictionary via RFC / OData", table_cell_style),
            Paragraph("Connects to BW system, extracts in-scope objects, and populates DuckDB metadata repo.", table_cell_style),
            Paragraph("DuckDB (objects, deps)", table_cell_style)
        ],
        [
            Paragraph("<b>F1: Foundation</b>", table_cell_bold),
            Paragraph("<b>T1:</b> Graph &amp; Wave Planner", table_cell_bold),
            Paragraph("Dependencies table from DuckDB", table_cell_style),
            Paragraph("Constructs DiGraph; detects and breaks cyclic references; derives topological migration waves.", table_cell_style),
            Paragraph("T3 Traffic Controller", table_cell_style)
        ],
        [
            Paragraph("<b>F1: Foundation</b>", table_cell_bold),
            Paragraph("<b>T2:</b> Scoring &amp; Classifier", table_cell_bold),
            Paragraph("Raw metadata from DuckDB", table_cell_style),
            Paragraph("Evaluates 1–5 complexity based on routines/compounding; tags target migration Paths 1–7.", table_cell_style),
            Paragraph("T3 Traffic Controller", table_cell_style)
        ],
        [
            Paragraph("<b>F1: Foundation</b>", table_cell_bold),
            Paragraph("<b>T3:</b> Traffic Controller", table_cell_bold),
            Paragraph("Waves (T1) + Scores (T2)", table_cell_style),
            Paragraph("Combines topology and risk scores to batch execution; dispatches objects to F2 generators.", table_cell_style),
            Paragraph("F2 Generators (T4–T9)", table_cell_style)
        ],
        [
            Paragraph("<b>F2: Generator</b>", table_cell_bold),
            Paragraph("<b>T4:</b> Source System Converter", table_cell_bold),
            Paragraph("Source System specs (P1)", table_cell_style),
            Paragraph("Converts BW source system connections (S4, ECC, ODP) into Datasphere Space Connections.", table_cell_style),
            Paragraph("DSP Space Connections", table_cell_style)
        ],
        [
            Paragraph("<b>F2: Generator</b>", table_cell_bold),
            Paragraph("<b>T5:</b> InfoObjects Migrator", table_cell_bold),
            Paragraph("InfoObjects (P2: CHA, KYF)", table_cell_style),
            Paragraph("Converts characteristics, attributes (/BI0/P*), texts (/BI0/T*), and surrogates into CSN Dimensions.", table_cell_style),
            Paragraph("CSN Artifact Bundle", table_cell_style)
        ],
        [
            Paragraph("<b>F2: Generator</b>", table_cell_bold),
            Paragraph("<b>T6:</b> SQL/ABAP Transpiler", table_cell_bold),
            Paragraph("Transformations (P3: TRFN)", table_cell_style),
            Paragraph("Transpiles direct rules, formulas, and ABAP Start/End routines into Datasphere SQL Views.", table_cell_style),
            Paragraph("CSN Artifact Bundle", table_cell_style)
        ],
        [
            Paragraph("<b>F2: Generator</b>", table_cell_bold),
            Paragraph("<b>T7:</b> ADSO Table Converter", table_cell_bold),
            Paragraph("ADSO structures (P4)", table_cell_style),
            Paragraph("Converts Inbound (*1), Active (*2), and Change Log (*3) ADSO tables into Fact Entities and Views.", table_cell_style),
            Paragraph("CSN Artifact Bundle", table_cell_style)
        ],
        [
            Paragraph("<b>F2: Generator</b>", table_cell_bold),
            Paragraph("<b>T8:</b> CompositeProvider Converter", table_cell_bold),
            Paragraph("HCPR / MultiProviders (P5)", table_cell_style),
            Paragraph("Maps joins and unions combining Fact ADSOs and Dimension InfoObjects into Relational/Analytical Views.", table_cell_style),
            Paragraph("CSN Artifact Bundle", table_cell_style)
        ],
        [
            Paragraph("<b>F2: Generator</b>", table_cell_bold),
            Paragraph("<b>T9:</b> BEx Query Converter", table_cell_bold),
            Paragraph("BEx Queries (P6)", table_cell_style),
            Paragraph("Translates restricted/calculated measures and variables into Datasphere Analytic Models.", table_cell_style),
            Paragraph("Analytic Perspectives", table_cell_style)
        ],
        [
            Paragraph("<b>F3: Governance</b>", table_cell_bold),
            Paragraph("<b>T10:</b> Process Chain &amp; Security", table_cell_bold),
            Paragraph("RSPC Chains &amp; RSEC Auth (P7)", table_cell_style),
            Paragraph("Converts process chains into Datasphere Task Chains; converts Analysis Authorizations into DAC policies.", table_cell_style),
            Paragraph("DSP Task Chains &amp; DAC", table_cell_style)
        ],
        [
            Paragraph("<b>F3: Governance</b>", table_cell_bold),
            Paragraph("<b>T11:</b> Data Quality Engine", table_cell_bold),
            Paragraph("BW source rows vs DSP target rows", table_cell_style),
            Paragraph("Executes automated row-count and SHA-256 metric hash reconciliation with tolerance checking.", table_cell_style),
            Paragraph("reconciliation_results", table_cell_style)
        ],
        [
            Paragraph("<b>F3: Governance</b>", table_cell_bold),
            Paragraph("<b>T12:</b> Web Dashboard", table_cell_bold),
            Paragraph("Metadata repo &amp; artifacts", table_cell_style),
            Paragraph("Interactive Streamlit command center visualizing KPIs, dependency graphs, waves, and code previews.", table_cell_style),
            Paragraph("End-User / Architect", table_cell_style)
        ]
    ]

    t_flow = Table(flow_data, colWidths=[70, 95, 95, 150, 94])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F5F7FA')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CFD8DC')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_flow)

    # PAGE BREAK FOR MAPPINGS & APIS
    story.append(PageBreak())

    # SECTION 4
    story.append(Paragraph("4. Technical Mapping Catalog: SAP BW to SAP Datasphere", h1_style))
    story.append(Paragraph(
        "To guarantee high-fidelity migration, BW Morph systematically maps the SAP ABAP Data Dictionary tables into corresponding modern Datasphere CSN primitives:",
        body_style
    ))

    mapping_data = [
        [Paragraph("BW Source Object", table_header_style), Paragraph("BW Dictionary Tables", table_header_style), Paragraph("Internal BW Structures / Behavior", table_header_style), Paragraph("Target SAP Datasphere Entity", table_header_style), Paragraph("CSN Semantic Category", table_header_style)],
        [
            Paragraph("InfoObjects (Characteristics)", table_cell_bold),
            Paragraph("RSDIOBJ, RSDCHABAS", table_cell_style),
            Paragraph("Business keys, compounding attributes, master data settings", table_cell_style),
            Paragraph("Local Table / Dimension Entity", table_cell_style),
            Paragraph("<code>#DIMENSION</code>", table_cell_style)
        ],
        [
            Paragraph("Master Data Attributes", table_cell_bold),
            Paragraph("/BI0/P* (time-indep)<br/>/BI0/Q* (time-dep)", table_cell_style),
            Paragraph("Display & navigational attributes linked to master characteristic", table_cell_style),
            Paragraph("CDS Elements with 1:1 or N:1 <code>cds.Association</code> links", table_cell_style),
            Paragraph("<code>Association</code>", table_cell_style)
        ],
        [
            Paragraph("Master Data Texts", table_cell_bold),
            Paragraph("/BI0/T*", table_cell_style),
            Paragraph("Language-dependent descriptions (Short, Medium, Long)", table_cell_style),
            Paragraph("Text Entity (<code>&lt;IOBJ&gt;_TEXT</code>) with compound language key", table_cell_style),
            Paragraph("<code>#TEXT</code>", table_cell_style)
        ],
        [
            Paragraph("Surrogate IDs (SIDs)", table_cell_bold),
            Paragraph("/BI0/S*, /BI0/X*, /BI0/Y*", table_cell_style),
            Paragraph("Internal integer surrogate keys used for performance", table_cell_style),
            Paragraph("Replaced with Natural Business Keys in Datasphere models", table_cell_style),
            Paragraph("Primary Key", table_cell_style)
        ],
        [
            Paragraph("ADSO: Inbound Queue", table_cell_bold),
            Paragraph("/BIC/A*1 (or /BI0/A*1)", table_cell_style),
            Paragraph("Raw unactivated data landing staging table", table_cell_style),
            Paragraph("Staging Local Table for raw ingestion", table_cell_style),
            Paragraph("<code>#STAGING</code>", table_cell_style)
        ],
        [
            Paragraph("ADSO: Active Data", table_cell_bold),
            Paragraph("/BIC/A*2 (or /BI0/A*2)", table_cell_style),
            Paragraph("Activated master/fact records with semantic key partitioning", table_cell_style),
            Paragraph("Primary Analytical Fact Local Table", table_cell_style),
            Paragraph("<code>#FACT</code>", table_cell_style)
        ],
        [
            Paragraph("ADSO: Change Log", table_cell_bold),
            Paragraph("/BIC/A*3 (or /BI0/A*3)", table_cell_style),
            Paragraph("Delta recordmode history (before/after images)", table_cell_style),
            Paragraph("Delta Audit View / Historical Change Log View", table_cell_style),
            Paragraph("Relational View", table_cell_style)
        ],
        [
            Paragraph("Transformations &amp; DTPs", table_cell_bold),
            Paragraph("RSTRAN, RSTRANRULE, RSTRANROUT", table_cell_style),
            Paragraph("Formulas, direct mappings, and ABAP Start/End/Field routines", table_cell_style),
            Paragraph("Datasphere SQL Views (AST transpiled logic &amp; CASE WHEN)", table_cell_style),
            Paragraph("SQL View / Data Flow", table_cell_style)
        ],
        [
            Paragraph("CompositeProviders", table_cell_bold),
            Paragraph("RSDHCPR, RSDHCPRCOMP, RSDHCPRLNK", table_cell_style),
            Paragraph("Star schema multi-table Left Outer/Inner joins and unions", table_cell_style),
            Paragraph("Datasphere Graphical &amp; Analytical Views with Star Joins", table_cell_style),
            Paragraph("Analytical View", table_cell_style)
        ],
        [
            Paragraph("BEx Queries", table_cell_bold),
            Paragraph("RSZELTDIR, RSZELTTXT, RSZCALC", table_cell_style),
            Paragraph("Restricted/Calculated Key Figures (RKF/CKF), Variables", table_cell_style),
            Paragraph("Datasphere Analytic Model with Parameters &amp; Perspectives", table_cell_style),
            Paragraph("Analytic Model", table_cell_style)
        ],
        [
            Paragraph("Process Chains", table_cell_bold),
            Paragraph("RSPCPROCESS, RSPCLOGCHAIN", table_cell_style),
            Paragraph("Batch scheduling of DTPs, activations, and rollups", table_cell_style),
            Paragraph("Datasphere Task Chains orchestrating data flows &amp; views", table_cell_style),
            Paragraph("Task Chain", table_cell_style)
        ],
        [
            Paragraph("Analysis Authorizations", table_cell_bold),
            Paragraph("RSECVAL, RSECBIOBJ, AGR_1251", table_cell_style),
            Paragraph("Row-level data authorization criteria by user/role", table_cell_style),
            Paragraph("Datasphere Data Access Controls (DAC) with filter criteria", table_cell_style),
            Paragraph("DAC Policy", table_cell_style)
        ]
    ]

    t_map = Table(mapping_data, colWidths=[90, 80, 124, 130, 80])
    t_map.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A237E')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F5F7FA')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CFD8DC')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_map)

    # SECTION 5
    story.append(Spacer(1, 8))
    story.append(Paragraph("5. Connectivity &amp; API Integration Framework", h1_style))
    story.append(Paragraph(
        "BW Morph utilizes industry-standard connectivity for ingestion and deployment across both platforms:",
        body_style
    ))
    story.append(Paragraph("• <b>SAP BW Inbound Metadata APIs:</b> Connected via Python RFC (<code>pyrfc</code> wrapper on SAP NetWeaver RFC SDK). Uses <code>RFC_READ_TABLE</code> for dictionary queries, <code>BAPI_MDPROVIDER_GET_DIMENSIONS</code> for multidimensional metadata, and custom OData CDS services over SAP Cloud Connector (SCC).", bullet_style))
    story.append(Paragraph("• <b>SAP Datasphere Target Deployment APIs:</b> Deploys compiled CSN documents via the official <code>@sap/datasphere-cli</code> (e.g. <code>datasphere objects import --space DEV_SPACE_01 --file &lt;csn_file&gt;</code>) and Datasphere REST APIs (<code>POST /api/v1/spaces/{space}/definitions</code>).", bullet_style))
    story.append(Paragraph("• <b>Data Pipeline &amp; Replication:</b> Physical delta data streams are replicated from source ADSO active tables into Datasphere Local Tables using the SAP Data Provisioning Agent (DP Agent) and SAP Replication Flows.", bullet_style))

    # SECTION 6
    story.append(Spacer(1, 6))
    story.append(Paragraph("6. Architecture Deliverable Reference", h1_style))
    story.append(Paragraph(
        "A complete, interactive Draw.io architectural diagram has been generated in the project workspace: <b>BW_Morph_Architecture_Flow.drawio</b>. It visualizes the complete 5-swimlane enterprise layout matching the initial Release Line Design (RLD).",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filename

if __name__ == "__main__":
    out_file = r"C:\Users\Varad\.gemini\antigravity-cli\brain\fe73ba1d-65f7-4038-9e93-de509c9dc3e1\BW_Morph_Solution_Architecture.pdf"
    build_pdf(out_file)
    print(f"Generated PDF successfully: {out_file} ({os.path.getsize(out_file)} bytes)")
