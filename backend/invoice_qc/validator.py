from collections import Counter
from decimal import Decimal
from datetime import date
from typing import Iterable
from .schemas import Invoice, InvoiceValidationResult, ValidationSummary
from .supabase_client import store_qc_result, check_duplicate_invoice

TOLERANCE = Decimal("0.05")

def validate_business_rules(invoice: Invoice) -> list[str]:
    errors: list[str] = []

    if invoice.line_items:
        sum_lines = sum((li.line_total for li in invoice.line_items), Decimal("0"))
        if abs(sum_lines - invoice.net_total) > TOLERANCE:
            errors.append("business_rule_failed: line_items_sum_mismatch")

    if abs(invoice.net_total + invoice.tax_amount - invoice.gross_total) > TOLERANCE:
        errors.append("business_rule_failed: totals_mismatch")

    if invoice.due_date and invoice.due_date < invoice.invoice_date:
        errors.append("business_rule_failed: due_date_before_invoice_date")

    if not (date(2015, 1, 1) <= invoice.invoice_date <= date.today()):
        errors.append("format_rule_failed: invoice_date_out_of_range")

    if invoice.currency not in {"INR", "EUR", "USD"}:
        errors.append("format_rule_failed: unsupported_currency")

    return errors


def validate_completeness(invoice: Invoice) -> list[str]:
    errors: list[str] = []
    if not invoice.invoice_number or invoice.invoice_number == "UNKNOWN":
        errors.append("missing_field: invoice_number")
    if not invoice.seller_name or invoice.seller_name == "UNKNOWN_SELLER":
        errors.append("missing_field: seller_name")
    if not invoice.buyer_name or invoice.buyer_name == "UNKNOWN_BUYER":
        errors.append("missing_field: buyer_name")
    return errors


def validate_duplicates(invoices: Iterable[Invoice]) -> dict[str, list[str]]:
    """Check for duplicates within batch"""
    seen: dict[tuple, str] = {}
    dup_errors: dict[str, list[str]] = {}
    
    for inv in invoices:
        key = (inv.invoice_number, inv.seller_name, inv.invoice_date)
        inv_id = inv.invoice_number
        
        if key in seen:
            dup_errors.setdefault(inv_id, []).append("anomaly_rule_failed: duplicate_invoice_in_batch")
        else:
            seen[key] = inv_id
    
    return dup_errors


def check_database_duplicates(invoice: Invoice) -> list[str]:
    """Check if invoice already exists in Supabase"""
    errors: list[str] = []
    
    if check_duplicate_invoice(
        invoice.invoice_number, 
        invoice.seller_name, 
        str(invoice.invoice_date)
    ):
        errors.append("anomaly_rule_failed: duplicate_invoice_in_database")
    
    return errors


def validate_invoices(invoices: list[Invoice], store_results: bool = False) -> tuple[list[InvoiceValidationResult], ValidationSummary]:
    """
    Validate invoices and optionally store results in Supabase
    
    Args:
        invoices: List of invoices to validate
        store_results: Whether to store validation results in Supabase
    """
    batch_dup_errors = validate_duplicates(invoices)
    results: list[InvoiceValidationResult] = []
    error_counter: Counter[str] = Counter()

    for inv in invoices:
        errors: list[str] = []
        
        # Run all validation checks
        errors.extend(validate_completeness(inv))
        errors.extend(validate_business_rules(inv))
        errors.extend(batch_dup_errors.get(inv.invoice_number, []))
        # errors.extend(check_database_duplicates(inv))

        # Count errors
        for e in errors:
            error_counter[e] += 1

        # Create result
        is_valid = len(errors) == 0
        result = InvoiceValidationResult(
            invoice_id=inv.invoice_number,
            is_valid=is_valid,
            errors=errors
        )
        results.append(result)
        
        # Store in Supabase if requested
        if store_results:
            try:
                store_qc_result(inv.invoice_number, is_valid, errors)
                print(f"✓ Stored validation result for {inv.invoice_number}")
            except Exception as e:
                print(f"⚠ Failed to store result for {inv.invoice_number}: {e}")

    valid_count = sum(1 for r in results if r.is_valid)
    summary = ValidationSummary(
        total_invoices=len(invoices),
        valid_invoices=valid_count,
        invalid_invoices=len(invoices) - valid_count,
        error_counts=dict(error_counter),
    )
    
    return results, summary
