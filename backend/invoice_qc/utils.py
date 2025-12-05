from datetime import datetime, date
from decimal import Decimal
import re

def parse_date(date_str: str | None) -> date:
    """Parse date string in various formats"""
    if not date_str:
        return date.today()
    
    # Try common formats
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return date.today()

def parse_amount(text_or_match, group: int = 1) -> Decimal:
    """Extract decimal amount from regex match or string"""
    if text_or_match is None:
        return Decimal("0")
    
    # Handle regex match objects
    if hasattr(text_or_match, 'group'):
        try:
            text = text_or_match.group(group)
        except:
            return Decimal("0")
    else:
        text = str(text_or_match)
    
    if not text:
        return Decimal("0")
    
    # Remove currency symbols, commas, and extra spaces
    text = re.sub(r'[^\d.\-]', '', text)
    
    try:
        return Decimal(text) if text else Decimal("0")
    except:
        return Decimal("0")