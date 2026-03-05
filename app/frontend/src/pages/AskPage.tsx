import { useState } from 'react';
import { Send, Database, MessageSquare, Loader2, Sparkles, Cpu } from 'lucide-react';

interface QueryResult {
  question: string;
  sql?: string;
  columns?: string[];
  rows?: string[][];
  row_count?: number;
  error?: string;
  text_response?: string;
  source?: string;
}

const SAMPLE_QUESTIONS = [
  "Which documents have non-compete clauses longer than 12 months?",
  "Show all invoices with compliance flags",
  "Which subpoenas have production deadlines in the next 30 days?",
  "List all parties involved in NDAs",
  "Which documents are governed by California law?",
  "What regulatory filings affect consumer lending?",
  "Which invoices have the highest hourly rates?",
  "How many documents of each type do we have?",
];

function AskPage() {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<QueryResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<'genie' | 'ai_query'>('genie');

  const askQuestion = async (q?: string) => {
    const query = q || question;
    if (!query.trim()) return;

    setLoading(true);
    setQuestion('');

    const endpoint = mode === 'genie' ? '/api/genie/ask' : '/api/nlquery';

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query }),
      });
      const data = await res.json();
      data.source = mode;
      setHistory((prev) => [data, ...prev]);
    } catch (err) {
      setHistory((prev) => [
        { question: query, error: 'Failed to connect to server', source: mode },
        ...prev,
      ]);
    }
    setLoading(false);
  };

  return (
    <div className="page-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h2 style={{ marginBottom: 4 }}>Ask Your Documents</h2>
          <p style={{ color: '#666', fontSize: 14 }}>
            Ask natural language questions about your legal document portfolio.
          </p>
        </div>
        {/* Mode toggle */}
        <div style={{ display: 'flex', borderRadius: 8, border: '1px solid var(--gray-200)', overflow: 'hidden' }}>
          <button
            onClick={() => setMode('genie')}
            style={{
              padding: '8px 16px', fontSize: 12, fontWeight: 600, border: 'none', cursor: 'pointer',
              background: mode === 'genie' ? 'var(--navy)' : 'white',
              color: mode === 'genie' ? 'white' : 'var(--gray-700)',
              display: 'flex', alignItems: 'center', gap: 4,
            }}
          >
            <Sparkles size={13} /> Genie
          </button>
          <button
            onClick={() => setMode('ai_query')}
            style={{
              padding: '8px 16px', fontSize: 12, fontWeight: 600, border: 'none', cursor: 'pointer',
              borderLeft: '1px solid var(--gray-200)',
              background: mode === 'ai_query' ? 'var(--navy)' : 'white',
              color: mode === 'ai_query' ? 'white' : 'var(--gray-700)',
              display: 'flex', alignItems: 'center', gap: 4,
            }}
          >
            <Cpu size={13} /> ai_query
          </button>
        </div>
      </div>

      <div style={{ padding: '6px 12px', borderRadius: 6, background: mode === 'genie' ? '#eff6ff' : 'rgba(200,160,74,0.1)', fontSize: 12, marginBottom: 16, display: 'inline-block',
        color: mode === 'genie' ? '#1e40af' : 'var(--gold-dark)', border: `1px solid ${mode === 'genie' ? '#bfdbfe' : 'rgba(200,160,74,0.3)'}` }}>
        {mode === 'genie'
          ? 'Using Genie Conversation API — optimized NL-to-SQL with table context'
          : 'Using ai_query() with Foundation Model — direct text-to-SQL generation'}
      </div>

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
          <div>{mode === 'genie' ? 'Asking Genie...' : 'Generating and executing SQL query...'}</div>
        </div>
      )}

      {/* Results history */}
      {history.map((result, idx) => (
        <div key={idx} className="card" style={{ marginBottom: 16 }}>
          {/* Question */}
          <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--gray-200)', display: 'flex', alignItems: 'center', gap: 10 }}>
            <MessageSquare size={16} style={{ color: 'var(--gold)', flexShrink: 0 }} />
            <span style={{ fontWeight: 600, color: 'var(--navy)', flex: 1 }}>{result.question}</span>
            <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 100, background: result.source === 'genie' ? '#eff6ff' : 'rgba(200,160,74,0.1)',
              color: result.source === 'genie' ? '#2563eb' : 'var(--gold-dark)', fontWeight: 600 }}>
              {result.source === 'genie' ? 'Genie' : 'ai_query'}
            </span>
          </div>

          {/* Text response from Genie */}
          {result.text_response && (
            <div style={{ padding: '12px 20px', borderBottom: '1px solid var(--gray-200)', fontSize: 14, color: 'var(--gray-700)', lineHeight: 1.6 }}>
              {result.text_response}
            </div>
          )}

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
