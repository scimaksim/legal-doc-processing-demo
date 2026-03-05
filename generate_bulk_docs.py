"""Generate a large batch of legal documents to demonstrate scale."""
from fpdf import FPDF
import os
import random

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_docs_bulk")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COMPANIES = [
    "Apex Industries", "BlueStar Holdings", "Cascade Dynamics", "Delta Financial Group",
    "Evergreen Capital", "Falcon Technologies", "Granite Systems", "Horizon Ventures",
    "Ironclad Solutions", "Jupiter Analytics", "Keystone Partners", "Lighthouse Corp",
    "Meridian Health", "Nova Biotech", "Obsidian Energy", "Pinnacle Software",
    "Quantum Logistics", "Redwood Consulting", "Summit Robotics", "Titan Manufacturing",
    "Unified Networks", "Vertex Pharma", "Westfield Properties", "Xenon Labs",
    "Yellowstone Mining", "Zenith Aerospace", "Atlas Data Systems", "Beacon Finance",
    "Cobalt Engineering", "Drummond Legal",
]

STATES = ["Delaware", "California", "New York", "Texas", "Massachusetts",
          "Illinois", "Florida", "Washington", "Colorado", "Virginia"]

CITIES = {
    "Delaware": "Wilmington", "California": "San Francisco", "New York": "New York",
    "Texas": "Austin", "Massachusetts": "Boston", "Illinois": "Chicago",
    "Florida": "Miami", "Washington": "Seattle", "Colorado": "Denver",
    "Virginia": "Arlington",
}


def rand_amount(low, high):
    return f"${random.randint(low, high):,}.00"


def rand_date():
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    y = random.choice([2025, 2026])
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    return f"{months[m-1]} {d}, {y}"


def make_pdf(filename, title, sections):
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
    pdf.output(os.path.join(OUTPUT_DIR, filename))


templates = {
    "nda": lambda c1, c2, state, date: (
        f"MUTUAL NON-DISCLOSURE AGREEMENT - {c1} & {c2}",
        [
            ("Parties", f"This Mutual Non-Disclosure Agreement is entered into as of {date}, by and between "
             f"{c1}, a {state} corporation, and {c2}, a {random.choice(STATES)} limited liability company."),
            ("1. Confidential Information", f"\"Confidential Information\" means any non-public information disclosed by either party, including trade secrets, "
             f"inventions, source code, business plans, financial data valued at approximately {rand_amount(1000000, 50000000)}, "
             f"customer lists, and strategic plans. Information shall be marked \"Confidential\" or identified as such within {random.randint(5,30)} business days."),
            ("2. Obligations", f"The Receiving Party agrees to: (a) protect Confidential Information using at least {random.choice(['reasonable','commercially reasonable','the same degree of'])} care; "
             f"(b) limit disclosure to employees and contractors with need-to-know; (c) not reverse engineer any products or prototypes; "
             f"(d) maintain records of all individuals who access Confidential Information."),
            ("3. Term", f"This Agreement remains in effect for {random.choice([2,3,5])} years from the Effective Date. "
             f"Confidentiality obligations survive termination for {random.choice([3,5,7])} additional years."),
            ("4. Governing Law", f"Governed by the laws of the State of {state}. Disputes resolved in {CITIES[state]}, {state}."),
            ("Signatures", f"IN WITNESS WHEREOF:\n{c1}: _______________\n{c2}: _______________\nDate: {date}"),
        ]
    ),
    "license": lambda c1, c2, state, date: (
        f"SOFTWARE LICENSE AGREEMENT - {c1}",
        [
            ("Parties", f"Effective {date}, between {c1} (\"Licensor\") and {c2} (\"Licensee\"), "
             f"both organized under the laws of {state}."),
            ("1. Grant of License", f"Licensor grants Licensee a non-exclusive, non-transferable license to use "
             f"the \"{c1} Enterprise Platform\" on up to {random.randint(10,500)} designated workstations for internal business purposes."),
            ("2. Fees", f"Annual license fee: {rand_amount(50000, 1000000)}, payable in advance. "
             f"Late payments accrue interest at {random.choice(['1.0%','1.5%','2.0%'])} per month. "
             f"Support and maintenance: {rand_amount(10000, 200000)} per year."),
            ("3. Intellectual Property", f"All rights, title, and interest in the Software remain with Licensor. "
             f"Licensee shall not decompile, reverse engineer, or create derivative works. "
             f"Licensee acknowledges the Software contains trade secrets valued in excess of {rand_amount(5000000, 100000000)}."),
            ("4. Warranty", f"Licensor warrants the Software will perform substantially per documentation for {random.randint(60,180)} days. "
             f"EXCEPT AS STATED, SOFTWARE IS PROVIDED \"AS IS\". Maximum liability: {rand_amount(100000, 2000000)}."),
            ("5. Term", f"Initial term: {random.choice([1,2,3,5])} years. Auto-renews for {random.choice([1,2])} year periods unless "
             f"terminated with {random.randint(30,90)} days written notice."),
        ]
    ),
    "employment": lambda c1, c2, state, date: (
        f"EMPLOYMENT AGREEMENT - {c2}",
        [
            ("Parties", f"This Employment Agreement is entered into as of {date}, between {c1}, "
             f"a {state} corporation (\"Employer\"), and {c2} (\"Employee\")."),
            ("1. Position", f"Employee is hired as {random.choice(['Chief Technology Officer','VP of Engineering','General Counsel','Chief Financial Officer','SVP of Operations','Chief Data Officer'])}. "
             f"Employee shall report to the CEO and oversee a team of approximately {random.randint(10,200)} individuals."),
            ("2. Compensation", f"Base Salary: {rand_amount(200000, 600000)} per annum, paid bi-weekly.\n"
             f"Signing Bonus: {rand_amount(25000, 150000)}.\n"
             f"Annual Bonus: Up to {random.randint(15,40)}% of base salary based on performance.\n"
             f"Equity: {random.randint(10000, 100000)} stock options vesting over {random.choice([3,4])} years."),
            ("3. Benefits", f"Comprehensive health/dental/vision insurance; 401(k) with {random.randint(3,8)}% match; "
             f"{random.randint(15,30)} days PTO; professional development budget of {rand_amount(5000, 25000)}."),
            ("4. Restrictive Covenants", f"Non-compete: {random.randint(6,24)} months post-employment within {random.randint(25,100)}-mile radius.\n"
             f"Non-solicitation: {random.randint(12,24)} months.\nConfidentiality: Perpetual."),
            ("5. Termination", f"Either party may terminate with {random.randint(30,90)} days notice. "
             f"Severance upon termination without cause: {random.randint(6,18)} months base salary. "
             f"For-cause termination includes: material breach, conviction of felony, gross negligence."),
        ]
    ),
    "lease": lambda c1, c2, state, date: (
        f"COMMERCIAL LEASE AGREEMENT - {c2}",
        [
            ("Parties and Premises", f"Effective {date}, between {c1} (\"Landlord\") and {c2} (\"Tenant\"). "
             f"PREMISES: Suite {random.randint(100,9900)}, {random.randint(1,200)} {random.choice(['Main','Market','Commerce','Innovation','Tech'])} "
             f"{random.choice(['Street','Avenue','Boulevard','Drive'])}, {CITIES[state]}, {state}. "
             f"Approximately {random.randint(2000,50000)} square feet of rentable space."),
            ("1. Term", f"Initial term: {random.choice([3,5,7,10])} years commencing {date}. "
             f"Renewal options: {random.choice([1,2,3])} additional term(s) of {random.choice([3,5])} years each. "
             f"Notice required: {random.randint(6,18)} months prior to expiration."),
            ("2. Rent", f"Base Rent: {rand_amount(20, 150)} per square foot per annum.\n"
             f"Annual escalation: {random.choice(['2%','3%','CPI + 1%','3.5%'])} per year.\n"
             f"Additional Rent: Tenant's proportionate share ({random.uniform(0.5, 10):.1f}%) of operating expenses and taxes."),
            ("3. Security Deposit", f"Tenant shall deposit {rand_amount(50000, 1000000)} as security, "
             f"equivalent to {random.randint(3,12)} months' base rent."),
            ("4. Use", f"The Premises shall be used solely for {random.choice(['general office','research and development','technology operations','professional services','medical practice'])} purposes. "
             f"Tenant shall comply with all applicable laws and obtain necessary permits."),
            ("5. Maintenance", f"Landlord maintains structure, common areas, HVAC, and elevators. "
             f"Tenant maintains interior. Alterations exceeding {rand_amount(10000, 100000)} require Landlord consent."),
        ]
    ),
    "services": lambda c1, c2, state, date: (
        f"MASTER SERVICES AGREEMENT - {c1} & {c2}",
        [
            ("Parties", f"This Master Services Agreement is entered into as of {date}, by {c1} (\"Provider\") "
             f"and {c2} (\"Client\"), each organized under the laws of {state}."),
            ("1. Services", f"Provider shall deliver professional services as described in Statements of Work (SOWs). "
             f"Initial SOW covers: {random.choice(['cloud migration','data analytics platform','cybersecurity assessment','digital transformation','AI/ML implementation'])}. "
             f"Estimated initial project value: {rand_amount(100000, 5000000)}."),
            ("2. Fees and Payment", f"Time and materials at rates specified in each SOW. Standard rates range from "
             f"{rand_amount(150, 300)}/hour to {rand_amount(400, 800)}/hour depending on seniority. "
             f"Payment net {random.choice([30,45,60])} days. Late payment fee: {random.choice(['1.0%','1.5%'])} monthly."),
            ("3. Intellectual Property", f"All pre-existing IP remains with respective owners. "
             f"Work product created under SOWs shall be owned by {random.choice(['Client','Provider, with Client receiving a perpetual license'])}. "
             f"Provider retains rights to general knowledge, skills, and tools developed."),
            ("4. Liability", f"Provider's total liability shall not exceed {random.choice(['the fees paid in the prior 12 months','2x annual fees','$5,000,000'])}. "
             f"Neither party liable for indirect, consequential, or punitive damages. "
             f"Provider maintains {rand_amount(1000000, 10000000)} professional liability insurance."),
            ("5. Term and Termination", f"Initial term: {random.choice([1,2,3])} years, auto-renewing annually. "
             f"Either party may terminate with {random.randint(30,90)} days notice. "
             f"Client may terminate individual SOWs with {random.randint(15,30)} days notice plus payment for work completed."),
        ]
    ),
}

doc_num = 0
for i in range(50):
    template_name = random.choice(list(templates.keys()))
    c1, c2 = random.sample(COMPANIES, 2)
    state = random.choice(STATES)
    date = rand_date()
    title, sections = templates[template_name](c1, c2, state, date)
    fname = f"{template_name}_{doc_num:03d}_{c1.lower().replace(' ','_')}.pdf"
    make_pdf(fname, title, sections)
    doc_num += 1
    if (doc_num) % 10 == 0:
        print(f"  Generated {doc_num} documents...")

print(f"\nGenerated {doc_num} bulk legal documents in {OUTPUT_DIR}")
