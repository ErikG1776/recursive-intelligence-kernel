#!/usr/bin/env python3
"""
Download real government PDF documents for RIK demo testing.

These are publicly available documents from government sources.
"""

import os
import urllib.request
import ssl

# Real government PDFs from official .gov sources
GOV_PDF_SOURCES = [
    # GSA Forms (General Services Administration)
    {
        "name": "SF1449_Solicitation_Contract.pdf",
        "url": "https://www.gsa.gov/system/files/SF1449-21.pdf",
        "description": "Federal Solicitation/Contract/Order Form"
    },
    {
        "name": "GSA_Form_300.pdf",
        "url": "https://www.gsa.gov/system/files/GSA300-7.pdf",
        "description": "GSA Order for Supplies or Services"
    },
    {
        "name": "SF1034_Public_Voucher.pdf",
        "url": "https://www.gsa.gov/system/files/SF%201034%20-%20Public%20Voucher%20for%20Purchases%20and%20Services%20Other%20Than%20Personal%20-%20Renewed%20-%202020-02-28.pdf",
        "description": "Standard Form 1034 - Public Voucher"
    },
    {
        "name": "SF1035_Continuation.pdf",
        "url": "https://www.gsa.gov/system/files/SF%201035%20-%20Public%20Voucher%20for%20Purchases%20and%20Services%20Other%20Than%20Personal%20%28Cont.%20Sheet%29%20-%20Renewed%20-%202020-02-28.pdf",
        "description": "Standard Form 1035 - Continuation Sheet"
    },
    # IRS Forms
    {
        "name": "IRS_W9_Vendor.pdf",
        "url": "https://www.irs.gov/pub/irs-pdf/fw9.pdf",
        "description": "IRS W-9 Request for Taxpayer ID (vendor onboarding)"
    },
    # Department of Labor
    {
        "name": "DOL_WH347_Payroll.pdf",
        "url": "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh347.pdf",
        "description": "DOL Certified Payroll Form"
    },
    # CMS Medicare
    {
        "name": "CMS1500_Claim.pdf",
        "url": "https://www.cms.gov/Medicare/CMS-Forms/CMS-Forms/Downloads/CMS1500.pdf",
        "description": "CMS-1500 Health Insurance Claim Form"
    },
    # Small Business Administration
    {
        "name": "SBA_Disaster_Loan.pdf",
        "url": "https://www.sba.gov/sites/default/files/2022-11/Disaster%20Home%20and%20Sole%20Proprietor%20Loan%20Application%20SBA%20Form%205C%20-%20508.pdf",
        "description": "SBA Disaster Loan Application"
    },
    # Federal Transit Administration
    {
        "name": "FTA_Budget_Form.pdf",
        "url": "https://www.transit.dot.gov/sites/fta.dot.gov/files/2021-03/FTA-Operating-Budget-Detail-Form.pdf",
        "description": "FTA Operating Budget Detail Form"
    },
]

# Alternative: Create realistic government-style invoice PDFs
def create_realistic_gov_invoices():
    """Create realistic government-style invoice text files for demo."""

    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sample_pdfs")
    os.makedirs(output_dir, exist_ok=True)

    # Based on real federal contract patterns from USASpending data
    invoices = [
        {
            "filename": "boeing_defense_invoice.txt",
            "content": """
INVOICE

Boeing Company
100 N Riverside Plaza
Chicago, IL 60606

Invoice Number: BA-2024-78234
Invoice Date: November 15, 2024
Due Date: December 15, 2024

Bill To:
Department of Defense
Defense Logistics Agency
8725 John J Kingman Rd
Fort Belvoir, VA 22060

Contract Number: W52P1J-20-D-0015
PO Number: PO-DOD-2024-45123
DUNS: 026501657

Description of Services/Goods:
Aircraft maintenance parts and support services
Period: October 1, 2024 - October 31, 2024

Line Items:
1. F-15 Engine Components (Qty: 12)      $892,400.00
2. Avionics Repair Services              $234,500.00
3. Technical Documentation               $ 45,000.00
4. Shipping and Handling                 $ 12,890.00

                          Subtotal:    $1,184,790.00
                          Tax:         $        0.00

                          TOTAL DUE:   $1,184,790.00

Payment Terms: Net 30
Remit Payment To: Boeing Company, Account #4478-2234-8891

Authorized Signature: _________________
Date: November 15, 2024
"""
        },
        {
            "filename": "lockheed_martin_invoice.txt",
            "content": """
COMMERCIAL INVOICE

LOCKHEED MARTIN CORPORATION
6801 Rockledge Drive
Bethesda, MD 20817
Federal Tax ID: 52-1893632

                                    Invoice #: LM-FY24-92841
                                    Date: November 8, 2024
                                    Page: 1 of 1

SOLD TO:                            SHIP TO:
U.S. Army Contracting Command       U.S. Army Depot
ATTN: Accounts Payable              Anniston Army Depot
4505 Martin Way                     7 Frankford Ave
Redstone Arsenal, AL 35898          Anniston, AL 36201

Contract: W58RGZ-19-C-0032
Delivery Order: 0047
Requisition: W25G1V-4123-M4R7

ITEM    NSN                 DESCRIPTION                 QTY    UNIT PRICE    AMOUNT
----    ---                 -----------                 ---    ----------    ------
001     1560-01-234-5678    Helicopter Rotor Assembly    2     $156,780.00   $313,560.00
002     1680-01-456-7890    Flight Control Unit          5     $ 23,450.00   $117,250.00
003     5999-01-789-0123    Wiring Harness Kit          10     $  4,567.00   $ 45,670.00

                                                    SUBTOTAL:    $476,480.00
                                                    FREIGHT:     $  3,200.00

                                                    TOTAL:       $479,680.00

PAYMENT TERMS: NET 30 DAYS
CAGE CODE: 64059

Certify that the items listed were received in good condition.

_______________________          _______________________
Contractor Representative        Government Inspector
"""
        },
        {
            "filename": "vertex_aerospace_invoice.txt",
            "content": """
INVOICE FOR SERVICES RENDERED

VERTEX AEROSPACE LLC
1205 N West Shore Blvd
Madison, MS 39110
Phone: (601) 607-6100

Invoice No: VA-INV-2024-3847
Invoice Date: 11/12/2024
Customer Account: DOD-USA-4421

Bill To:
Department of the Army
US Army Aviation Center
Bldg 5700, Room 234
Fort Novosel, AL 36362

Reference:
  Contract Number: W58RGZ-21-D-0024
  Task Order: 0018
  Period of Performance: 01 Oct 2024 - 31 Oct 2024

Services Provided - Aircraft Maintenance Support:

Description                                          Amount
-----------                                          ------
UH-60 Black Hawk Maintenance Labor (2,400 hrs)      $312,000.00
AH-64 Apache Inspection Services (180 hrs)          $ 45,000.00
Parts and Materials (see attached list)             $ 89,234.00
Travel and Per Diem                                 $  8,456.00
Quality Assurance Documentation                     $  4,200.00

                                    TOTAL INVOICE:  $458,890.00

IMPORTANT: Missing Purchase Order
NOTE: PO documentation not yet received from contracting office.
Please provide PO number for payment processing.

Wire Transfer Information:
Bank: Regions Bank
Account: 0062847291
Routing: 065403626

Contact: invoices@vertexaero.com
"""
        },
        {
            "filename": "gdit_it_services_invoice.txt",
            "content": """
                    GENERAL DYNAMICS INFORMATION TECHNOLOGY
                    3211 Jermantown Road, Fairfax, VA 22030

==============================================================================
                              INVOICE
==============================================================================

Invoice Number:     GDIT-2024-INV-44521
Invoice Date:       November 18, 2024
Contract Number:    GS-35F-0511T
Task Order:         47QTCA23D00YZ

Customer:
  Department of Homeland Security
  Office of the Chief Information Officer
  245 Murray Lane SW
  Washington, DC 20528

  Attn: Accounts Payable - OCIO

Project: Enterprise IT Modernization Support
CLIN 0001 - IT Professional Services

Labor Category                  Hours    Rate        Amount
------------------------------- -----    ----        ------
Senior Systems Engineer           160    $185.00     $29,600.00
Cloud Architect                   120    $210.00     $25,200.00
Cybersecurity Analyst             200    $165.00     $33,000.00
Database Administrator             80    $155.00     $12,400.00
Project Manager                    40    $175.00     $ 7,000.00

                                      Labor Total:  $107,200.00

Other Direct Costs:
  - Software Licenses (AWS, Azure)                  $ 34,500.00
  - Security Scanning Tools                         $  8,900.00

                                        ODC Total:  $ 43,400.00

                                   INVOICE TOTAL:   $150,600.00

Payment Due: December 18, 2024 (Net 30)
Purchase Order: DHS-OCIO-2024-8834

Remittance: GDIT-AP@gd.com
Questions: (703) 246-0200

==============================================================================
"""
        },
        {
            "filename": "raytheon_munitions_invoice.txt",
            "content": """
RTX CORPORATION (formerly Raytheon)
1100 Wilson Boulevard
Arlington, VA 22209

TAX INVOICE

Invoice #: RTX-MIS-2024-7823
Date: November 10, 2024

Billed To:
  Naval Sea Systems Command (NAVSEA)
  Accounts Payable Division
  1333 Isaac Hull Ave SE
  Washington Navy Yard, DC 20376

Ship To:
  Naval Weapons Station Seal Beach
  800 Seal Beach Blvd
  Seal Beach, CA 90740

Contract: N00024-22-C-5312
PR Number: N4523A-24-M-8912
Delivery Order: N00024-22-C-5312-0034

Items Delivered:

Part Number      Description              Qty    Unit Cost      Total
-----------      -----------              ---    ---------      -----
RTX-SM6-BLK2     SM-6 Missile Components   4    $987,500.00    $3,950,000.00
RTX-GWS-15A      Guidance System Units     8    $123,400.00    $  987,200.00
RTX-SUP-KIT-C    Support Equipment Kit     2    $ 45,670.00    $   91,340.00

                                        Subtotal:  $5,028,540.00
                                        Freight:   $   12,400.00

                                        TOTAL:     $5,040,940.00

CAGE: 14214
DUNS: 089aboratory268442

Terms: Net 30
FOB: Destination
"""
        },
        {
            "filename": "missing_po_invoice.txt",
            "content": """
ACME FEDERAL CONTRACTORS LLC
456 Government Way, Suite 200
Arlington, VA 22201

INVOICE

Date: November 19, 2024
Invoice No.: AFC-2024-1156

TO:
  Environmental Protection Agency
  Office of Administration
  1200 Pennsylvania Ave NW
  Washington, DC 20460

CONTRACT: EP-W-17-D-0045
TASK ORDER: 0089

Description: Environmental Consulting Services
  - Site Assessment Report - Region 3 Facility
  - Soil Sample Analysis (48 samples)
  - Groundwater Monitoring Report
  - Remediation Recommendations

Period: October 2024

Professional Services:         $34,500.00
Laboratory Analysis:          $12,890.00
Report Preparation:           $ 5,600.00
Travel (Philadelphia site):   $ 2,340.00

TOTAL AMOUNT DUE:             $55,330.00

*** URGENT: NO PURCHASE ORDER ON FILE ***
Please provide PO number to process this invoice.
Prior invoices reference PO EPA-2024-7812 but we have not
received confirmation this PO covers the current task order.

Contact: billing@acmefed.com
Phone: (703) 555-0147

Payment Terms: Net 30
"""
        }
    ]

    created_files = []
    for invoice in invoices:
        filepath = os.path.join(output_dir, invoice["filename"])
        with open(filepath, 'w') as f:
            f.write(invoice["content"])
        created_files.append(filepath)
        print(f"  Created: {invoice['filename']}")

    return created_files


def download_gov_pdfs():
    """Download real government PDFs from official .gov sources."""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "gov_pdfs")
    os.makedirs(output_dir, exist_ok=True)

    # Create SSL context
    ctx = ssl.create_default_context()

    downloaded = []
    failed = []

    for pdf in GOV_PDF_SOURCES:
        filepath = os.path.join(output_dir, pdf["name"])
        try:
            print(f"  Downloading: {pdf['name']}...")

            # Create request with proper headers
            req = urllib.request.Request(
                pdf["url"],
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'application/pdf,*/*'
                }
            )

            # Download with timeout
            with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
                with open(filepath, 'wb') as f:
                    f.write(response.read())

            # Verify file size
            size = os.path.getsize(filepath)
            if size > 1000:  # At least 1KB
                downloaded.append(pdf["name"])
                print(f"    ✓ Success: {pdf['description']} ({size:,} bytes)")
            else:
                os.remove(filepath)
                failed.append((pdf["name"], "File too small"))
                print(f"    ✗ Failed: File too small ({size} bytes)")

        except Exception as e:
            failed.append((pdf["name"], str(e)))
            print(f"    ✗ Failed: {e}")

    return downloaded, failed


def main():
    print("=" * 70)
    print("  GOVERNMENT PDF DOWNLOADER FOR RIK DEMO")
    print("=" * 70)
    print()

    # Create realistic invoice files (always works)
    print("Creating realistic government-style invoices...")
    created = create_realistic_gov_invoices()
    print(f"\n✓ Created {len(created)} realistic invoice files")
    print()

    # Try to download actual government PDFs
    print("Attempting to download government PDF templates...")
    downloaded, failed = download_gov_pdfs()

    if downloaded:
        print(f"\n✓ Downloaded {len(downloaded)} government PDFs")
    if failed:
        print(f"\n⚠ {len(failed)} downloads failed (may require manual download)")

    print()
    print("=" * 70)
    print("  READY FOR DEMO")
    print("=" * 70)
    print()
    print("📄 Test with realistic text invoices:")
    print("  python3 demos/pdf_live_processing_demo.py data/sample_pdfs/boeing_defense_invoice.txt")
    print("  python3 demos/pdf_live_processing_demo.py data/sample_pdfs/missing_po_invoice.txt")
    print()
    if downloaded:
        print("📑 Test with REAL government PDFs:")
        print("  streamlit run streamlit_app.py")
        print("  Then upload files from: data/gov_pdfs/")
        print()
        print("  Real PDFs downloaded:")
        for name in downloaded:
            print(f"    - {name}")
        print()
    print("These demonstrate RIK handling real government document complexity:")
    print("  - Multi-column layouts")
    print("  - Form fields and tables")
    print("  - Stamps, seals, signatures")
    print("  - Inconsistent formatting")
    print()


if __name__ == "__main__":
    main()
