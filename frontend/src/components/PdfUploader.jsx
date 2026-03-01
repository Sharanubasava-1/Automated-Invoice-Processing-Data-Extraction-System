import { useState } from 'react';
import axios from 'axios';

const API_BASE = "https://invoice-backend-gsce.onrender.com";

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

            const res = await axios.post(
                `${API_BASE}/upload-pdf`,
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    },
                    timeout: 60000
                }
            );

            const { is_valid, errors, invoice_data } = res.data;

            const resultForTable = {

                invoice_id: invoice_data.invoice_number,
                is_valid,
                errors

            };

            onValidationResult(resultForTable);

        } catch (err) {

            console.error(err);

            if (err.code === "ECONNABORTED") {

                setError("Server is waking up. Try again in 10 seconds.");

            } else if (err.response) {

                setError(err.response.data?.detail || "Upload failed");

            } else {

                setError("Network error. Backend may be sleeping.");

            }

        } finally {

            setLoading(false);

            e.target.value = null;

        }

    };

    return (

        <div className="pdf-uploader-section"
            style={{
                marginBottom: '2rem',
                padding: '1.5rem',
                border: '2px dashed #ccc',
                borderRadius: '8px',
                backgroundColor: '#f9f9f9'
            }}>

            <h3>📄 Upload PDF Invoice</h3>

            <p style={{ fontSize: '0.9rem', color: '#666' }}>
                Upload PDF and validate instantly.
            </p>

            <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                disabled={loading}
            />

            {loading && (
                <div>⏳ Processing Invoice...</div>
            )}

            {error && (
                <div className="error">
                    ❌ {error}
                </div>
            )}

        </div>

    );

}