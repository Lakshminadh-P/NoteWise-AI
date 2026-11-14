import { useState, useEffect } from 'react';
import api from '../services/api';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const res = await api.get('/api/documents');
      setDocuments(res.data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage('Upload successful! Processing your document...');
      setFile(null);
      loadDocuments();
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const statusBadge = (status) => {
    const colors = { pending: '#f59e0b', processing: '#6366f1', ready: '#10b981', error: '#ef4444' };
    return (
      <span style={{
        background: colors[status] || '#94a3b8', color: 'white',
        padding: '0.125rem 0.625rem', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 500,
      }}>
        {status}
      </span>
    );
  };

  return (
    <div className="container">
      <h1 style={{ marginBottom: '1.5rem' }}>📄 Upload Study Material</h1>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <form onSubmit={handleUpload}>
          <div className="upload-zone"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); setFile(e.dataTransfer.files[0]); }}
          >
            <p style={{ fontSize: '2rem' }}>📁</p>
            <p><strong>Drag & drop a PDF</strong> or click to browse</p>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files[0])}
              style={{ marginTop: '0.75rem' }}
            />
            {file && <p style={{ marginTop: '0.5rem', color: 'var(--color-primary)' }}>Selected: {file.name}</p>}
          </div>
          <button type="submit" className="btn btn-primary" disabled={!file || uploading} style={{ marginTop: '1rem' }}>
            {uploading ? 'Uploading...' : 'Upload & Process'}
          </button>
        </form>
        {message && <p style={{ marginTop: '1rem', fontWeight: 500 }}>{message}</p>}
      </div>

      <h2 style={{ marginBottom: '1rem' }}>Your Documents</h2>
      {documents.length === 0 ? (
        <p style={{ color: 'var(--color-text-secondary)' }}>No documents yet. Upload your first PDF!</p>
      ) : (
        <div className="doc-grid">
          {documents.map((doc) => (
            <div key={doc.id} className="card doc-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <h3 style={{ fontSize: '1rem' }}>{doc.title}</h3>
                {statusBadge(doc.status)}
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
                {doc.page_count ? `${doc.page_count} pages • ` : ''}
                {new Date(doc.uploaded_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}

      <style>{`
        .upload-zone {
          border: 2px dashed var(--color-border); border-radius: var(--radius);
          padding: 2rem; text-align: center; transition: border-color 0.15s;
        }
        .upload-zone:hover { border-color: var(--color-primary); }
        .doc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
        .doc-card { transition: box-shadow 0.15s; }
        .doc-card:hover { box-shadow: var(--shadow-md); }
      `}</style>
    </div>
  );
}

export default UploadPage;
