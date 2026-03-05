# Databricks notebook source
# MAGIC %md
# MAGIC # Step 6: Generate Specialized Legal Documents
# MAGIC Generates sample subpoenas, outside counsel invoices, and regulatory filings
# MAGIC to demonstrate the three specialized extraction pipelines.

# COMMAND ----------

# MAGIC %pip install fpdf2
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

try:
    catalog = spark.conf.get("spark.databricks.bundle.variables.catalog")
except Exception:
    catalog = "classic_stable_tetifz_catalog"
try:
    schema = spark.conf.get("spark.databricks.bundle.variables.schema")
except Exception:
    schema = "legal_docs"
volume_path = f"/Volumes/{catalog}/{schema}/raw_documents"

# COMMAND ----------

import random
import tempfile
import os
import shutil
from fpdf import FPDF

random.seed(123)
tmpdir = tempfile.mkdtemp()

def make_pdf(filepath, title, sections):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)
    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, heading, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, body)
        pdf.ln(4)
    pdf.output(filepath)

# ============================================================
# SUBPOENAS
# ============================================================
COURTS = [
    ("United States District Court, Southern District of New York", "New York, NY"),
    ("United States District Court, Northern District of California", "San Francisco, CA"),
    ("United States District Court, District of Delaware", "Wilmington, DE"),
    ("Superior Court of the State of California, County of Los Angeles", "Los Angeles, CA"),
    ("Circuit Court of Cook County, Illinois", "Chicago, IL"),
]
CUSTODIANS = [
    "John Smith", "Maria Rodriguez", "David Chen", "Sarah Thompson", "James Wilson",
    "Emily Davis", "Robert Kim", "Jennifer Martinez", "Michael Brown", "Lisa Anderson",
]
DOC_CATEGORIES = [
    "All electronic communications including emails, text messages, and instant messages",
    "Financial records including bank statements, wire transfers, and account ledgers",
    "Meeting minutes and board resolutions",
    "Contracts, agreements, and amendments",
    "Internal memoranda and policy documents",
    "Customer account records and transaction histories",
    "Audit reports and compliance assessments",
    "Employee personnel files and compensation records",
]

for i in range(15):
    court, location = random.choice(COURTS)
    case_num = f"{random.randint(2023,2026)}-cv-{random.randint(1000,9999)}"
    requesting = random.choice(["Securities and Exchange Commission", "Department of Justice",
                                "Federal Trade Commission", "Consumer Financial Protection Bureau",
                                "State Attorney General", f"Plaintiff {random.choice(['Alpha Corp','Beta Holdings','Gamma Partners'])}"])
    responding = random.choice(["National Financial Services Inc.", "Pacific Trust Bank", "Continental Holdings Corp.",
                                "Meridian Capital Group", "Eastshore Insurance Co.", "Northland Mortgage LLC"])
    custodians = random.sample(CUSTODIANS, random.randint(2, 5))
    date_start = f"{random.choice(['January','March','June','September'])} 1, {random.randint(2020,2024)}"
    date_end = f"{random.choice(['June','September','December'])} 30, {random.randint(2024,2026)}"
    deadline = f"{random.choice(['March','April','May','June'])} {random.randint(1,28)}, 2026"
    categories = random.sample(DOC_CATEGORIES, random.randint(3, 6))

    make_pdf(os.path.join(tmpdir, f"subpoena_{i:03d}.pdf"),
        f"SUBPOENA DUCES TECUM",
        [
            ("Court", f"{court}\nCase No. {case_num}"),
            ("Parties", f"IN THE MATTER OF:\n{requesting} v. {responding}"),
            ("To", f"{responding}\nc/o General Counsel\n{location}"),
            ("Command", f"YOU ARE HEREBY COMMANDED to produce the documents and materials described below "
             f"at the offices of {requesting}, or electronically in a mutually agreed format, "
             f"on or before {deadline}."),
            ("Data Custodians", f"Documents shall be produced for the following custodians:\n" +
             "\n".join(f"  - {c}" for c in custodians)),
            ("Date Range", f"All responsive documents dated or created between {date_start} and {date_end}."),
            ("Document Categories Requested",
             "\n".join(f"  {j+1}. {cat}" for j, cat in enumerate(categories))),
            ("Preservation Notice", f"You are hereby notified of your obligation to preserve all documents, "
             f"communications, and electronically stored information (ESI) relevant to this matter. "
             f"Failure to preserve may result in sanctions including adverse inference instructions."),
            ("Special Instructions", f"All documents shall be produced in native format where possible. "
             f"Metadata must be preserved. Password-protected files must include passwords. "
             f"Privileged documents must be listed on a privilege log with sufficient detail."),
        ]
    )

print(f"Generated 15 subpoenas")

# ============================================================
# OUTSIDE COUNSEL INVOICES
# ============================================================
LAW_FIRMS = [
    "Morrison & Sterling LLP", "Blackwell Patterson PC", "Thornton Gray Associates",
    "Whitfield & Crane LLP", "Lancaster Brooks PC", "Harrington Cole LLP",
]
TIMEKEEPERS = {
    "Partner": (650, 1200),
    "Senior Associate": (400, 700),
    "Associate": (250, 500),
    "Paralegal": (150, 300),
}
TASK_DESCRIPTIONS = [
    "Review and analysis of discovery documents",
    "Prepare motion for summary judgment",
    "Attend deposition of {custodian}",
    "Draft correspondence to opposing counsel re: discovery dispute",
    "Legal research regarding applicable statute of limitations",
    "Prepare witness preparation materials",
    "Review and revise settlement agreement",
    "Conference call with client regarding case strategy",
    "Review documents for privilege; prepare privilege log entries",
    "Draft responses to interrogatories",
    "Attend court hearing on motion to compel",
    "Analyze regulatory compliance issues",
    "Review and comment on expert witness report",
    "Prepare filing for regulatory submission",
    "Multiple tasks: review docs, email to team, call with client, research precedent",
]

for i in range(15):
    firm = random.choice(LAW_FIRMS)
    matter = f"Matter {random.randint(10000,99999)}-{random.choice(['LIT','REG','COMP','M&A','IP'])}"
    client = random.choice(["National Financial Services Inc.", "Pacific Trust Bank", "Continental Holdings Corp."])
    invoice_num = f"INV-{random.randint(100000,999999)}"
    period_start = f"{random.choice(['January','February','March','April'])} 1, 2026"
    period_end = f"{random.choice(['January','February','March','April'])} {random.choice([28,30,31])}, 2026"

    line_items = []
    total = 0.0
    for _ in range(random.randint(8, 20)):
        role = random.choice(list(TIMEKEEPERS.keys()))
        rate_low, rate_high = TIMEKEEPERS[role]
        rate = random.randint(rate_low, rate_high)
        hours = round(random.uniform(0.5, 8.0), 1)
        amount = round(rate * hours, 2)
        total += amount
        desc = random.choice(TASK_DESCRIPTIONS).format(custodian=random.choice(CUSTODIANS))
        line_items.append(f"  {role} | {hours}h @ ${rate}/hr | ${amount:,.2f}\n    {desc}")

    expenses = []
    expense_total = 0.0
    for _ in range(random.randint(1, 4)):
        exp_type = random.choice(["Westlaw research charges", "Court filing fees", "Document production costs",
                                   "Expert witness fees", "Travel expenses", "Deposition transcript fees"])
        exp_amt = round(random.uniform(50, 5000), 2)
        expense_total += exp_amt
        expenses.append(f"  {exp_type}: ${exp_amt:,.2f}")

    make_pdf(os.path.join(tmpdir, f"invoice_{i:03d}.pdf"),
        f"LEGAL SERVICES INVOICE",
        [
            ("Invoice Details", f"Invoice #: {invoice_num}\nDate: March 15, 2026\n"
             f"Law Firm: {firm}\nClient: {client}\nMatter: {matter}\n"
             f"Billing Period: {period_start} - {period_end}"),
            ("Professional Services", "\n\n".join(line_items)),
            ("Professional Services Total", f"${total:,.2f}"),
            ("Expenses and Disbursements", "\n".join(expenses)),
            ("Expenses Total", f"${expense_total:,.2f}"),
            ("Invoice Total", f"${total + expense_total:,.2f}"),
            ("Payment Terms", f"Payment due within 30 days of invoice date. "
             f"Late payments subject to 1.5% monthly interest. "
             f"Please remit to: {firm}, Trust Account #{''.join([str(random.randint(0,9)) for _ in range(10)])}"),
            ("Billing Guidelines Compliance", f"This invoice has been prepared in accordance with "
             f"the Outside Counsel Billing Guidelines dated January 1, 2025. "
             f"All time entries reflect actual time spent. Block billing has been avoided "
             f"except where noted."),
        ]
    )

print(f"Generated 15 invoices")

# ============================================================
# REGULATORY FILINGS
# ============================================================
AGENCIES = [
    ("Securities and Exchange Commission", "SEC"),
    ("Consumer Financial Protection Bureau", "CFPB"),
    ("Office of the Comptroller of the Currency", "OCC"),
    ("Federal Reserve Board", "FRB"),
    ("Federal Deposit Insurance Corporation", "FDIC"),
]
REG_TYPES = [
    "Final Rule", "Proposed Rule", "Interpretive Release",
    "Enforcement Action", "Consent Order", "Supervisory Guidance",
]

for i in range(10):
    agency_name, agency_abbr = random.choice(AGENCIES)
    reg_type = random.choice(REG_TYPES)
    reg_id = f"{agency_abbr}-{random.randint(2025,2026)}-{random.randint(1000,9999)}"
    eff_date = f"{random.choice(['April','May','June','July'])} {random.randint(1,28)}, 2026"
    comment_deadline = f"{random.choice(['March','April'])} {random.randint(1,28)}, 2026" if "Proposed" in reg_type else None

    affected = random.sample([
        "National banks and federal savings associations",
        "State-chartered banks",
        "Bank holding companies with assets exceeding $10 billion",
        "Non-bank financial companies designated as systemically important",
        "Consumer lending institutions",
        "Mortgage servicers and originators",
        "Investment advisers and broker-dealers",
        "Digital asset service providers",
    ], random.randint(2, 4))

    requirements = random.sample([
        f"Institutions must implement enhanced risk management frameworks within {random.randint(6,18)} months of effective date",
        f"Annual stress testing required for institutions with assets exceeding ${random.randint(10,250)} billion",
        "Board-level oversight committee must be established with quarterly reporting requirements",
        "Third-party vendor risk assessments must be completed and documented annually",
        f"Capital reserves must be increased by {random.uniform(0.5, 3.0):.1f} percentage points for affected asset classes",
        "Consumer disclosure requirements updated to include plain-language summaries",
        "Anti-money laundering (AML) transaction monitoring thresholds reduced",
        "Climate-related financial risk disclosures required in annual reports",
        "Digital asset custody standards must meet specified security benchmarks",
        f"Civil money penalties up to ${random.randint(100000, 10000000):,} per violation per day",
    ], random.randint(3, 6))

    penalties = random.sample([
        f"Civil money penalties up to ${random.randint(100000, 10000000):,} per violation",
        "Cease and desist orders",
        "Removal and prohibition orders for responsible individuals",
        "Restitution to affected consumers",
        f"Disgorgement of profits up to ${random.randint(1000000, 50000000):,}",
    ], random.randint(2, 3))

    sections = [
        ("Issuing Agency", f"{agency_name} ({agency_abbr})"),
        ("Document Type", reg_type),
        ("Regulation ID", reg_id),
        ("Effective Date", eff_date),
        ("Affected Entities", "\n".join(f"  - {e}" for e in affected)),
        ("Summary", f"The {agency_name} is {'proposing' if 'Proposed' in reg_type else 'issuing'} "
         f"this {reg_type.lower()} to address emerging risks in the financial services sector. "
         f"This action is taken pursuant to the authority granted under "
         f"{random.choice(['the Dodd-Frank Wall Street Reform Act', 'the Bank Secrecy Act', 'the Securities Exchange Act of 1934', 'the Consumer Financial Protection Act'])}. "
         f"The {agency_abbr} has determined that current regulatory frameworks are insufficient to address "
         f"the identified risks and that additional requirements are necessary to protect "
         f"{'consumers' if agency_abbr in ['CFPB','FDIC'] else 'market integrity and financial stability'}."),
        ("Compliance Requirements", "\n".join(f"  {j+1}. {r}" for j, r in enumerate(requirements))),
        ("Penalties for Non-Compliance", "\n".join(f"  - {p}" for p in penalties)),
    ]
    if comment_deadline:
        sections.append(("Comment Period", f"Written comments must be received by {comment_deadline}. "
                        f"Comments may be submitted electronically via {agency_abbr.lower()}.gov/comments."))

    make_pdf(os.path.join(tmpdir, f"regulatory_{i:03d}.pdf"),
        f"{agency_abbr} {reg_type.upper()}: {reg_id}",
        sections
    )

print(f"Generated 10 regulatory filings")

# COMMAND ----------

# Upload all to volume
count = 0
for fname in sorted(os.listdir(tmpdir)):
    if fname.endswith('.pdf'):
        shutil.copy2(os.path.join(tmpdir, fname), f"{volume_path}/{fname}")
        count += 1

shutil.rmtree(tmpdir)
print(f"Uploaded {count} specialized documents to {volume_path}")
