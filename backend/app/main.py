from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import tempfile
import os
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from invoice_qc.schemas import Invoice, ValidationSummary
from invoice_qc.validator import validate_invoices
from invoice_qc.supabase_client import get_recent_invoices, get_qc_results_by_invoice, store_invoice
from invoice_qc.extractor import extract_text_from_pdf, extract_invoice_from_text

app = FastAPI(title="Invoice QC Service", version="1.0.0")

@app.get("/")
def root():
    return {
        "message": "Invoice QC API is running",
        "docs": "/docs",
        "health": "/health"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://your-netlify-site.netlify.app"   # add your Netlify URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/validate-json")
def validate_json(invoices: List[Invoice], store_results: bool = False):
    """
    Validate a list of invoices
    
    Args:
        invoices: List of invoice objects
        store_results: Whether to store results in Supabase
    """
    results, summary = validate_invoices(invoices, store_results=store_results)
    return {
        "summary": summary,
        "results": results,
    }


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and validate a PDF invoice
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Create a temporary file to save the upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        # Extract text from the temporary file
        text = extract_text_from_pdf(tmp_path)
        if not text:
             raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        # Parse invoice data
        invoice = extract_invoice_from_text(text)
        
        # Store invoice data in Supabase
        try:
            # Convert pydantic model to dict, ensuring dates etc are json friendly if needed
            # For supabase-py, basic python types usually work, but let's use json mode for safety with dates
            invoice_data = invoice.model_dump(mode='json')
            store_invoice(invoice_data)
        except Exception as e:
            print(f"Failed to store invoice data: {e}")

        # Validate invoice
        # validate_invoices expects a list
        # Enable store_results=True so validation results are also saved
        results, summary = validate_invoices([invoice], store_results=True)
        
        # We only processed one, so return the first result
        result = results[0]
        
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "invoice_data": invoice
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        if tmp_path.exists():
            os.remove(tmp_path)


@app.get("/invoices/recent")
def get_recent(limit: int = 10):
    """Get recent invoices from database"""
    invoices = get_recent_invoices(limit)
    return {"invoices": invoices}


@app.get("/invoices/{invoice_number}/qc-results")
def get_invoice_qc_results(invoice_number: str):
    """Get QC results for a specific invoice"""
    results = get_qc_results_by_invoice(invoice_number)
    return {"invoice_number": invoice_number, "results": results}

