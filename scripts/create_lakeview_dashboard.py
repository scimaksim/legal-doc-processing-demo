"""Create Lakeview AI/BI Dashboard for Legal Document Intelligence.

Designed for paralegals and attorneys — every widget answers a question
a legal professional would actually ask.
"""
import json
import uuid

CATALOG = "classic_stable_tetifz_catalog"
SCHEMA = "legal_docs"
T_KEY = f"{CATALOG}.{SCHEMA}.extracted_key_info"
T_SUB = f"{CATALOG}.{SCHEMA}.extracted_subpoenas"
T_INV = f"{CATALOG}.{SCHEMA}.extracted_invoices"
T_REG = f"{CATALOG}.{SCHEMA}.extracted_regulatory"
T_ELE = f"{CATALOG}.{SCHEMA}.document_elements"


def uid():
    return uuid.uuid4().hex[:8]


def counter(dataset, field, title, display=""):
    return {
        "name": uid(),
        "queries": [{"name": "main_query", "query": {"datasetName": dataset, "fields": [{"name": field, "expression": f"`{field}`"}], "disaggregated": True}}],
        "spec": {"version": 2, "widgetType": "counter", "encodings": {"value": {"fieldName": field, "displayName": display or title}}, "frame": {"showTitle": True, "title": title}}
    }


def bar(dataset, x, y, title, color="#FFAB00", sort="y-reversed", x_label=None, y_label=None):
    return {
        "name": uid(),
        "queries": [{"name": "main_query", "query": {"datasetName": dataset, "fields": [
            {"name": x, "expression": f"`{x}`"},
            {"name": y, "expression": f"`{y}`"}
        ], "disaggregated": True}}],
        "spec": {"version": 3, "widgetType": "bar", "encodings": {
            "x": {"fieldName": x, "scale": {"type": "categorical", "sort": {"by": sort}}, "displayName": x_label or x},
            "y": {"fieldName": y, "scale": {"type": "quantitative"}, "displayName": y_label or y},
            "label": {"show": True}
        }, "frame": {"showTitle": True, "title": title}, "mark": {"colors": [color]}}
    }


def pie(dataset, angle_field, color_field, title):
    return {
        "name": uid(),
        "queries": [{"name": "main_query", "query": {"datasetName": dataset, "fields": [
            {"name": angle_field, "expression": f"`{angle_field}`"},
            {"name": color_field, "expression": f"`{color_field}`"}
        ], "disaggregated": True}}],
        "spec": {"version": 3, "widgetType": "pie", "encodings": {
            "angle": {"fieldName": angle_field, "scale": {"type": "quantitative"}, "displayName": "Count"},
            "color": {"fieldName": color_field, "scale": {"type": "categorical"}, "displayName": color_field.replace("_", " ").title()}
        }, "frame": {"showTitle": True, "title": title}}
    }


def table(dataset, columns, title):
    fields = [{"name": c["fieldName"], "expression": f'`{c["fieldName"]}`'} for c in columns]
    return {
        "name": uid(),
        "queries": [{"name": "main_query", "query": {"datasetName": dataset, "fields": fields, "disaggregated": True}}],
        "spec": {"version": 1, "widgetType": "table", "encodings": {"columns": columns}, "frame": {"showTitle": True, "title": title}}
    }


def text(md):
    return {"name": uid(), "textbox_spec": md}


def col(field, title, typ="string", fmt=None, align=None):
    c = {"fieldName": field, "type": typ, "displayAs": fmt or typ, "title": title}
    if align:
        c["alignContent"] = align
    return c


def build_dashboard():
    datasets = []
    pages = []

    def ds(name, sql):
        datasets.append({"name": name, "displayName": name, "queryLines": [sql]})

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 1: MATTER OVERVIEW  (the "war room" view)
    # ═══════════════════════════════════════════════════════════════════════

    ds("kpi_docs", f"SELECT COUNT(DISTINCT file_name) as total FROM {T_KEY}")
    ds("kpi_spend", f"SELECT ROUND(SUM(CAST(REGEXP_REPLACE(invoice_total, '[^0-9.]', '') AS DOUBLE)),2) as total FROM {T_INV}")
    ds("kpi_subpoenas", f"SELECT COUNT(*) as total FROM {T_SUB}")
    ds("kpi_regulatory", f"SELECT COUNT(*) as total FROM {T_REG}")

    ds("doc_type_mix", f"SELECT document_type, COUNT(*) as cnt FROM {T_KEY} GROUP BY document_type")
    ds("jurisdiction_exposure",
       f"SELECT governing_law as jurisdiction, COUNT(*) as matters FROM {T_KEY} WHERE governing_law IS NOT NULL AND governing_law != '' GROUP BY governing_law ORDER BY matters DESC")
    ds("risk_flags_all",
       f"SELECT risk_flags, COUNT(*) as cnt FROM {T_KEY} WHERE risk_flags IS NOT NULL AND risk_flags != '' GROUP BY risk_flags ORDER BY cnt DESC LIMIT 10")

    p1 = []
    p1.append({"widget": text("# Legal Matter Overview\nPortfolio-wide snapshot: active matters, jurisdictional exposure, outside counsel spend, and risk flags requiring attention."), "position": {"x": 0, "y": 0, "width": 6, "height": 1}})
    p1.append({"widget": counter("kpi_docs", "total", "Documents Under Management"), "position": {"x": 0, "y": 1, "width": 1, "height": 2}})
    p1.append({"widget": counter("kpi_spend", "total", "Outside Counsel Spend ($)"), "position": {"x": 1, "y": 1, "width": 2, "height": 2}})
    p1.append({"widget": counter("kpi_subpoenas", "total", "Active Subpoenas"), "position": {"x": 3, "y": 1, "width": 1, "height": 2}})
    p1.append({"widget": counter("kpi_regulatory", "total", "Regulatory Filings"), "position": {"x": 4, "y": 1, "width": 2, "height": 2}})

    p1.append({"widget": pie("doc_type_mix", "cnt", "document_type", "Matter Type Distribution"), "position": {"x": 0, "y": 3, "width": 2, "height": 5}})
    p1.append({"widget": bar("jurisdiction_exposure", "jurisdiction", "matters", "Jurisdictional Exposure", color="#2563eb", x_label="Governing Law", y_label="Agreements"), "position": {"x": 2, "y": 3, "width": 2, "height": 5}})
    p1.append({"widget": bar("risk_flags_all", "risk_flags", "cnt", "Risk Flags Requiring Review", color="#FF3621", x_label="Risk Flag", y_label="Documents"), "position": {"x": 4, "y": 3, "width": 2, "height": 5}})

    pages.append({"name": uid(), "displayName": "Matter Overview", "pageType": "PAGE_TYPE_CANVAS", "layout": p1})

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 2: DISCOVERY & SUBPOENAS  (paralegal daily driver)
    # ═══════════════════════════════════════════════════════════════════════

    ds("sub_deadlines",
       f"SELECT file_name, case_number, court_jurisdiction, requesting_party, responding_party, production_deadline, preservation_required, data_custodians FROM {T_SUB} ORDER BY production_deadline")
    ds("sub_by_court",
       f"SELECT court_jurisdiction, COUNT(*) as cnt FROM {T_SUB} GROUP BY court_jurisdiction ORDER BY cnt DESC")
    ds("sub_custodians",
       f"SELECT data_custodians as custodian, COUNT(*) as matters FROM {T_SUB} WHERE data_custodians IS NOT NULL AND data_custodians != '' GROUP BY data_custodians ORDER BY matters DESC LIMIT 10")
    ds("sub_preservation",
       f"SELECT preservation_required, COUNT(*) as cnt FROM {T_SUB} GROUP BY preservation_required")

    p2 = []
    p2.append({"widget": text("# Discovery & Subpoena Management\nProduction deadlines, custodian obligations, preservation holds, and jurisdictional distribution of active subpoenas."), "position": {"x": 0, "y": 0, "width": 6, "height": 1}})

    p2.append({"widget": counter("kpi_subpoenas", "total", "Active Subpoenas"), "position": {"x": 0, "y": 1, "width": 2, "height": 2}})
    p2.append({"widget": bar("sub_by_court", "court_jurisdiction", "cnt", "Subpoenas by Court / Jurisdiction", color="#AB4057", x_label="Court", y_label="Subpoenas"), "position": {"x": 2, "y": 1, "width": 2, "height": 4}})
    p2.append({"widget": pie("sub_preservation", "cnt", "preservation_required", "Preservation Hold Status"), "position": {"x": 4, "y": 1, "width": 2, "height": 4}})

    p2.append({"widget": table("sub_deadlines", [
        col("case_number", "Case No."),
        col("court_jurisdiction", "Court"),
        col("requesting_party", "Requesting Party"),
        col("responding_party", "Responding Party"),
        col("production_deadline", "Production Deadline"),
        col("preservation_required", "Preservation Hold"),
        col("data_custodians", "Custodians"),
    ], "Production Deadline Tracker"), "position": {"x": 0, "y": 5, "width": 6, "height": 6}})

    pages.append({"name": uid(), "displayName": "Discovery & Subpoenas", "pageType": "PAGE_TYPE_CANVAS", "layout": p2})

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 3: CONTRACT RISK REVIEW  (attorney review board)
    # ═══════════════════════════════════════════════════════════════════════

    ds("contract_terms",
       f"SELECT file_name, document_type, governing_law, non_compete_duration, confidentiality_period, termination_notice_period, risk_flags FROM {T_KEY} ORDER BY file_name")
    ds("noncompete_by_law",
       f"SELECT governing_law, COUNT(*) as cnt FROM {T_KEY} WHERE non_compete_duration IS NOT NULL AND non_compete_duration != '' AND governing_law IS NOT NULL GROUP BY governing_law ORDER BY cnt DESC")
    ds("obligations_risk",
       f"SELECT file_name, document_type, key_obligations, risk_flags FROM {T_KEY} WHERE risk_flags IS NOT NULL AND risk_flags != '' ORDER BY file_name")
    ds("dollar_exposure",
       f"SELECT file_name, document_type, key_dollar_amounts, governing_law FROM {T_KEY} WHERE key_dollar_amounts IS NOT NULL AND key_dollar_amounts != '' ORDER BY file_name")

    p3 = []
    p3.append({"widget": text("# Contract Risk Review\nRestrictive covenants, enforceability by jurisdiction, dollar exposure, and flagged obligations across your agreement portfolio."), "position": {"x": 0, "y": 0, "width": 6, "height": 1}})

    p3.append({"widget": bar("noncompete_by_law", "governing_law", "cnt", "Non-Competes by Governing Law (Enforceability Varies)", color="#8B5CF6", x_label="Jurisdiction", y_label="Agreements with Non-Compete"), "position": {"x": 0, "y": 1, "width": 3, "height": 4}})
    p3.append({"widget": pie("jurisdiction_exposure", "matters", "jurisdiction", "Agreement Concentration by Jurisdiction"), "position": {"x": 3, "y": 1, "width": 3, "height": 4}})

    p3.append({"widget": table("contract_terms", [
        col("file_name", "Agreement"),
        col("document_type", "Type"),
        col("governing_law", "Governing Law"),
        col("non_compete_duration", "Non-Compete"),
        col("confidentiality_period", "Confidentiality"),
        col("termination_notice_period", "Termination Notice"),
        col("risk_flags", "Risk Flags"),
    ], "Restrictive Covenant & Termination Summary"), "position": {"x": 0, "y": 5, "width": 6, "height": 5}})

    p3.append({"widget": table("dollar_exposure", [
        col("file_name", "Agreement"),
        col("document_type", "Type"),
        col("key_dollar_amounts", "Dollar Amounts / Liability Caps"),
        col("governing_law", "Governing Law"),
    ], "Financial Exposure by Agreement"), "position": {"x": 0, "y": 10, "width": 6, "height": 4}})

    pages.append({"name": uid(), "displayName": "Contract Risk Review", "pageType": "PAGE_TYPE_CANVAS", "layout": p3})

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 4: OUTSIDE COUNSEL BILLING AUDIT  (GC / billing partner view)
    # ═══════════════════════════════════════════════════════════════════════

    ds("spend_by_firm",
       f"SELECT law_firm, ROUND(SUM(CAST(REGEXP_REPLACE(invoice_total, '[^0-9.]', '') AS DOUBLE)),2) as total_billed, COUNT(*) as invoices FROM {T_INV} GROUP BY law_firm ORDER BY total_billed DESC")
    ds("rate_benchmark",
       f"SELECT law_firm, ROUND(MAX(CAST(REGEXP_REPLACE(highest_hourly_rate, '[^0-9.]', '') AS DOUBLE)),2) as max_rate FROM {T_INV} WHERE highest_hourly_rate IS NOT NULL GROUP BY law_firm ORDER BY max_rate DESC")
    ds("billing_flags",
       f"SELECT compliance_flags, COUNT(*) as cnt FROM {T_INV} WHERE compliance_flags IS NOT NULL AND compliance_flags != '' GROUP BY compliance_flags ORDER BY cnt DESC")
    ds("invoice_audit",
       f"SELECT law_firm, client, matter_number, billing_period, invoice_total, total_hours, highest_hourly_rate, compliance_flags FROM {T_INV} ORDER BY law_firm, billing_period")

    p4 = []
    p4.append({"widget": text("# Outside Counsel Billing Audit\nSpend analysis by firm, hourly rate benchmarking against billing guidelines, and compliance flag review for invoice approval workflows."), "position": {"x": 0, "y": 0, "width": 6, "height": 1}})

    p4.append({"widget": counter("kpi_spend", "total", "Total Outside Counsel Spend ($)"), "position": {"x": 0, "y": 1, "width": 2, "height": 2}})
    p4.append({"widget": bar("spend_by_firm", "law_firm", "total_billed", "Spend by Law Firm", color="#FFAB00", x_label="Law Firm", y_label="Total Billed ($)"), "position": {"x": 2, "y": 1, "width": 2, "height": 4}})
    p4.append({"widget": bar("rate_benchmark", "law_firm", "max_rate", "Highest Hourly Rate by Firm", color="#AB4057", x_label="Law Firm", y_label="Max Rate ($/hr)"), "position": {"x": 4, "y": 1, "width": 2, "height": 4}})

    p4.append({"widget": bar("billing_flags", "compliance_flags", "cnt", "Billing Guideline Violations", color="#FF3621", x_label="Compliance Flag", y_label="Invoices"), "position": {"x": 0, "y": 5, "width": 3, "height": 4}})

    p4.append({"widget": text("**Review Required:** Invoices with compliance flags may exceed rate caps, contain block billing, or include non-approved expenses. Route flagged invoices to the billing partner for review before payment."), "position": {"x": 3, "y": 5, "width": 3, "height": 1}})

    p4.append({"widget": table("invoice_audit", [
        col("law_firm", "Law Firm"),
        col("client", "Client / Matter"),
        col("matter_number", "Matter No."),
        col("billing_period", "Period"),
        col("invoice_total", "Amount", align="right"),
        col("total_hours", "Hours", align="right"),
        col("highest_hourly_rate", "Top Rate", align="right"),
        col("compliance_flags", "Compliance Flags"),
    ], "Invoice Line Detail — Pending Review"), "position": {"x": 0, "y": 9, "width": 6, "height": 6}})

    pages.append({"name": uid(), "displayName": "Billing Audit", "pageType": "PAGE_TYPE_CANVAS", "layout": p4})

    # ═══════════════════════════════════════════════════════════════════════
    # PAGE 5: REGULATORY COMPLIANCE  (compliance officer / regulatory counsel)
    # ═══════════════════════════════════════════════════════════════════════

    ds("reg_by_agency",
       f"SELECT issuing_agency, COUNT(*) as filings FROM {T_REG} GROUP BY issuing_agency ORDER BY filings DESC")
    ds("reg_by_type",
       f"SELECT document_type, COUNT(*) as cnt FROM {T_REG} GROUP BY document_type ORDER BY cnt DESC")
    ds("reg_tracker",
       f"SELECT issuing_agency, document_type, regulation_id, effective_date, comment_period_deadline, affected_entities, penalties, compliance_requirements FROM {T_REG} ORDER BY effective_date")
    ds("reg_penalties",
       f"SELECT issuing_agency, regulation_id, penalties FROM {T_REG} WHERE penalties IS NOT NULL AND penalties != '' ORDER BY issuing_agency")

    p5 = []
    p5.append({"widget": text("# Regulatory Compliance Tracker\nFiling obligations by agency, upcoming comment period deadlines, penalty exposure, and compliance requirement summaries."), "position": {"x": 0, "y": 0, "width": 6, "height": 1}})

    p5.append({"widget": counter("kpi_regulatory", "total", "Regulatory Filings Tracked"), "position": {"x": 0, "y": 1, "width": 2, "height": 2}})
    p5.append({"widget": bar("reg_by_agency", "issuing_agency", "filings", "Filings by Regulatory Agency", color="#00A972", x_label="Agency", y_label="Filings"), "position": {"x": 2, "y": 1, "width": 2, "height": 4}})
    p5.append({"widget": pie("reg_by_type", "cnt", "document_type", "Filing Type Distribution"), "position": {"x": 4, "y": 1, "width": 2, "height": 4}})

    p5.append({"widget": table("reg_tracker", [
        col("issuing_agency", "Agency"),
        col("document_type", "Filing Type"),
        col("regulation_id", "Regulation"),
        col("effective_date", "Effective Date"),
        col("comment_period_deadline", "Comment Deadline"),
        col("affected_entities", "Affected Entities"),
        col("penalties", "Penalties"),
        col("compliance_requirements", "Requirements"),
    ], "Regulatory Filing Obligations"), "position": {"x": 0, "y": 5, "width": 6, "height": 6}})

    p5.append({"widget": table("reg_penalties", [
        col("issuing_agency", "Agency"),
        col("regulation_id", "Regulation"),
        col("penalties", "Penalty / Enforcement Risk"),
    ], "Penalty Exposure Summary"), "position": {"x": 0, "y": 11, "width": 6, "height": 4}})

    pages.append({"name": uid(), "displayName": "Regulatory Compliance", "pageType": "PAGE_TYPE_CANVAS", "layout": p5})

    # ═══════════════════════════════════════════════════════════════════════

    dashboard = {
        "datasets": datasets,
        "pages": pages,
        "uiSettings": {"theme": {"widgetHeaderAlignment": "ALIGNMENT_UNSPECIFIED"}, "applyModeEnabled": False}
    }
    return json.dumps(dashboard)


if __name__ == "__main__":
    payload = {
        "display_name": "Legal Document Intelligence Analytics",
        "warehouse_id": "d09c046d71503257",
        "parent_path": "/Users/maksim.nikiforov@databricks.com",
        "serialized_dashboard": build_dashboard()
    }
    print(json.dumps(payload))
