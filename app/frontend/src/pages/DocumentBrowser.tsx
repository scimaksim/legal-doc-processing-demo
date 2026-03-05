import { FileText, Hash, Type, AlignLeft, Heading } from 'lucide-react';
import { useApi } from '../hooks/useApi';

interface Document {
  file_name: string;
  doc_id: string;
  total_elements: number;
  titles: number;
  section_headers: number;
  text_blocks: number;
  page_headers: number;
}

interface Props {
  onOpenDocument: (docId: string) => void;
}

const DOC_TYPE_LABELS: Record<string, string> = {
  'nda_agreement.pdf': 'Non-Disclosure Agreement',
  'software_license.pdf': 'Software License Agreement',
  'employment_agreement.pdf': 'Employment Agreement',
  'commercial_lease.pdf': 'Commercial Lease Agreement',
  'merger_agreement.pdf': 'Merger Agreement',
};

export default function DocumentBrowser({ onOpenDocument }: Props) {
  const { data, loading, error } = useApi<{ documents: Document[] }>('/api/documents');

  return (
    <div>
      <div className="page-header">
        <h2>Document Library</h2>
        <p>Browse and inspect parsed legal documents</p>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner" />
          Loading documents...
        </div>
      )}

      {error && <div className="error-message">Failed to load documents: {error}</div>}

      {data && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon gold">
                <FileText size={20} />
              </div>
              <div className="stat-label">Total Documents</div>
              <div className="stat-value">{data.documents.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon blue">
                <Hash size={20} />
              </div>
              <div className="stat-label">Total Elements</div>
              <div className="stat-value">
                {data.documents.reduce((sum, d) => sum + d.total_elements, 0)}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon green">
                <Type size={20} />
              </div>
              <div className="stat-label">Element Types</div>
              <div className="stat-value">4</div>
            </div>
          </div>

          <div className="doc-list">
            {data.documents.map((doc) => (
              <div
                key={doc.doc_id}
                className="doc-item"
                onClick={() => onOpenDocument(doc.doc_id)}
              >
                <div className="doc-icon">
                  <FileText size={24} />
                </div>
                <div className="doc-info">
                  <h4>{DOC_TYPE_LABELS[doc.file_name] || doc.file_name}</h4>
                  <div className="doc-meta">
                    <span>{doc.file_name}</span>
                    <span>{doc.total_elements} elements</span>
                  </div>
                </div>
                <div className="doc-badges">
                  {doc.titles > 0 && (
                    <span className="badge gold">{doc.titles} title{doc.titles !== 1 ? 's' : ''}</span>
                  )}
                  {doc.section_headers > 0 && (
                    <span className="badge blue">
                      {doc.section_headers} section{doc.section_headers !== 1 ? 's' : ''}
                    </span>
                  )}
                  {doc.text_blocks > 0 && (
                    <span className="badge green">
                      {doc.text_blocks} text
                    </span>
                  )}
                  {doc.page_headers > 0 && (
                    <span className="badge gray">
                      {doc.page_headers} pg header{doc.page_headers !== 1 ? 's' : ''}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
