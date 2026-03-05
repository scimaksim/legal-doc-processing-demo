import { useState, useCallback } from 'react';
import { Search, FileText } from 'lucide-react';

interface SearchResult {
  file_name: string;
  doc_id: string;
  element_id: string;
  element_type: string;
  content: string;
}

interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchResult[];
}

interface Props {
  onOpenDocument: (docId: string) => void;
}

export default function SearchPage({ onOpenDocument }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const doSearch = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/documents/search/${encodeURIComponent(query.trim())}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResults(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') doSearch();
  };

  const highlightMatch = (text: string, q: string) => {
    if (!q) return text;
    const regex = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, i) =>
      regex.test(part) ? <mark key={i}>{part}</mark> : part
    );
  };

  return (
    <div>
      <div className="page-header">
        <h2>Search Documents</h2>
        <p>Full-text search across all parsed legal document content</p>
      </div>

      <div className="search-container">
        <Search size={20} className="search-icon" />
        <input
          type="text"
          className="search-input"
          placeholder="Search for terms, clauses, parties, dates..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner" />
          Searching...
        </div>
      )}

      {error && <div className="error-message">Search failed: {error}</div>}

      {results && !loading && (
        <div>
          <p style={{ fontSize: 14, color: 'var(--slate)', marginBottom: 16 }}>
            Found <strong>{results.total_results}</strong> result{results.total_results !== 1 ? 's' : ''}{' '}
            for "{results.query}"
          </p>
          {results.results.map((r, i) => (
            <div key={i} className="search-result">
              <div className="result-file">
                <FileText size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                <span
                  style={{ cursor: 'pointer', textDecoration: 'underline' }}
                  onClick={() => onOpenDocument(r.doc_id)}
                >
                  {r.file_name}
                </span>
              </div>
              <div className="result-type">
                <span className={`badge ${r.element_type === 'title' ? 'gold' : r.element_type === 'section_header' ? 'blue' : 'green'}`} style={{ fontSize: 10 }}>
                  {r.element_type}
                </span>
                {' '}Element #{r.element_id}
              </div>
              <div className="result-content">
                {highlightMatch(r.content, results.query)}
              </div>
            </div>
          ))}
        </div>
      )}

      {!results && !loading && (
        <div style={{ textAlign: 'center', padding: 64, color: 'var(--slate)' }}>
          <Search size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
          <p>Enter a search term to find content across all documents</p>
        </div>
      )}
    </div>
  );
}
