# Manifest of Temporary / Scratch / Clean Code Files

This file tracks all temporary scripts, mock datasets, and clean code generation utilities created in Project BW Morph. Any item listed here can be inspected or purged cleanly without impacting core runtime modules.

---

| File / Folder Path | Purpose & Description | Safe-to-Delete Condition |
| :--- | :--- | :--- |
| `clean_code/generate_diagrams.py` | Python generation script for SVG, Draw.io XML, and headless Chrome rendering wrapper. | Safe to delete or keep as a repeatable diagram build script. |
| `clean_code/render_wrapper.html` | Temporary HTML wrapper for 2x scale Playwright screenshot capture of the SVG diagram. | Safe to delete anytime; regenerable on demand. |
| `generate_pdf.py` | Python script using ReportLab to compile the executive solution architecture PDF. | Safe to delete or retain in `clean_code/`. |
| `extractors/sample_data.py` | Mock BW system dictionary dataset used for offline testing of T0–T12 pipeline. | Do NOT delete during demo phase; replace with live RFC extractor in production. |
