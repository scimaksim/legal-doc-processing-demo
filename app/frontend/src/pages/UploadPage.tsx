import { useState, useRef, useCallback } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';

type UploadState = 'idle' | 'uploading' | 'parsing' | 'success' | 'error';

export default function UploadPage() {
  const [state, setState] = useState<UploadState>('idle');
  const [dragover, setDragover] = useState(false);
  const [message, setMessage] = useState('');
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadFile = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setState('error');
      setMessage('Only PDF files are supported.');
      return;
    }

    setFileName(file.name);
    setState('uploading');
    setMessage(`Uploading ${file.name}...`);

    const formData = new FormData();
    formData.append('file', file);

    try {
      setState('parsing');
      setMessage(`Processing ${file.name} with AI Document Parse...`);

      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Upload failed');
      }

      setState('success');
      setMessage(data.message || `${file.name} processed successfully.`);
    } catch (e: any) {
      setState('error');
      setMessage(e.message || 'Upload failed');
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragover(false);
      const file = e.dataTransfer.files[0];
      if (file) uploadFile(file);
    },
    [uploadFile]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) uploadFile(file);
    },
    [uploadFile]
  );

  const reset = () => {
    setState('idle');
    setMessage('');
    setFileName('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div>
      <div className="page-header">
        <h2>Upload Document</h2>
        <p>
          Upload a legal PDF document to parse and index with Databricks AI Document Parse
        </p>
      </div>

      {state === 'idle' && (
        <div
          className={`upload-zone ${dragover ? 'dragover' : ''}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragover(true);
          }}
          onDragLeave={() => setDragover(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload size={48} />
          <h3>Drop a PDF file here or click to browse</h3>
          <p>
            The document will be uploaded to the Unity Catalog volume, parsed using
            ai_document_parse, and indexed into the document_elements table.
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            style={{ display: 'none' }}
            onChange={handleFileSelect}
          />
        </div>
      )}

      {state !== 'idle' && (
        <div className="upload-progress">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {state === 'uploading' || state === 'parsing' ? (
              <div className="spinner" />
            ) : state === 'success' ? (
              <CheckCircle size={24} color="var(--green)" />
            ) : (
              <AlertCircle size={24} color="var(--red)" />
            )}
            <div>
              <div style={{ fontWeight: 600, fontSize: 15 }}>
                <FileText size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />
                {fileName}
              </div>
              <div className={`upload-status ${state}`}>{message}</div>
            </div>
          </div>

          {(state === 'uploading' || state === 'parsing') && (
            <div className="progress-bar-container">
              <div
                className="progress-bar"
                style={{ width: state === 'uploading' ? '30%' : '70%' }}
              />
            </div>
          )}

          {(state === 'success' || state === 'error') && (
            <button
              className="back-btn"
              style={{ marginTop: 16 }}
              onClick={reset}
            >
              Upload Another
            </button>
          )}
        </div>
      )}

      <div className="card" style={{ marginTop: 24 }}>
        <div className="card-header">
          <h3>Processing Pipeline</h3>
        </div>
        <div className="card-body">
          <div style={{ display: 'flex', gap: 24 }}>
            {[
              { step: 1, title: 'Upload', desc: 'PDF uploaded to Unity Catalog Volume' },
              { step: 2, title: 'Parse', desc: 'ai_document_parse extracts structure' },
              { step: 3, title: 'Flatten', desc: 'Elements indexed into document_elements table' },
            ].map((s) => (
              <div key={s.step} style={{ flex: 1, textAlign: 'center' }}>
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    background: 'var(--navy)',
                    color: 'var(--gold)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: 16,
                    marginBottom: 8,
                  }}
                >
                  {s.step}
                </div>
                <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{s.title}</h4>
                <p style={{ fontSize: 12, color: 'var(--slate)' }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
