import os
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend folder
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Get credentials
_url = os.getenv("SUPABASE_URL")
_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Initialize client
if not _url or not _key:
    print("⚠ Warning: Supabase credentials not found. Database features disabled.")
    supabase: Client | None = None
else:
    supabase: Client = create_client(_url, _key)


# Store invoice
def store_invoice(invoice_dict: Dict[str, Any]) -> Dict[str, Any] | None:
    if not supabase:
        return None
    
    try:
        response = supabase.table("invoices").insert(invoice_dict).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error storing invoice: {e}")
        return None


# Store QC result
def store_qc_result(invoice_number: str, is_valid: bool, errors: List[str]) -> Dict[str, Any] | None:
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


# Check duplicate invoice
def check_duplicate_invoice(invoice_number: str, seller_name: str, invoice_date: str) -> bool:
    if not supabase:
        return False
    
    try:
        response = (
            supabase.table("invoices")
            .select("id")
            .eq("invoice_number", invoice_number)
            .eq("seller_name", seller_name)
            .eq("invoice_date", invoice_date)
            .execute()
        )
        
        return len(response.data) > 0
    
    except Exception as e:
        print(f"Error checking duplicate: {e}")
        return False


# Get recent invoices
def get_recent_invoices(limit: int = 10) -> List[Dict[str, Any]]:
    if not supabase:
        return []
    
    try:
        response = (
            supabase.table("invoices")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        
        return response.data or []
    
    except Exception as e:
        print(f"Error retrieving invoices: {e}")
        return []
    
    # Get QC results by invoice number
def get_qc_results_by_invoice(invoice_number: str) -> List[Dict[str, Any]]:
    if not supabase:
        return []
    
    try:
        response = (
            supabase.table("qc_results")
            .select("*")
            .eq("invoice_number", invoice_number)
            .execute()
        )
        
        return response.data or []
    
    except Exception as e:
        print(f"Error retrieving QC results: {e}")
        return []