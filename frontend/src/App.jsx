import { useState } from 'react';
import axios from 'axios';
import './App.css';
import { PdfUploader } from './components/PdfUploader';

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
      const res = await axios.post('http://localhost:8000/validate-json', invoices);
      setResults(res.data.results);
      setSummary(res.data.summary);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to validate');
    } finally {
      setLoading(false);
    }
  };

  const handlePdfResult = (result) => {
    // Append the new result to the existing results
    setResults(prev => [...prev, result]);
    // Optionally update summary logic here if needed, or clear it since it corresponds to the JSON batch
    // For simplicity, let's clear the batch summary to avoid confusion, or we'd need to recalculate it.
    // Let's clear it since we are mixing sources now.
    setSummary(null);
  };

  const loadSampleData = () => {
    const sample = [
      {
        "invoice_number": "AUFNR34343",
        "invoice_date": "2024-05-22",
        "due_date": null,
        "seller_name": "ABC Corporation",
        "buyer_name": "Beispielname Unternehmen",
        "currency": "EUR",
        "net_total": 64.00,
        "tax_amount": 12.16,
        "gross_total": 76.16,
        "line_items": []
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

      <PdfUploader onValidationResult={handlePdfResult} />

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
          placeholder='Paste invoice JSON array here: [{"invoice_number": "INV-001", ...}]'
        />
        <button onClick={handleValidate} disabled={loading} className="btn-primary">
          {loading ? '⏳ Validating...' : '✓ Validate Invoices'}
        </button>
        {error && <div className="error">❌ {error}</div>}
      </div>

      {summary && (
        <div className="summary">
          <h3>📊 Validation Summary</h3>
          <div className="stats">
            <div className="stat">
              <span className="label">Total Invoices</span>
              <span className="value">{summary.total_invoices}</span>
            </div>
            <div className="stat valid">
              <span className="label">Valid</span>
              <span className="value">{summary.valid_invoices}</span>
            </div>
            <div className="stat invalid">
              <span className="label">Invalid</span>
              <span className="value">{summary.invalid_invoices}</span>
            </div>
          </div>

          {summary.error_counts && Object.keys(summary.error_counts).length > 0 && (
            <div className="error-counts">
              <h4>Error Breakdown:</h4>
              <ul>
                {Object.entries(summary.error_counts).map(([error, count]) => (
                  <li key={error}>
                    <span className="error-type">{error}</span>
                    <span className="error-count">{count}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {results.length > 0 && (
        <div className="results-section">
          <div className="controls">
            <h3>📑 Validation Results ({filtered.length})</h3>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={showOnlyInvalid}
                onChange={e => setShowOnlyInvalid(e.target.checked)}
              />
              Show only invalid
            </label>
          </div>

          <div className="table-container">
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
                  <tr key={r.invoice_id} className={r.is_valid ? '' : 'invalid-row'}>
                    <td><strong>{r.invoice_id}</strong></td>
                    <td>
                      <span className={`badge ${r.is_valid ? 'valid' : 'invalid'}`}>
                        {r.is_valid ? '✓ Valid' : '✗ Invalid'}
                      </span>
                    </td>
                    <td>
                      {r.errors.length > 0 ? (
                        <ul className="error-list">
                          {r.errors.map((e, idx) => (
                            <li key={idx}>{e}</li>
                          ))}
                        </ul>
                      ) : (
                        <span className="no-errors">✓ No errors</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;