# Databricks notebook source
# MAGIC %md
# MAGIC # Step 2: Generate and Upload Sample Legal Documents
# MAGIC Generates 55 sample legal PDFs (NDAs, licenses, employment agreements, leases, MSAs) and uploads them to the UC volume.

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
from fpdf import FPDF

COMPANIES = [
    "Acme Corporation", "TechVentures LLC", "DataFlow Systems", "Global Analytics Corp",
    "Pinnacle Health Systems", "Metropolitan Properties", "CloudFirst Technologies",
    "Apex Industries", "BlueStar Holdings", "Cascade Dynamics", "Delta Financial Group",
    "Evergreen Capital", "Falcon Technologies", "Granite Systems", "Horizon Ventures",
    "Ironclad Solutions", "Jupiter Analytics", "Keystone Partners", "Lighthouse Corp",
    "Meridian Health", "Nova Biotech", "Obsidian Energy", "Pinnacle Software",
    "Quantum Logistics", "Redwood Consulting", "Summit Robotics", "Titan Manufacturing",
    "Unified Networks", "Vertex Pharma", "Westfield Properties",
]

STATES = ["Delaware", "California", "New York", "Texas", "Massachusetts",
          "Illinois", "Florida", "Washington", "Colorado", "Virginia"]


def rand_amount(low, high):
    return f"${random.randint(low, high):,}.00"


def rand_date():
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    y = random.choice([2025, 2026])
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    return f"{months[m-1]} {d}, {y}"


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


templates = {
    "nda": lambda c1, c2, state, date: (
        f"MUTUAL NON-DISCLOSURE AGREEMENT - {c1} & {c2}",
        [
            ("Parties", f"This Mutual NDA is entered into as of {date}, by {c1} ({state}) and {c2}."),
            ("1. Confidential Information", f"Includes trade secrets, source code, business plans, financial data valued at approximately {rand_amount(1000000, 50000000)}, customer lists, and strategic plans."),
            ("2. Obligations", f"Receiving Party agrees to: (a) protect using {random.choice(['reasonable','commercially reasonable'])} care; (b) limit disclosure to need-to-know personnel; (c) not reverse engineer products."),
            ("3. Term", f"Effective for {random.choice([2,3,5])} years. Confidentiality survives termination for {random.choice([3,5,7])} additional years."),
            ("4. Governing Law", f"Governed by the laws of {state}."),
            ("Signatures", f"IN WITNESS WHEREOF:\n{c1}: _______________\n{c2}: _______________\nDate: {date}"),
        ]
    ),
    "license": lambda c1, c2, state, date: (
        f"SOFTWARE LICENSE AGREEMENT - {c1}",
        [
            ("Parties", f"Effective {date}, between {c1} (Licensor) and {c2} (Licensee), organized under {state} law."),
            ("1. Grant of License", f"Non-exclusive, non-transferable license for up to {random.randint(10,500)} workstations."),
            ("2. Fees", f"Annual license fee: {rand_amount(50000, 1000000)}. Support: {rand_amount(10000, 200000)}/year. Late fees: {random.choice(['1.0%','1.5%','2.0%'])}/month."),
            ("3. IP Rights", f"All rights remain with Licensor. Software contains trade secrets valued over {rand_amount(5000000, 100000000)}."),
            ("4. Warranty", f"Performs per documentation for {random.randint(60,180)} days. Max liability: {rand_amount(100000, 2000000)}."),
            ("5. Term", f"Initial term: {random.choice([1,2,3,5])} years. Auto-renews unless {random.randint(30,90)} days notice given."),
        ]
    ),
    "employment": lambda c1, c2, state, date: (
        f"EMPLOYMENT AGREEMENT - {c2} at {c1}",
        [
            ("Parties", f"Entered {date}, between {c1} ({state}) and {c2} (Employee)."),
            ("1. Position", f"Hired as {random.choice(['CTO','VP Engineering','General Counsel','CFO','SVP Operations','CDO'])}. Reports to CEO."),
            ("2. Compensation", f"Base: {rand_amount(200000, 600000)}/year. Signing bonus: {rand_amount(25000, 150000)}. Annual bonus: up to {random.randint(15,40)}%. Equity: {random.randint(10000, 100000)} options over {random.choice([3,4])} years."),
            ("3. Benefits", f"Health/dental/vision; 401(k) with {random.randint(3,8)}% match; {random.randint(15,30)} days PTO; {rand_amount(5000, 25000)} professional development."),
            ("4. Restrictive Covenants", f"Non-compete: {random.randint(6,24)} months, {random.randint(25,100)}-mile radius. Non-solicitation: {random.randint(12,24)} months."),
            ("5. Termination", f"Either party with {random.randint(30,90)} days notice. Severance: {random.randint(6,18)} months base salary."),
        ]
    ),
    "lease": lambda c1, c2, state, date: (
        f"COMMERCIAL LEASE - {c2}",
        [
            ("Parties", f"Effective {date}, between {c1} (Landlord) and {c2} (Tenant). Premises: {random.randint(2000,50000)} sq ft in {state}."),
            ("1. Term", f"Initial: {random.choice([3,5,7,10])} years. Renewal: {random.choice([1,2,3])} options of {random.choice([3,5])} years each."),
            ("2. Rent", f"Base: {rand_amount(20, 150)}/sq ft/year. Annual escalation: {random.choice(['2%','3%','CPI+1%'])}. Tenant share of operating expenses: {random.uniform(0.5, 10):.1f}%."),
            ("3. Security Deposit", f"Deposit: {rand_amount(50000, 1000000)} ({random.randint(3,12)} months' rent)."),
            ("4. Use", f"Solely for {random.choice(['general office','R&D','technology operations','professional services'])} purposes."),
            ("5. Maintenance", f"Landlord: structure, HVAC, elevators. Tenant: interior. Alterations over {rand_amount(10000, 100000)} require consent."),
        ]
    ),
    "services": lambda c1, c2, state, date: (
        f"MASTER SERVICES AGREEMENT - {c1} & {c2}",
        [
            ("Parties", f"Entered {date}, by {c1} (Provider) and {c2} (Client), both under {state} law."),
            ("1. Services", f"Professional services per SOWs. Initial: {random.choice(['cloud migration','data analytics','cybersecurity','digital transformation','AI/ML'])}. Value: {rand_amount(100000, 5000000)}."),
            ("2. Fees", f"T&M rates: {rand_amount(150, 300)}-{rand_amount(400, 800)}/hour. Payment net {random.choice([30,45,60])} days."),
            ("3. IP", f"Pre-existing IP stays with owner. Work product owned by {random.choice(['Client','Provider with perpetual license to Client'])}."),
            ("4. Liability", f"Capped at {random.choice(['12 months fees','2x annual fees','$5,000,000'])}. {rand_amount(1000000, 10000000)} professional liability insurance."),
            ("5. Term", f"Initial: {random.choice([1,2,3])} years, auto-renewing. Terminate with {random.randint(30,90)} days notice."),
        ]
    ),
}

# Generate documents
tmpdir = tempfile.mkdtemp()
doc_count = 0

# 5 original detailed documents
original_docs = [
    ("nda_agreement.pdf", "MUTUAL NON-DISCLOSURE AGREEMENT", [
        ("Parties", "This Mutual NDA is entered into as of January 15, 2026, by Acme Corporation (Delaware) and TechVentures LLC (California)."),
        ("1. Confidential Information", "Includes trade secrets, inventions, source code, business plans, financial statements, customer lists, and employee compensation data."),
        ("2. Obligations", "Receiving Party shall: (a) hold in strict confidence; (b) not disclose to third parties; (c) not use beyond the Purpose; (d) protect with no less than reasonable care."),
        ("3. Term", "3 years from Effective Date. Confidentiality survives for 5 years after termination."),
        ("4. Governing Law", "California law. Disputes in San Francisco County courts."),
        ("Signatures", "Acme Corporation: John Smith, CEO\nTechVentures LLC: Sarah Johnson, Managing Partner\nDate: January 15, 2026"),
    ]),
    ("software_license.pdf", "SOFTWARE LICENSE AGREEMENT", [
        ("Parties", "Effective February 1, 2026, between DataFlow Systems Inc. (Delaware) and Global Analytics Corp. (New York)."),
        ("1. Grant", "Non-exclusive, non-transferable license for up to 50 workstations for internal use."),
        ("2. Fees", "Annual: $250,000.00. Late fees: 1.5%/month."),
        ("3. IP", "All rights remain with Licensor. Software contains proprietary trade secrets."),
        ("4. Warranty", "90 days. Provided AS IS thereafter. Max liability: 12 months fees paid."),
        ("5. Term", "3 years. Terminate with 60 days notice for material breach (30-day cure)."),
    ]),
    ("employment_agreement.pdf", "EMPLOYMENT AGREEMENT", [
        ("Parties", "Effective March 1, 2026, between Pinnacle Health Systems (Massachusetts) and Dr. Emily Chen."),
        ("1. Position", "Chief Medical Information Officer. Reports to CEO. Oversees EHR systems and clinical informatics."),
        ("2. Compensation", "Base: $425,000/year. Signing: $75,000. Bonus: up to 30%. Dev budget: $15,000/year."),
        ("3. Benefits", "Health/dental/vision; 401(k) 6% match; 4 weeks PTO; license renewal paid."),
        ("4. Restrictive Covenants", "Non-compete: 12 months, 50-mile radius. Non-solicitation: 12 months."),
        ("5. Termination", "90 days notice. Severance: 12 months base salary without cause."),
    ]),
    ("commercial_lease.pdf", "COMMERCIAL LEASE AGREEMENT", [
        ("Parties", "Effective January 1, 2026. Landlord: Metropolitan Properties Group LLC. Tenant: Quantum Computing Solutions Inc. Premises: Suite 4200, One World Trade Center, 12,500 sq ft."),
        ("1. Term", "10 years (April 2026 - March 2036). Two 5-year renewal options."),
        ("2. Rent", "Years 1-3: $78/sqft ($81,250/mo). Years 4-6: $84/sqft. Years 7-10: $90/sqft. Tenant share: 2.3% operating expenses."),
        ("3. Security", "$487,500 (6 months' rent)."),
        ("4. Use", "General office, computer R&D, software engineering."),
        ("5. Maintenance", "Landlord: structure, HVAC, elevators. Tenant: interior. Alterations over $25,000 need consent."),
    ]),
    ("merger_agreement.pdf", "AGREEMENT AND PLAN OF MERGER", [
        ("Parties", "December 15, 2025. Acquiror: CloudFirst Technologies. Merger Sub: CF Merger Sub. Target: NexGen Data Platforms."),
        ("Article I", "Merger Sub merges into Company. Company survives under Delaware law."),
        ("Article II", "Consideration: $47.50/share (35% premium). Total: ~$3,200,000,000. Options cashed out."),
        ("Article III", "Company reps: duly organized, authorized, financials accurate, no MAE, IP owned/licensed, no material litigation."),
        ("Article IV", "Conditions: stockholder approval, no restraint, HSR clearance, SEC review. Termination fee: $96,000,000."),
        ("Article V", "Delaware law. Entire agreement. Amendment requires written consent. Closing by June 30, 2026."),
    ]),
]

for fname, title, sections in original_docs:
    make_pdf(os.path.join(tmpdir, fname), title, sections)
    doc_count += 1

# 50 generated documents
random.seed(42)
for i in range(50):
    template_name = random.choice(list(templates.keys()))
    c1, c2 = random.sample(COMPANIES, 2)
    state = random.choice(STATES)
    date = rand_date()
    title, sections = templates[template_name](c1, c2, state, date)
    fname = f"{template_name}_{i:03d}_{c1.lower().replace(' ','_')}.pdf"
    make_pdf(os.path.join(tmpdir, fname), title, sections)
    doc_count += 1

print(f"Generated {doc_count} documents")

# COMMAND ----------

# Upload all PDFs to the volume
import shutil

for fname in os.listdir(tmpdir):
    if fname.endswith('.pdf'):
        src = os.path.join(tmpdir, fname)
        dst = f"{volume_path}/{fname}"
        shutil.copy2(src, dst)

shutil.rmtree(tmpdir)
print(f"Uploaded {doc_count} documents to {volume_path}")

# COMMAND ----------

# Verify
files = dbutils.fs.ls(f"dbfs:{volume_path}")
print(f"Volume contains {len(files)} files")
for f in files[:5]:
    print(f"  {f.name} ({f.size:,} bytes)")
print(f"  ... and {len(files)-5} more")
