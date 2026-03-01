import { useState } from 'react';
import axios from 'axios';
import './App.css';
import { PdfUploader } from './components/PdfUploader';
import { supabase } from './supabaseClient';

const API_BASE = "https://invoice-backend-gsce.onrender.com";

function App() {
  const [payload, setPayload] = useState('');
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState(null);
  const [showOnlyInvalid, setShowOnlyInvalid] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleValidate = async () => {
    setLoading(true);
    setError('');

    try {
      const invoices = JSON.parse(payload);

      const res = await axios.post(
        `${API_BASE}/validate-json`,
        invoices,
        {
          headers: {
            "Content-Type": "application/json"
          },
          timeout: 60000
        }
      );

      setResults(res.data.results);
      setSummary(res.data.summary);

      // Save to Supabase
      const { error: supabaseError } = await supabase
        .from('invoices')
        .insert(
          res.data.results.map(result => ({
            invoice_id: result.invoice_id,
            is_valid: result.is_valid,
            errors: result.errors
          }))
        );

      if (supabaseError) {
        console.log("Supabase error:", supabaseError.message);
      } else {
        console.log("Saved to Supabase successfully ✅");
      }

    } catch (err) {
      console.error(err);

      if (err.code === "ECONNABORTED") {
        setError("Server is waking up. Please wait 10 seconds and try again.");
      } else if (err.response) {
        setError(err.response.data?.detail || "Validation failed");
      } else {
        setError("Network error. Backend may be sleeping.");
      }

    } finally {
      setLoading(false);
    }
  };

  const handlePdfResult = (result) => {
    setResults(prev => [...prev, result]);
    setSummary(null);
  };

  const loadSampleData = () => {
    const sample = [
      {
        invoice_number: "AUFNR34343",
        invoice_date: "2024-05-22",
        due_date: null,
        seller_name: "ABC Corporation",
        buyer_name: "Beispielname Unternehmen",
        currency: "EUR",
        net_total: 64,
        tax_amount: 12.16,
        gross_total: 76.16,
        line_items: []
      }
    ];

    setPayload(JSON.stringify(sample, null, 2));
  };

  const filtered = showOnlyInvalid
    ? results.filter(r => !r.is_valid)
    : results;

  return (
    <div className="container">

      <h1>📋 Invoice QC Console</h1>
      <p className="subtitle">Quality Control System for Invoice Data</p>

      <PdfUploader 
        apiBase={API_BASE}
        onValidationResult={handlePdfResult} 
      />

      <div className="input-section">

        <div className="header-row">
          <h3>OR: Paste Invoice JSON Data</h3>
          <button onClick={loadSampleData} className="btn-secondary">
            Load Sample
          </button>
        </div>

        <textarea
          rows={12}
          value={payload}
          onChange={e => setPayload(e.target.value)}
        />

        <button 
          onClick={handleValidate} 
          disabled={loading}
          className="btn-primary"
        >
          {loading ? "⏳ Validating..." : "✓ Validate Invoices"}
        </button>

        {error && (
          <div className="error">
            ❌ {error}
          </div>
        )}

      </div>

      {summary && (
        <div className="summary">

          <h3>📊 Validation Summary</h3>

          <div className="stats">
            <div className="stat">
              Total: {summary.total_invoices}
            </div>

            <div className="stat valid">
              Valid: {summary.valid_invoices}
            </div>

            <div className="stat invalid">
              Invalid: {summary.invalid_invoices}
            </div>
          </div>

        </div>
      )}

      {results.length > 0 && (
        <div className="results-section">

          <h3>📑 Results ({filtered.length})</h3>

          <table>

            <thead>
              <tr>
                <th>Invoice ID</th>
                <th>Status</th>
                <th>Errors</th>
              </tr>
            </thead>

            <tbody>

              {filtered.map(r => (

                <tr key={r.invoice_id}>

                  <td>{r.invoice_id}</td>

                  <td>
                    {r.is_valid ? "✓ Valid" : "✗ Invalid"}
                  </td>

                  <td>
                    {r.errors.join(", ")}
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>
      )}

    </div>
  );
}
export default App;