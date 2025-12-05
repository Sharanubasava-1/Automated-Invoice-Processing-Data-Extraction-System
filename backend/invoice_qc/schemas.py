# invoice_qc/schemas.py
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, condecimal, constr

class LineItem(BaseModel):
    description: constr(strip_whitespace=True, min_length=1)
    quantity: condecimal(gt=0)
    unit_price: condecimal(ge=0)
    line_total: condecimal(ge=0)

class Invoice(BaseModel):
    invoice_number: constr(strip_whitespace=True, min_length=1)
    invoice_date: date
    due_date: Optional[date] = None

    seller_name: constr(strip_whitespace=True, min_length=1)
    seller_tax_id: Optional[str] = None
    buyer_name: constr(strip_whitespace=True, min_length=1)
    buyer_tax_id: Optional[str] = None

    currency: constr(strip_whitespace=True, min_length=3, max_length=3)
    net_total: condecimal(ge=0)
    tax_amount: condecimal(ge=0)
    gross_total: condecimal(ge=0)
    payment_terms: Optional[str] = None

    line_items: List[LineItem] = Field(default_factory=list)

    # invoice_qc/schemas.py (continued)
class InvoiceValidationResult(BaseModel):
    invoice_id: str
    is_valid: bool
    errors: list[str]

class ValidationSummary(BaseModel):
    total_invoices: int
    valid_invoices: int
    invalid_invoices: int
    error_counts: dict[str, int]