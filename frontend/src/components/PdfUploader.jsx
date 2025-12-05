import { useState } from 'react';
import axios from 'axios';

export function PdfUploader({ onValidationResult }) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setLoading(true);
        setError('');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post('http://localhost:8000/upload-pdf', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const { is_valid, errors, invoice_data } = res.data;

            const resultForTable = {
                invoice_id: invoice_data.invoice_number,
                is_valid,
                errors
            };

            onValidationResult(resultForTable);

        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "Upload failed");
        } finally {
            setLoading(false);
            // Reset file input
            e.target.value = null;
        }
    };

    return (
        <div className="pdf-uploader-section" style={{ marginBottom: '2rem', padding: '1.5rem', border: '2px dashed #ccc', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
            <h3 style={{ marginTop: 0 }}>📄 Upload PDF Invoice</h3>
            <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
                Upload a PDF to extract invoice data and validate it immediately.
            </p>

            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    disabled={loading}
                    style={{ padding: '0.5rem' }}
                />
                {loading && <span style={{ fontWeight: 'bold', color: '#0066cc' }}>⏳ Processing Invoice...</span>}
            </div>

            {error && (
                <div className="error" style={{ marginTop: '1rem', padding: '0.5rem', backgroundColor: '#fee', color: '#c00', borderRadius: '4px' }}>
                    ❌ {error}
                </div>
            )}
        </div>
    );
}
