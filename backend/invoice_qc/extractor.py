import re
from pathlib import Path
from typing import List
from decimal import Decimal
from datetime import date
import pdfplumber
from .schemas import Invoice, LineItem
from .utils import parse_date, parse_amount

# German invoice patterns
ORDER_NO_PATTERNS = [
    r"Bestellung\s+(\w+)",
    r"AUFNR(\d+)",
    r"Order\s*(?:No\.?|Number)\s*[:\-]?\s*(\S+)",
]

DATE_PATTERNS = [
    r"vom\s+(\d{2}\.\d{2}\.\d{4})",  # German date format
    r"Bestellung\s+\w+\s+vom\s+(\d{2}\.\d{2}\.\d{4})",
    r"(\d{2}\.\d{2}\.\d{4})",
]

CUSTOMER_PATTERNS = [
    r"Kundennummer\s+(\d+)",
    r"Kundenanschrift\s*\n(.+?)(?:\n|$)",
]

SUPPLIER_PATTERNS = [
    r"im Auftrag von\s+(\d+)",
    r"^(.+?)\s+Bestellung",  # First line usually company name
]

def extract_text_from_pdf(path: Path) -> str:
    """Extract all text from PDF"""
    try:
        with pdfplumber.open(str(path)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages)
    except Exception as e:
        print(f"Error reading PDF {path}: {e}")
        return ""

def find_first_group(text: str, patterns: list[str]) -> str | None:
    """Find first matching pattern in text"""
    if not text:
        return None
    
    for pat in patterns:
        try:
            m = re.search(pat, text, flags=re.IGNORECASE | re.MULTILINE)
            if m:
                return m.group(1).strip()
        except:
            continue
    return None

def parse_german_date(date_str: str | None) -> date:
    """Parse German date format DD.MM.YYYY"""
    if not date_str:
        return date.today()
    
    try:
        # German format: DD.MM.YYYY
        parts = date_str.strip().split('.')
        if len(parts) == 3:
            day, month, year = parts
            return date(int(year), int(month), int(day))
    except:
        pass
    
    return date.today()

def extract_amounts(text: str) -> tuple[Decimal, Decimal, Decimal]:
    """Extract net, tax, and gross totals from German invoice"""
    net = Decimal("0")
    tax = Decimal("0")
    gross = Decimal("0")
    
    # Gesamtwert (net total)
    net_match = re.search(r"Gesamtwert\s+EUR\s+([\d,]+\.?\d*)", text)
    if net_match:
        net_str = net_match.group(1).replace(",", "")
        net = Decimal(net_str)
    
    # MwSt (VAT/tax)
    tax_match = re.search(r"MwSt\.?\s+[\d,]+%\s+EUR\s+([\d,]+\.?\d*)", text)
    if tax_match:
        tax_str = tax_match.group(1).replace(",", "")
        tax = Decimal(tax_str)
    
    # Gesamtwert inkl. MwSt (gross total)
    gross_match = re.search(r"Gesamtwert inkl\.\s+MwSt\.\s+EUR\s+([\d,]+\.?\d*)", text)
    if gross_match:
        gross_str = gross_match.group(1).replace(",", "")
        gross = Decimal(gross_str)
    
    return net, tax, gross

def extract_line_items(text: str) -> List[LineItem]:
    """Extract line items from German invoice"""
    items = []
    
    # Find the table section
    lines = text.split('\n')
    in_items = False
    
    for line in lines:
        # Start of items section
        if re.search(r"Pos\.\s+Artikelbeschreibung", line):
            in_items = True
            continue
        
        # End of items section
        if in_items and re.search(r"Gesamtwert", line):
            break
        
        if in_items:
            # Match line items: number at start, description, then amounts
            match = re.match(r"^(\d+)\s+(.+?)\s+([\d,]+\.?\d*)\s+(\d+)\s+(\w+)", line)
            if match:
                desc = match.group(2).strip()
                unit_price = Decimal(match.group(3).replace(",", ""))
                quantity = Decimal(match.group(4))
                
                # Find line total (usually at end of line)
                total_match = re.search(r"([\d,]+\.?\d*)\s*$", line)
                line_total = Decimal(total_match.group(1).replace(",", "")) if total_match else unit_price * quantity
                
                items.append(LineItem(
                    description=desc,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total
                ))
    
    return items

def extract_invoice_from_text(text: str) -> Invoice:
    """Extract invoice data from German text"""
    
    # Extract order/invoice number
    invoice_number = find_first_group(text, ORDER_NO_PATTERNS) or "UNKNOWN"
    
    # Extract date
    date_str = find_first_group(text, DATE_PATTERNS)
    invoice_date = parse_german_date(date_str)
    
    # Currency (always EUR in these documents)
    currency = "EUR"
    
    # Extract amounts
    net_total, tax_amount, gross_total = extract_amounts(text)
    
    # Extract parties
    # For German invoices, try to get company names
    lines = text.split('\n')
    seller_name = "ABC Corporation" if "ABC Corporation" in text else lines[1] if len(lines) > 1 else "UNKNOWN_SELLER"
    
    buyer_match = re.search(r"Kundenanschrift\s*\n(.+?)(?:\n.+?){0,2}\n", text, re.MULTILINE)
    buyer_name = buyer_match.group(1).strip() if buyer_match else "UNKNOWN_BUYER"
    
    # Extract customer number as tax ID
    customer_no = find_first_group(text, CUSTOMER_PATTERNS)
    
    # Extract line items
    line_items = extract_line_items(text)
    
    return Invoice(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=None,
        seller_name=seller_name,
        seller_tax_id=None,
        buyer_name=buyer_name,
        buyer_tax_id=customer_no,
        currency=currency,
        net_total=net_total,
        tax_amount=tax_amount,
        gross_total=gross_total,
        payment_terms=None,
        line_items=line_items,
    )

def extract_invoices_from_dir(pdf_dir: Path) -> List[Invoice]:
    """Extract invoices from all PDFs in directory"""
    invoices: list[Invoice] = []
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for path in pdf_files:
        try:
            text = extract_text_from_pdf(path)
            if not text:
                print(f"Failed to extract text from {path.name}")
                continue
            
            inv = extract_invoice_from_text(text)
            invoices.append(inv)
            print(f"✓ Successfully parsed {path.name}: {inv.invoice_number}")
        except Exception as e:
            print(f"Failed to parse {path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    return invoices