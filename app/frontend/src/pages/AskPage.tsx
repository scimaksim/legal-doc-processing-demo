import { useState } from 'react';
import { Send, Database, MessageSquare, Loader2 } from 'lucide-react';

interface QueryResult {
  question: string;
  sql?: string;
  columns?: string[];
  rows?: string[][];
  row_count?: number;
  error?: string;
}

const SAMPLE_QUESTIONS = [
  "Which documents have non-compete clauses longer than 12 months?",
  "List all parties involved in NDAs",
  "What are the total dollar amounts across all software license agreements?",
  "Which documents are governed by California law?",
  "Show all risk flags for employment agreements",
  "Which leases have security deposits over $200,000?",
  "Find documents with termination notice periods of 90 days or more",
  "How many documents of each type do we have?",
];

function AskPage() {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<QueryResult[]>([]);
  const [loading, setLoading] = useState(false);

  const askQuestion = async (q?: string) => {
    const query = q || question;
    if (!query.trim()) return;

    setLoading(true);
    setQuestion('');

    try {
      const res = await fetch('/api/nlquery', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query }),
      });
      const data = await res.json();
      setHistory((prev) => [data, ...prev]);
    } catch (err) {
      setHistory((prev) => [
        { question: query, error: 'Failed to connect to server' },
        ...prev,
      ]);
    }
    setLoading(false);
  };

  return (
    <div className="page-content">
      <h2 style={{ marginBottom: 4 }}>Ask Your Documents</h2>
      <p style={{ color: '#666', marginBottom: 24, fontSize: 14 }}>
        Ask natural language questions about your legal document portfolio. Powered by AI-generated SQL over your extracted data.
      </p>

      {/* Input */}
      <div
        style={{
          display: 'flex',
          gap: 8,
          marginBottom: 24,
          position: 'sticky',
          top: 0,
          background: 'var(--off-white)',
          paddingTop: 4,
          paddingBottom: 12,
          zIndex: 10,
        }}
      >
        <input
          type="text"
          className="search-input"
          style={{ paddingLeft: 18 }}
          placeholder="Ask a question about your legal documents..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && askQuestion()}
          disabled={loading}
        />
        <button
          onClick={() => askQuestion()}
          disabled={loading || !question.trim()}
          style={{
            padding: '12px 20px',
            background: loading ? 'var(--gray-300)' : 'var(--navy)',
            color: 'white',
            border: 'none',
            borderRadius: 'var(--radius-lg)',
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontWeight: 600,
            fontSize: 14,
            flexShrink: 0,
          }}
        >
          {loading ? <Loader2 size={16} className="spinning" /> : <Send size={16} />}
          Ask
        </button>
      </div>

      {/* Sample questions */}
      {history.length === 0 && (
        <div style={{ marginBottom: 32 }}>
          <h4 style={{ fontSize: 13, fontWeight: 600, color: 'var(--slate)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>
            Try these questions
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {SAMPLE_QUESTIONS.map((sq) => (
              <button
                key={sq}
                onClick={() => { setQuestion(sq); askQuestion(sq); }}
                style={{
                  padding: '8px 14px',
                  borderRadius: 100,
                  border: '1px solid var(--gray-200)',
                  background: 'white',
                  color: 'var(--gray-700)',
                  fontSize: 13,
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
                onMouseEnter={(e) => {
                  (e.target as HTMLElement).style.borderColor = 'var(--gold)';
                  (e.target as HTMLElement).style.background = 'rgba(200,160,74,0.05)';
                }}
                onMouseLeave={(e) => {
                  (e.target as HTMLElement).style.borderColor = 'var(--gray-200)';
                  (e.target as HTMLElement).style.background = 'white';
                }}
              >
                {sq}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="card" style={{ padding: 24, marginBottom: 16, textAlign: 'center', color: 'var(--slate)' }}>
          <Loader2 size={24} style={{ animation: 'spin 1s linear infinite', marginBottom: 8 }} />
          <div>Generating and executing SQL query...</div>
        </div>
      )}

      {/* Results history */}
      {history.map((result, idx) => (
        <div key={idx} className="card" style={{ marginBottom: 16 }}>
          {/* Question */}
          <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--gray-200)', display: 'flex', alignItems: 'center', gap: 10 }}>
            <MessageSquare size={16} style={{ color: 'var(--gold)', flexShrink: 0 }} />
            <span style={{ fontWeight: 600, color: 'var(--navy)' }}>{result.question}</span>
          </div>

          {/* Error */}
          {result.error && (
            <div style={{ padding: 20, color: 'var(--red)', fontSize: 14 }}>
              {result.error}
            </div>
          )}

          {/* SQL */}
          {result.sql && (
            <div style={{ padding: '12px 20px', borderBottom: '1px solid var(--gray-200)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6, color: 'var(--slate)', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                <Database size={12} /> Generated SQL
              </div>
              <pre style={{
                background: 'var(--navy-dark)',
                color: '#e2e8f0',
                padding: '12px 16px',
                borderRadius: 'var(--radius)',
                fontSize: 12,
                lineHeight: 1.5,
                overflow: 'auto',
                maxHeight: 200,
                whiteSpace: 'pre-wrap',
              }}>
                {result.sql}
              </pre>
            </div>
          )}

          {/* Results table */}
          {result.columns && result.rows && (
            <div style={{ padding: 20 }}>
              <div style={{ fontSize: 12, color: 'var(--slate)', marginBottom: 8 }}>
                {result.row_count} result{result.row_count !== 1 ? 's' : ''}
              </div>
              <div style={{ overflow: 'auto', maxHeight: 400 }}>
                <table className="comparison-table">
                  <thead>
                    <tr>
                      {result.columns.map((col) => (
                        <th key={col}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.rows.map((row, ri) => (
                      <tr key={ri}>
                        {row.map((cell, ci) => (
                          <td key={ci} style={{ maxWidth: 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default AskPage;
