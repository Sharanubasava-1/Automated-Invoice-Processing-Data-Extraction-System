Invoice QC Service


A production-ready Invoice Extraction & Quality Control system that processes German B2B invoice PDFs, validates data against business rules, and provides CLI, API, and web interfaces.

Watch Demo Video
https://drive.google.com/file/d/1NG6ywQCPkLpoBR0OvnOisdy5z2ziuxf2/view?usp=drive_link


Features
PDF Extraction - Parses German invoices using pdfplumber + regex patterns

Smart Validation - 9 rules across completeness, format, business logic, and anomaly detection

CLI Tool - extract, validate, full-run commands for batch processing

REST API - FastAPI with /validate-json and /health endpoints

React UI - Real-time validation console with filtering

Database - Optional Supabase PostgreSQL integration

Schema Design
12 Invoice Fields: invoice_number, invoice_date, due_date, seller_name, seller_tax_id, buyer_name, buyer_tax_id, currency, net_total, tax_amount, gross_total, payment_terms, line_items

9 Validation Rules:

Completeness (3): Required fields check

Format (2): Date range, currency whitelist

Business (3): Totals match, line items sum, logical dates

Anomaly (1): Duplicate detection

Quick Start
Backend
bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m invoice_qc extract pdfs extracted.json
uvicorn app.main:app --reload
Frontend
bash
cd frontend
npm install
npm run dev
Visit http://localhost:5173 for the QC Console.

Architecture
PDFs → Extraction (pdfplumber) → Validation (Pydantic + rules)
                                        ↓
                            ┌───────────┼───────────┐
                            ↓           ↓           ↓
                          CLI      FastAPI     Supabase
                                       ↓
                                  React UI
AI Usage
Tools: Perplexity AI (primary), ChatGPT-4

Helped with:

Regex patterns for German text extraction

FastAPI CORS setup (saved 15+ min)

React component scaffolding

Pydantic condecimal for currency precision

AI Failures Fixed:

German number format (1.234,56) - AI suggested wrong separator logic, I added position detection

Line item regex - Too greedy, I implemented state machine for table boundaries

Date parsing - Single format assumption, I added multi-format fallback

Impact: 40% faster development, but required critical debugging for edge cases.

Tech Stack
Backend: Python 3.10, FastAPI, Pydantic, pdfplumber, Typer
Frontend: React 18, Vite, Axios
Database: Supabase (PostgreSQL)
Deployment: Docker-ready

Deliverables
- PDF extraction with German invoice support
- 9 validation rules with detailed error reporting
- CLI with 3 commands (extract, validate, full-run)
- REST API with Swagger docs
- React QC console with real-time validation
- Optional Supabase integration
- Comprehensive README with AI usage notes

🔗 Integration
Production Pipeline:

text
[OCR] → [Storage] → [Invoice QC API] → [ERP System]
                          ↓
                    [Supabase DB]
                          ↓
                  [Manual Review Queue]


Assumptions & Limitations

Assumptions:
German B2B invoices with consistent layout

Machine-readable PDFs (no OCR required)

Supported currencies: EUR, USD, INR

Limitations:
Heuristic line item extraction (works for simple tables)

No authentication on API endpoints

Synchronous processing (queue system for production scale)
