import json
from pathlib import Path
import typer
from typing_extensions import Annotated

app = typer.Typer()

@app.command()
def extract(
    pdf_dir: str = typer.Argument(..., help="Directory containing PDF files"),
    output: str = typer.Argument(..., help="Output JSON file path"),
    store_db: bool = typer.Option(False, "--store-db", help="Store invoices in Supabase")
):
    """Extract invoice data from PDFs"""
    try:
        from .extractor import extract_invoices_from_dir
        from .supabase_client import store_invoice
        
        pdf_path = Path(pdf_dir)
        if not pdf_path.exists():
            typer.secho(f"❌ Error: Directory '{pdf_dir}' does not exist!", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        
        typer.echo(f"📂 Scanning {pdf_dir} for PDFs...")
        invoices = extract_invoices_from_dir(pdf_path)
        
        if not invoices:
            typer.secho(f"⚠ Warning: No invoices extracted from {pdf_dir}", fg=typer.colors.YELLOW)
        
        # Store in Supabase if requested
        if store_db:
            typer.echo("💾 Storing invoices in Supabase...")
            for inv in invoices:
                inv_dict = inv.model_dump(mode="json")
                result = store_invoice(inv_dict)
                if result:
                    typer.echo(f"  ✓ Stored {inv.invoice_number}")
        
        data = [inv.model_dump(mode="json") for inv in invoices]
        Path(output).write_text(json.dumps(data, indent=2, default=str))
        typer.secho(f"✓ Extracted {len(invoices)} invoices to {output}", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        import traceback
        traceback.print_exc()
        raise


@app.command()
def validate(
    input_file: str = typer.Argument(..., help="Input JSON file with invoices"),
    report: str = typer.Argument(..., help="Output validation report file"),
    store_db: bool = typer.Option(False, "--store-db", help="Store results in Supabase")
):
    """Validate extracted invoices"""
    try:
        from .validator import validate_invoices
        from .schemas import Invoice
        
        input_path = Path(input_file)
        if not input_path.exists():
            typer.secho(f"❌ Error: File '{input_file}' does not exist!", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        
        raw = json.loads(input_path.read_text())
        invoices = [Invoice(**item) for item in raw]
        
        # Validate with optional DB storage
        results, summary = validate_invoices(invoices, store_results=store_db)
        
        Path(report).write_text(json.dumps({
            "summary": summary.model_dump(),
            "results": [r.model_dump() for r in results],
        }, indent=2))
        
        typer.secho(f"✓ Total: {summary.total_invoices}, "
                   f"Valid: {summary.valid_invoices}, "
                   f"Invalid: {summary.invalid_invoices}", fg=typer.colors.GREEN)
        
        if summary.invalid_invoices > 0:
            typer.secho(f"⚠ Found {summary.invalid_invoices} invalid invoices", fg=typer.colors.YELLOW)
            raise typer.Exit(code=1)
            
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        raise


@app.command()
def full_run(
    pdf_dir: str = typer.Argument(..., help="Directory containing PDF files"),
    report: str = typer.Argument(..., help="Output validation report file"),
    store_db: bool = typer.Option(False, "--store-db", help="Store in Supabase")
):
    """Extract and validate invoices (end-to-end)"""
    try:
        from .extractor import extract_invoices_from_dir
        from .validator import validate_invoices
        from .supabase_client import store_invoice
        
        typer.echo(f"📄 Extracting invoices from {pdf_dir}...")
        invoices = extract_invoices_from_dir(Path(pdf_dir))
        typer.secho(f"✓ Extracted {len(invoices)} invoices", fg=typer.colors.GREEN)
        
        # Store invoices if requested
        if store_db:
            typer.echo("💾 Storing invoices in Supabase...")
            for inv in invoices:
                store_invoice(inv.model_dump(mode="json"))
        
        typer.echo("🔍 Validating invoices...")
        results, summary = validate_invoices(invoices, store_results=store_db)
        
        Path(report).write_text(json.dumps({
            "summary": summary.model_dump(),
            "results": [r.model_dump() for r in results],
        }, indent=2))
        
        typer.secho(f"✓ Total: {summary.total_invoices}, "
                   f"Valid: {summary.valid_invoices}, "
                   f"Invalid: {summary.invalid_invoices}", fg=typer.colors.GREEN)
        
        if summary.invalid_invoices > 0:
            typer.secho(f"⚠ Found {summary.invalid_invoices} invalid invoices", fg=typer.colors.YELLOW)
        else:
            typer.secho("✓ All invoices are valid!", fg=typer.colors.GREEN)
            
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    app()
