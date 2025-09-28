"""Test state generation for expense tracking application."""

import uuid
import datetime
from state import (
    State, StoreMemory, CompanyData, Bank, BankTransaction,
    Client, Supplier, Document, Invoice, Expense
)


def create_test_state() -> State:
    """Create a comprehensive test state with multiple expenses and receipts."""
    st = StoreMemory()

    # Generate dates for the last 3 months
    now = datetime.date.today()
    base_dates = [
        now - datetime.timedelta(days=90),
        now - datetime.timedelta(days=75),
        now - datetime.timedelta(days=60),
        now - datetime.timedelta(days=45),
        now - datetime.timedelta(days=30),
        now - datetime.timedelta(days=20),
        now - datetime.timedelta(days=15),
        now - datetime.timedelta(days=10),
        now - datetime.timedelta(days=7),
        now - datetime.timedelta(days=5),
        now - datetime.timedelta(days=3),
        now - datetime.timedelta(days=2),
        now - datetime.timedelta(days=1),
        now,
    ]

    # Set up company data
    st.set_company(
        CompanyData(
            id=uuid.uuid4(),
            name="Acme Inc.",
            address="123 Main St, Anytown USA",
            phone="555-1234",
            email="info@acmeinc.com",
            vat_number="123456789",
            country="USA",
        )
    )

    # Create banks
    bank1_id = uuid.uuid4()
    bank2_id = uuid.uuid4()

    # Bank 1 - Bank of America
    bank1_transactions = [
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[0],
            amount=-450.00,
            description="UNITED AIRLINES CORP"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[1],
            amount=-189.50,
            description="MARRIOTT HOTELS"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[1],
            amount=-67.25,
            description="UBER *TRIP"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[2],
            amount=-234.99,
            description="STAPLES #1234"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[3],
            amount=-89.99,
            description="BEST BUY #456"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[4],
            amount=-156.80,
            description="THE CAPITAL GRILLE"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[5],
            amount=-42.50,
            description="CHIPOTLE ONLINE"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[6],
            amount=-299.00,
            description="ADOBE SYSTEMS INC"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[0],
            amount=5000.00,
            description="WIRE TRANSFER REF#8923"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[2],
            amount=-3500.00,
            description="PAYROLL 03/2024"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[4],
            amount=-100.00,
            description="CLEANPRO SERVICES"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[5],
            amount=2500.00,
            description="ACH CREDIT TECH CORP"
        ),
    ]

    st.set_bank(
        Bank(
            id=bank1_id,
            currency="USD",
            iban="US1234567890",
            name="Bank of America"
        ),
        bank1_transactions
    )

    # Bank 2 - Chase
    bank2_transactions = [
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[7],
            amount=-159.99,
            description="MICROSOFT 365 BUSINESS"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[8],
            amount=-599.00,
            description="LINKEDIN LEARNING"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[9],
            amount=-249.99,
            description="AWS SERVICES"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[10],
            amount=-125.00,
            description="CITY PARKING"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[11],
            amount=-278.45,
            description="COSTCO WHSE #0234"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[12],
            amount=-2150.00,
            description="TECHSUMMIT INC"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[13],
            amount=-35.00,
            description="YELLOW CAB 4567"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[1],
            amount=-2500.00,
            description="CHECK #1234"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[3],
            amount=8000.00,
            description="WIRE IN 3847298"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[6],
            amount=-450.00,
            description="SAFEGUARD INS"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[8],
            amount=-185.00,
            description="COMCAST BUSINESS"
        ),
        BankTransaction(
            id=uuid.uuid4(),
            date=base_dates[10],
            amount=-320.00,
            description="FEDEX OFFICE"
        ),
    ]

    st.set_bank(
        Bank(
            id=bank2_id,
            currency="USD",
            iban="US9876543210",
            name="Chase"
        ),
        bank2_transactions
    )

    # Add clients
    client1 = Client(
        id=uuid.uuid4(),
        name="Johnson & Associates",
        address="456 Client St, New York, NY 10001",
        vat_number="CLIENT123456",
        email="billing@johnsonassoc.com",
        phone="555-234-5678",
        country="US"
    )
    st.store_client(client1)

    client2 = Client(
        id=uuid.uuid4(),
        name="Tech Corp",
        address="789 Tech Ave, San Francisco, CA 94105",
        vat_number="TECH789012",
        email="accounts@techcorp.com",
        phone="555-345-6789",
        country="US"
    )
    st.store_client(client2)

    client3 = Client(
        id=uuid.uuid4(),
        name="BigCorp Ltd",
        address="321 Corporate Blvd, Chicago, IL 60601",
        vat_number="BIG456789",
        email="finance@bigcorp.com",
        phone="555-456-7890",
        country="US"
    )
    st.store_client(client3)

    # Add suppliers
    suppliers = [
        Supplier(
            id=uuid.uuid4(),
            name="United Airlines",
            address="233 S Wacker Dr, Chicago, IL 60606",
            vat_number="UA123456",
            email="corporate@united.com",
            phone="800-864-8331",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="Marriott Hotels",
            address="10400 Fernwood Rd, Bethesda, MD 20817",
            vat_number="MAR789012",
            email="billing@marriott.com",
            phone="301-380-3000",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="Staples",
            address="500 Staples Dr, Framingham, MA 01702",
            vat_number="STA345678",
            email="business@staples.com",
            phone="800-333-3330",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="Best Buy",
            address="7601 Penn Ave S, Richfield, MN 55423",
            vat_number="BB901234",
            email="business@bestbuy.com",
            phone="888-237-8289",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="Adobe",
            address="345 Park Ave, San Jose, CA 95110",
            vat_number="AD567890",
            email="billing@adobe.com",
            phone="408-536-6000",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="Uber",
            address="1455 Market St, San Francisco, CA 94103",
            vat_number="UB234567",
            email="business@uber.com",
            phone="866-576-1039",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="The Capital Grille",
            address="900 Boylston St, Boston, MA 02115",
            vat_number="CG890123",
            email="events@thecapitalgrille.com",
            phone="617-262-8900",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="Costco",
            address="999 Lake Dr, Issaquah, WA 98027",
            vat_number="CO456789",
            email="business@costco.com",
            phone="800-774-2678",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="Amazon Web Services",
            address="410 Terry Ave N, Seattle, WA 98109",
            vat_number="AWS123890",
            email="billing@aws.amazon.com",
            phone="888-280-4331",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="Microsoft Corporation",
            address="One Microsoft Way, Redmond, WA 98052",
            vat_number="MS365789",
            email="billing@microsoft.com",
            phone="800-642-7676",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="LinkedIn Corporation",
            address="1000 W Maude Ave, Sunnyvale, CA 94085",
            vat_number="LI456789",
            email="learning@linkedin.com",
            phone="650-687-3600",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="FedEx Office",
            address="3610 Hacks Cross Rd, Memphis, TN 38125",
            vat_number="FX789012",
            email="business@fedex.com",
            phone="800-463-3339",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="Comcast Business",
            address="1701 JFK Blvd, Philadelphia, PA 19103",
            vat_number="CB234567",
            email="business@comcast.com",
            phone="800-391-3000",
            country="US"
        ),
        Supplier(
            id=uuid.uuid4(),
            name="TechSummit",
            address="500 Convention Way, Las Vegas, NV 89109",
            vat_number="TS567234",
            email="registration@techsummit.com",
            phone="702-555-0100",
            country="US"
        ),
    ]

    for supplier in suppliers:
        st.store_supplier(supplier)

    # Add documents (receipts)
    documents = [
        # Matching receipts for transactions
        Document(
            id=uuid.uuid4(),
            name="united_airlines_receipt.pdf",
            description="Flight receipt - United Airlines to San Francisco",
            content="""UNITED AIRLINES E-TICKET RECEIPT
Confirmation Code: ABC123
Date: """ + base_dates[0].strftime("%Y-%m-%d") + """
Passenger: John Doe / Acme Inc.
From: New York (JFK) To: San Francisco (SFO)
Flight: UA 523
Fare: $410.00
Taxes & Fees: $40.00
Total: $450.00
Payment: Corporate Card ending 1234"""
        ),
        Document(
            id=uuid.uuid4(),
            name="marriott_invoice_89234.pdf",
            description="Hotel invoice - Marriott Downtown SF",
            content="""MARRIOTT HOTELS - FOLIO
Guest: John Doe / Acme Inc.
Check-in: """ + base_dates[1].strftime("%Y-%m-%d") + """
Check-out: """ + (base_dates[1] + datetime.timedelta(days=2)).strftime("%Y-%m-%d") + """
Room Rate: $175.00 x 2 nights = $350.00
Taxes: $39.50
Total: $389.50
Payment: Corporate Card"""
        ),
        Document(
            id=uuid.uuid4(),
            name="staples_receipt_20240115.jpg",
            description="Office supplies purchase receipt",
            content="""STAPLES RECEIPT
Store #1234
Date: """ + base_dates[2].strftime("%Y-%m-%d") + """
Items:
- HP Printer Ink (2x): $89.99
- Copy Paper (10 reams): $79.99
- Misc Office Supplies: $65.01
Subtotal: $234.99
Tax: $0.00 (Tax Exempt)
Total: $234.99"""
        ),
        Document(
            id=uuid.uuid4(),
            name="bestbuy_receipt.png",
            description="Electronics purchase - ergonomic equipment",
            content="""BEST BUY RECEIPT
Transaction #78234
Date: """ + base_dates[3].strftime("%Y-%m-%d") + """
Logitech MX Master Mouse: $49.99
Microsoft Ergonomic Keyboard: $40.00
Subtotal: $89.99
Tax: $0.00
Total: $89.99"""
        ),
        Document(
            id=uuid.uuid4(),
            name="capital_grille_receipt.pdf",
            description="Business dinner receipt",
            content="""THE CAPITAL GRILLE
Date: """ + base_dates[4].strftime("%Y-%m-%d") + """
Server: Michael
Table: 12
Guests: 4
Food: $130.00
Beverages: $26.80
Subtotal: $156.80
Tax: Included
Tip: Included
Total: $156.80
Business Purpose: Client dinner - Johnson & Associates"""
        ),
        Document(
            id=uuid.uuid4(),
            name="adobe_invoice_2024.pdf",
            description="Adobe Creative Cloud subscription",
            content="""ADOBE SYSTEMS
Invoice Date: """ + base_dates[6].strftime("%Y-%m-%d") + """
Customer: Acme Inc.
Product: Creative Cloud for Business - Annual
Amount: $299.00
Tax: $0.00
Total: $299.00
Payment Method: Auto-renewal"""
        ),
        Document(
            id=uuid.uuid4(),
            name="microsoft_365_invoice.pdf",
            description="Microsoft 365 Business subscription",
            content="""MICROSOFT 365 BUSINESS
Invoice Date: """ + base_dates[7].strftime("%Y-%m-%d") + """
Plan: Business Standard
Users: 10
Period: Monthly
Amount: $159.99
Total: $159.99"""
        ),
        Document(
            id=uuid.uuid4(),
            name="linkedin_learning_receipt.pdf",
            description="LinkedIn Learning team subscription",
            content="""LINKEDIN LEARNING
Receipt Date: """ + base_dates[8].strftime("%Y-%m-%d") + """
Team License: 5 seats
Training Library Access
Duration: Annual
Price: $599.00
Total: $599.00"""
        ),
        Document(
            id=uuid.uuid4(),
            name="parking_pass_march.pdf",
            description="Monthly parking pass",
            content="""CITY PARKING AUTHORITY
Date: """ + base_dates[10].strftime("%Y-%m-%d") + """
Location: Downtown Garage
Type: Monthly Pass
Period: Current Month
Amount: $125.00"""
        ),
        Document(
            id=uuid.uuid4(),
            name="costco_receipt_8923.jpg",
            description="Office supplies bulk purchase - AMOUNT MISMATCH",
            content="""COSTCO WHOLESALE
Receipt #8923
Date: """ + base_dates[11].strftime("%Y-%m-%d") + """
Paper (10 cases): $145.00
Office supplies: $142.45
Total: $287.45
Note: Receipt amount doesn't match bank transaction ($278.45)"""
        ),
        Document(
            id=uuid.uuid4(),
            name="taxi_receipt_morning.jpg",
            description="Taxi to airport",
            content="""YELLOW CAB CO.
Date: """ + base_dates[13].strftime("%Y-%m-%d") + """
Pickup: Downtown Office
Dropoff: International Airport
Distance: 15 miles
Fare: $30.00
Tip: $5.00
Total: $35.00"""
        ),
        # Orphaned receipts (no matching transaction)
        Document(
            id=uuid.uuid4(),
            name="random_receipt_001.pdf",
            description="Office Depot purchase - ORPHANED",
            content="""OFFICE DEPOT
Date: """ + base_dates[5].strftime("%Y-%m-%d") + """
Pens and pencils: $25.00
Notebooks: $42.89
Total: $67.89
Note: No matching bank transaction"""
        ),
        Document(
            id=uuid.uuid4(),
            name="lunch_receipt_feb.jpg",
            description="Subway lunch - ORPHANED",
            content="""SUBWAY
Date: """ + base_dates[6].strftime("%Y-%m-%d") + """
Sandwiches (3): $28.50
Drinks: $6.00
Total: $34.50
Note: No matching bank transaction"""
        ),
        Document(
            id=uuid.uuid4(),
            name="gas_station_receipt.png",
            description="Shell gas purchase - ORPHANED",
            content="""SHELL STATION
Date: """ + base_dates[7].strftime("%Y-%m-%d") + """
Regular Gas: 15 gallons @ $3.67/gal
Total: $55.00
Note: No matching bank transaction"""
        ),
        Document(
            id=uuid.uuid4(),
            name="pharmacy_receipt.pdf",
            description="CVS Pharmacy purchase - ORPHANED",
            content="""CVS PHARMACY
Date: """ + base_dates[9].strftime("%Y-%m-%d") + """
Office first aid supplies: $23.45
Total: $23.45
Note: No matching bank transaction"""
        ),
        # Additional receipts for variety
        Document(
            id=uuid.uuid4(),
            name="conference_invoice.pdf",
            description="TechSummit 2024 registration",
            content="""TECHSUMMIT 2024
Registration Invoice
Date: """ + base_dates[12].strftime("%Y-%m-%d") + """
Event: TechSummit 2024
Date: June 15-17, 2024
Registration Type: Early Bird - Full Access
Includes: All sessions, workshops, networking events
Amount: $2,150.00
Payment: Corporate Card"""
        ),
        Document(
            id=uuid.uuid4(),
            name="aws_invoice.pdf",
            description="AWS cloud services monthly",
            content="""AMAZON WEB SERVICES
Invoice Date: """ + base_dates[9].strftime("%Y-%m-%d") + """
Services:
EC2 Instances: $150.00
S3 Storage: $45.99
RDS Database: $54.00
Subtotal: $249.99
Tax: $0.00
Total: $249.99"""
        ),
        Document(
            id=uuid.uuid4(),
            name="chipotle_receipt.jpg",
            description="Team lunch receipt - NO MATCHING TRANSACTION",
            content="""CHIPOTLE MEXICAN GRILL
Date: """ + base_dates[5].strftime("%Y-%m-%d") + """
Items:
- Burrito Bowls (4): $36.00
- Drinks (4): $6.50
Total: $42.50
Note: Team lunch - should match bank transaction"""
        ),
        Document(
            id=uuid.uuid4(),
            name="uber_rides_summary.pdf",
            description="Uber business rides in SF",
            content="""UBER FOR BUSINESS
Trip Summary
Date: """ + base_dates[1].strftime("%Y-%m-%d") + """
Rides:
1. Airport to Hotel: $28.50
2. Hotel to Client Office: $15.25
3. Client Office to Restaurant: $12.00
4. Restaurant to Hotel: $11.50
Total: $67.25
Account: Acme Inc. Business"""
        ),
        Document(
            id=uuid.uuid4(),
            name="insurance_invoice.pdf",
            description="Business insurance Q1 premium",
            content="""SAFEGUARD INSURANCE
Invoice Date: """ + base_dates[6].strftime("%Y-%m-%d") + """
Policy: Business General Liability
Period: Q1 2024
Premium: $450.00
Payment Due: Within 30 days"""
        ),
        Document(
            id=uuid.uuid4(),
            name="fedex_shipping_invoice.pdf",
            description="FedEx shipping and printing services",
            content="""FEDEX OFFICE
Invoice Date: """ + base_dates[10].strftime("%Y-%m-%d") + """
Services:
- Express Shipping (5 packages): $250.00
- Document Printing (500 pages): $50.00
- Binding Services: $20.00
Total: $320.00"""
        ),
        Document(
            id=uuid.uuid4(),
            name="comcast_business_bill.pdf",
            description="Internet and phone services",
            content="""COMCAST BUSINESS
Bill Date: """ + base_dates[8].strftime("%Y-%m-%d") + """
Services:
- Business Internet 1GB: $150.00
- VoIP Phone Lines (3): $35.00
Total: $185.00"""
        ),
    ]

    for doc in documents:
        st.store_document(doc)

    # Add invoices (money coming in)
    invoice1 = Invoice(
        id=uuid.uuid4(),
        client=client1.id,
        amount=5000.00,
        currency="USD",
        created=base_dates[0] - datetime.timedelta(days=15),
        due_date=base_dates[0],
        description="Consulting services - Project Alpha"
    )
    st.store_invoice(invoice1)

    invoice2 = Invoice(
        id=uuid.uuid4(),
        client=client2.id,
        amount=2500.00,
        currency="USD",
        created=base_dates[5] - datetime.timedelta(days=10),
        due_date=base_dates[5],
        description="Software development - Module Beta"
    )
    st.store_invoice(invoice2)

    invoice3 = Invoice(
        id=uuid.uuid4(),
        client=client3.id,
        amount=8000.00,
        currency="USD",
        created=base_dates[3] - datetime.timedelta(days=20),
        due_date=base_dates[3],
        description="Annual service contract - Q1 payment"
    )
    st.store_invoice(invoice3)

    # Add some expenses (to show some transactions are already expensed)
    expense1 = Expense(
        id=uuid.uuid4(),
        bank_txs=[bank1_transactions[0].id],  # United Airlines flight
        docs_ids=[documents[0].id],  # United Airlines receipt
        supplier_id=suppliers[0].id,  # United Airlines supplier
        description="Business travel to San Francisco for client meeting",
        vat_type="NO_VAT"  # Air travel typically no VAT
    )
    st.store_expense(expense1)

    expense2 = Expense(
        id=uuid.uuid4(),
        bank_txs=[bank1_transactions[3].id],  # Staples office supplies
        docs_ids=[documents[2].id],  # Staples receipt
        supplier_id=suppliers[2].id,  # Staples supplier
        description="Office supplies purchase - printer ink and paper",
        vat_type="VAT"  # Office supplies have VAT
    )
    st.store_expense(expense2)

    return st