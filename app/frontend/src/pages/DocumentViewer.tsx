import { useState } from 'react';
import { ArrowLeft, FileText } from 'lucide-react';
import { useApi } from '../hooks/useApi';

interface Element {
  element_id: number;
  element_type: string;
  content: string;
}

interface DocumentDetail {
  file_name: string;
  doc_id: string;
  total_elements: number;
  elements_by_type: Record<string, { element_id: number; content: string }[]>;
  elements_ordered: Element[];
}

interface Props {
  docId: string;
  onBack: () => void;
}

const TYPE_LABELS: Record<string, string> = {
  title: 'Titles',
  section_header: 'Section Headers',
  text: 'Text Blocks',
  page_header: 'Page Headers',
};

const TYPE_ORDER = ['title', 'section_header', 'text', 'page_header'];

export default function DocumentViewer({ docId, onBack }: Props) {
  const { data, loading, error } = useApi<DocumentDetail>(`/api/documents/${docId}`);
  const [viewMode, setViewMode] = useState<'ordered' | 'grouped'>('ordered');

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        Loading document...
      </div>
    );
  }

  if (error) {
    return <div className="error-message">Failed to load document: {error}</div>;
  }

  if (!data) return null;

  return (
    <div className="doc-viewer">
      <div className="doc-viewer-header">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={16} />
          Back
        </button>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--navy)' }}>
            <FileText size={20} style={{ marginRight: 8, verticalAlign: 'middle' }} />
            {data.file_name}
          </h2>
          <p style={{ fontSize: 13, color: 'var(--slate)', marginTop: 2 }}>
            {data.total_elements} elements | Doc ID: {data.doc_id.slice(0, 8)}...
          </p>
        </div>
        <div className="view-toggle">
          <button
            className={viewMode === 'ordered' ? 'active' : ''}
            onClick={() => setViewMode('ordered')}
          >
            Sequential
          </button>
          <button
            className={viewMode === 'grouped' ? 'active' : ''}
            onClick={() => setViewMode('grouped')}
          >
            By Type
          </button>
        </div>
      </div>

      {/* Element type summary badges */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {TYPE_ORDER.filter((t) => data.elements_by_type[t]).map((t) => (
          <span key={t} className={`badge ${t === 'title' ? 'gold' : t === 'section_header' ? 'blue' : t === 'text' ? 'green' : 'gray'}`}>
            {TYPE_LABELS[t] || t}: {data.elements_by_type[t].length}
          </span>
        ))}
      </div>

      {viewMode === 'ordered' ? (
        <div className="card">
          <div className="card-body">
            {data.elements_ordered.map((el) => (
              <div key={el.element_id} className={`element-card ${el.element_type}`}>
                <span className="element-number">{el.element_id}</span>
                {el.content}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
          {TYPE_ORDER.filter((t) => data.elements_by_type[t]).map((t) => (
            <div key={t} className="card">
              <div className="card-header">
                <h3>{TYPE_LABELS[t] || t}</h3>
                <span className="badge gray">{data.elements_by_type[t].length}</span>
              </div>
              <div className="card-body">
                {data.elements_by_type[t].map((el) => (
                  <div key={el.element_id} className={`element-card ${t}`}>
                    <span className="element-number">{el.element_id}</span>
                    {el.content}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
