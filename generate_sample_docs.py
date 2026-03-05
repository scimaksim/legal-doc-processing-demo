"""Generate sample legal documents as PDFs for the demo."""
from fpdf import FPDF
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def make_pdf(filename: str, title: str, sections: list[tuple[str, str]]):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, title, ln=True, align="C")
    pdf.ln(8)
    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, heading, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, body)
        pdf.ln(4)
    pdf.output(os.path.join(OUTPUT_DIR, filename))
    print(f"  Created {filename}")


# --- 1. Non-Disclosure Agreement ---
make_pdf("nda_agreement.pdf", "MUTUAL NON-DISCLOSURE AGREEMENT", [
    ("Parties",
     "This Mutual Non-Disclosure Agreement (\"Agreement\") is entered into as of January 15, 2026, "
     "by and between Acme Corporation, a Delaware corporation with its principal offices at "
     "123 Innovation Drive, San Francisco, CA 94105 (\"Disclosing Party\"), and TechVentures LLC, "
     "a California limited liability company with its principal offices at 456 Market Street, "
     "San Francisco, CA 94107 (\"Receiving Party\")."),
    ("1. Definition of Confidential Information",
     "\"Confidential Information\" means any and all non-public information, including but not limited to: "
     "(a) trade secrets, inventions, ideas, processes, formulas, source and object codes, data, programs, "
     "software, and other works of authorship; (b) information regarding plans for research, development, "
     "new products, marketing, and selling; (c) business plans, budgets, financial statements, contracts, "
     "prices, suppliers, and customers; (d) information regarding the skills and compensation of employees, "
     "contractors, and any other service providers of the Disclosing Party."),
    ("2. Obligations of Receiving Party",
     "The Receiving Party agrees to: (a) hold the Confidential Information in strict confidence; "
     "(b) not to disclose the Confidential Information to any third parties without prior written consent; "
     "(c) not to use the Confidential Information for any purpose other than the Purpose; "
     "(d) to protect the Confidential Information using the same degree of care it uses to protect its own "
     "confidential information, but in no event less than reasonable care."),
    ("3. Term and Termination",
     "This Agreement shall remain in effect for a period of three (3) years from the Effective Date. "
     "The obligations of confidentiality shall survive termination of this Agreement for a period of "
     "five (5) years following such termination."),
    ("4. Governing Law",
     "This Agreement shall be governed by and construed in accordance with the laws of the State of "
     "California, without regard to its conflict of laws principles. Any disputes arising under this "
     "Agreement shall be resolved in the state or federal courts located in San Francisco County, California."),
    ("Signatures",
     "IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.\n\n"
     "Acme Corporation                    TechVentures LLC\n"
     "By: _________________________       By: _________________________\n"
     "Name: John Smith                    Name: Sarah Johnson\n"
     "Title: Chief Executive Officer      Title: Managing Partner\n"
     "Date: January 15, 2026              Date: January 15, 2026"),
])

# --- 2. Software License Agreement ---
make_pdf("software_license.pdf", "SOFTWARE LICENSE AGREEMENT", [
    ("Parties and Recitals",
     "This Software License Agreement (\"Agreement\") is made effective as of February 1, 2026, "
     "by and between DataFlow Systems Inc., a Delaware corporation (\"Licensor\"), and Global Analytics Corp., "
     "a New York corporation (\"Licensee\").\n\n"
     "WHEREAS, Licensor owns certain proprietary software known as \"DataFlow Enterprise Suite\" "
     "(the \"Software\"); and WHEREAS, Licensee desires to obtain a license to use the Software "
     "in accordance with the terms and conditions set forth herein."),
    ("1. Grant of License",
     "Subject to the terms of this Agreement, Licensor hereby grants to Licensee a non-exclusive, "
     "non-transferable, limited license to install and use the Software on up to fifty (50) designated "
     "workstations within Licensee's organization solely for Licensee's internal business purposes."),
    ("2. License Fee and Payment Terms",
     "Licensee shall pay Licensor an annual license fee of Two Hundred Fifty Thousand Dollars ($250,000.00), "
     "payable in advance on the first day of each license year. Late payments shall accrue interest at a rate "
     "of 1.5% per month or the maximum rate permitted by law, whichever is less."),
    ("3. Intellectual Property Rights",
     "The Software and all copies thereof are proprietary to Licensor and title thereto remains in Licensor. "
     "All applicable rights to patents, copyrights, trademarks, and trade secrets in the Software are and "
     "shall remain in Licensor. Licensee shall not remove, obscure, or alter any proprietary notices on "
     "the Software."),
    ("4. Warranty and Limitation of Liability",
     "LICENSOR WARRANTS THAT THE SOFTWARE WILL PERFORM SUBSTANTIALLY IN ACCORDANCE WITH THE DOCUMENTATION "
     "FOR A PERIOD OF NINETY (90) DAYS FROM THE DATE OF DELIVERY. EXCEPT AS EXPRESSLY SET FORTH HEREIN, "
     "THE SOFTWARE IS PROVIDED \"AS IS\" WITHOUT WARRANTY OF ANY KIND. IN NO EVENT SHALL LICENSOR'S TOTAL "
     "LIABILITY EXCEED THE AMOUNT OF LICENSE FEES PAID BY LICENSEE IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM."),
    ("5. Term and Termination",
     "This Agreement shall commence on the Effective Date and continue for an initial term of three (3) years. "
     "Either party may terminate this Agreement upon sixty (60) days' written notice if the other party "
     "materially breaches any provision of this Agreement and fails to cure such breach within thirty (30) days."),
])

# --- 3. Employment Agreement ---
make_pdf("employment_agreement.pdf", "EMPLOYMENT AGREEMENT", [
    ("Parties",
     "This Employment Agreement (\"Agreement\") is entered into as of March 1, 2026, by and between "
     "Pinnacle Health Systems, Inc., a Massachusetts corporation with headquarters at 789 Medical Center Drive, "
     "Boston, MA 02115 (\"Employer\"), and Dr. Emily Chen, an individual residing at 321 Beacon Street, "
     "Boston, MA 02116 (\"Employee\")."),
    ("1. Position and Duties",
     "Employer hereby employs Employee as Chief Medical Information Officer (CMIO). Employee shall report "
     "directly to the Chief Executive Officer and shall be responsible for: (a) overseeing the implementation "
     "and optimization of electronic health record systems; (b) leading the clinical informatics department; "
     "(c) developing data-driven clinical decision support tools; (d) ensuring compliance with HIPAA and "
     "other healthcare regulations regarding health information technology."),
    ("2. Compensation",
     "Base Salary: Employee shall receive an annual base salary of Four Hundred Twenty-Five Thousand Dollars "
     "($425,000.00), payable in bi-weekly installments.\n"
     "Signing Bonus: Employee shall receive a one-time signing bonus of Seventy-Five Thousand Dollars "
     "($75,000.00), payable within thirty (30) days of the Effective Date.\n"
     "Annual Bonus: Employee shall be eligible for an annual performance bonus of up to 30% of base salary, "
     "based on achievement of mutually agreed-upon performance objectives."),
    ("3. Benefits",
     "Employee shall be entitled to: (a) comprehensive health, dental, and vision insurance; "
     "(b) 401(k) retirement plan with employer matching up to 6%; (c) four (4) weeks of paid vacation annually; "
     "(d) professional development allowance of $15,000 per year; (e) medical license renewal and board "
     "certification fees paid by Employer."),
    ("4. Non-Compete and Non-Solicitation",
     "For a period of twelve (12) months following termination of employment, Employee agrees not to: "
     "(a) engage in any competing business within a 50-mile radius of Employer's facilities; "
     "(b) solicit or recruit any employees of Employer; (c) solicit any patients or clients of Employer. "
     "Employee acknowledges that the restrictions in this Section are reasonable and necessary to protect "
     "Employer's legitimate business interests."),
    ("5. Termination",
     "Either party may terminate this Agreement at any time with ninety (90) days' written notice. "
     "Employer may terminate for Cause, defined as: (a) material breach of this Agreement; "
     "(b) conviction of a felony; (c) gross negligence or willful misconduct; (d) loss of medical license. "
     "Upon termination without Cause, Employee shall receive twelve (12) months of base salary as severance."),
])

# --- 4. Commercial Lease Agreement ---
make_pdf("commercial_lease.pdf", "COMMERCIAL LEASE AGREEMENT", [
    ("Parties and Premises",
     "This Commercial Lease Agreement (\"Lease\") is entered into as of January 1, 2026, by and between "
     "Metropolitan Properties Group LLC, a New York limited liability company (\"Landlord\"), and "
     "Quantum Computing Solutions Inc., a Delaware corporation (\"Tenant\").\n\n"
     "PREMISES: Suite 4200, One World Trade Center, 285 Fulton Street, New York, NY 10007, consisting of "
     "approximately 12,500 square feet of rentable office space on the 42nd floor (the \"Premises\")."),
    ("1. Term",
     "The initial lease term shall be ten (10) years, commencing on April 1, 2026, and expiring on "
     "March 31, 2036 (the \"Initial Term\"). Tenant shall have two (2) options to renew for additional "
     "periods of five (5) years each, upon written notice given no less than twelve (12) months prior "
     "to expiration of the then-current term."),
    ("2. Rent",
     "Base Rent: Tenant shall pay monthly base rent as follows:\n"
     "Years 1-3: $78.00 per square foot per annum ($81,250.00/month)\n"
     "Years 4-6: $84.00 per square foot per annum ($87,500.00/month)\n"
     "Years 7-10: $90.00 per square foot per annum ($93,750.00/month)\n\n"
     "Additional Rent: Tenant shall pay its proportionate share (2.3%) of operating expenses, "
     "real estate taxes, and insurance costs in excess of base year amounts."),
    ("3. Security Deposit",
     "Tenant shall deposit with Landlord the sum of Four Hundred Eighty-Seven Thousand Five Hundred Dollars "
     "($487,500.00), equivalent to six (6) months' base rent, as security for the faithful performance "
     "of Tenant's obligations under this Lease."),
    ("4. Use and Compliance",
     "The Premises shall be used solely for general office purposes, including computer research and "
     "development, software engineering, and related administrative functions. Tenant shall comply with "
     "all applicable federal, state, and local laws, codes, ordinances, and regulations."),
    ("5. Maintenance and Alterations",
     "Landlord shall maintain the building structure, common areas, HVAC systems, and elevators. "
     "Tenant shall maintain the interior of the Premises in good condition. Any alterations exceeding "
     "Twenty-Five Thousand Dollars ($25,000.00) shall require Landlord's prior written consent."),
])

# --- 5. Merger Agreement (multi-page) ---
make_pdf("merger_agreement.pdf", "AGREEMENT AND PLAN OF MERGER", [
    ("Parties and Recitals",
     "This Agreement and Plan of Merger (\"Agreement\") is entered into as of December 15, 2025, by and among "
     "CloudFirst Technologies, Inc., a Delaware corporation (\"Acquiror\"), CF Merger Sub, Inc., a Delaware "
     "corporation and wholly-owned subsidiary of Acquiror (\"Merger Sub\"), and NexGen Data Platforms, Inc., "
     "a Delaware corporation (\"Target\" or the \"Company\").\n\n"
     "WHEREAS, the Boards of Directors of Acquiror, Merger Sub, and the Company have each determined that "
     "it is in the best interests of their respective stockholders to consummate the merger of Merger Sub "
     "with and into the Company on the terms and conditions set forth herein."),
    ("Article I - The Merger",
     "1.1 The Merger. Upon the terms and subject to the conditions set forth in this Agreement, at the "
     "Effective Time, Merger Sub shall be merged with and into the Company. The Company shall be the "
     "surviving corporation (the \"Surviving Corporation\") and shall continue its corporate existence "
     "under the laws of the State of Delaware.\n\n"
     "1.2 Effective Time. The Merger shall become effective upon the filing of a Certificate of Merger "
     "with the Secretary of State of the State of Delaware."),
    ("Article II - Merger Consideration",
     "2.1 Conversion of Shares. At the Effective Time, each share of Company Common Stock issued and "
     "outstanding immediately prior to the Effective Time shall be converted into the right to receive "
     "$47.50 per share in cash (the \"Merger Consideration\"), representing a premium of approximately "
     "35% over the Company's 30-day volume-weighted average trading price.\n\n"
     "2.2 Treatment of Options. Each outstanding option to purchase shares of Company Common Stock shall "
     "be converted into the right to receive an amount in cash equal to the excess, if any, of the "
     "Merger Consideration over the exercise price of such option.\n\n"
     "2.3 Total Transaction Value. The aggregate Merger Consideration is estimated to be approximately "
     "Three Billion Two Hundred Million Dollars ($3,200,000,000.00)."),
    ("Article III - Representations and Warranties of the Company",
     "The Company represents and warrants to Acquiror and Merger Sub as follows:\n"
     "3.1 Organization: The Company is duly organized and validly existing under Delaware law.\n"
     "3.2 Authorization: The execution and delivery of this Agreement has been duly authorized.\n"
     "3.3 Financial Statements: The Company's financial statements fairly present its financial condition.\n"
     "3.4 No Material Adverse Effect: Since the date of the most recent balance sheet, there has been no "
     "Material Adverse Effect on the Company.\n"
     "3.5 Intellectual Property: The Company owns or has valid licenses to all intellectual property "
     "material to its business.\n"
     "3.6 Litigation: There is no pending litigation that would reasonably be expected to have a "
     "Material Adverse Effect."),
    ("Article IV - Conditions to Closing",
     "4.1 Mutual Conditions: (a) Stockholder approval of both companies; (b) No governmental restraint "
     "prohibiting the Merger; (c) HSR Act waiting period expired or terminated; (d) SEC review completed.\n\n"
     "4.2 Conditions to Acquiror's Obligations: (a) Accuracy of Company's representations; "
     "(b) Company's compliance with covenants; (c) No Material Adverse Effect.\n\n"
     "4.3 Termination Fee: If the Company terminates this Agreement to accept a Superior Proposal, "
     "the Company shall pay Acquiror a termination fee of Ninety-Six Million Dollars ($96,000,000.00)."),
    ("Article V - Miscellaneous",
     "5.1 Governing Law: This Agreement shall be governed by the laws of the State of Delaware.\n"
     "5.2 Entire Agreement: This Agreement constitutes the entire agreement between the parties.\n"
     "5.3 Amendment: This Agreement may be amended only by written instrument signed by all parties.\n"
     "5.4 Expenses: Each party shall bear its own expenses in connection with this Agreement.\n"
     "5.5 Closing Date: The closing of the Merger shall take place no later than June 30, 2026."),
])

print("\nAll sample legal documents generated successfully!")
