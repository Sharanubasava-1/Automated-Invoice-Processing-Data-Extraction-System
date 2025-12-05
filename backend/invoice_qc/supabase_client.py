import os
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
_url = os.getenv("SUPABASE_URL")
_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not _url or not _key:
    print("⚠ Warning: Supabase credentials not found. Database features disabled.")
    supabase: Client | None = None
else:
    supabase: Client = create_client(_url, _key)


def store_invoice(invoice_dict: Dict[str, Any]) -> Dict[str, Any] | None:
    """Store an invoice in Supabase"""
    if not supabase:
        return None
    
    try:
        if 'line_items' in invoice_dict:
            invoice_dict['line_items'] = invoice_dict['line_items']
        
        response = supabase.table("invoices").insert(invoice_dict).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error storing invoice: {e}")
        return None


def store_qc_result(invoice_number: str, is_valid: bool, errors: List[str]) -> Dict[str, Any] | None:
    """Store validation result in Supabase"""
    if not supabase:
        return None
    
    try:
        result_dict = {
            "invoice_number": invoice_number,
            "is_valid": is_valid,
            "errors": errors
        }
        response = supabase.table("qc_results").insert(result_dict).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error storing QC result: {e}")
        return None


def get_invoice_by_number(invoice_number: str) -> Dict[str, Any] | None:
    """Retrieve an invoice by invoice number"""
    if not supabase:
        return None
    
    try:
        response = supabase.table("invoices").select("*").eq("invoice_number", invoice_number).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error retrieving invoice: {e}")
        return None


def get_recent_invoices(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent invoices"""
    if not supabase:
        return []
    
    try:
        response = supabase.table("invoices").select("*").order("created_at", desc=True).limit(limit).execute()
        return response.data or []
    except Exception as e:
        print(f"Error retrieving invoices: {e}")
        return []


def get_qc_results_by_invoice(invoice_number: str) -> List[Dict[str, Any]]:
    """Get QC results for a specific invoice"""
    if not supabase:
        return []
    
    try:
        response = supabase.table("qc_results").select("*").eq("invoice_number", invoice_number).execute()
        return response.data or []
    except Exception as e:
        print(f"Error retrieving QC results: {e}")
        return []


def check_duplicate_invoice(invoice_number: str, seller_name: str, invoice_date: str) -> bool:
    """Check if invoice already exists in database"""
    if not supabase:
        return False
    
    try:
        response = (supabase.table("invoices")
                   .select("id")
                   .eq("invoice_number", invoice_number)
                   .eq("seller_name", seller_name)
                   .eq("invoice_date", invoice_date)
                   .execute())
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking duplicate: {e}")
        return False
