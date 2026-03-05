import { useState, useEffect } from 'react';
import { AlertTriangle, Calendar, Users, Building2 } from 'lucide-react';

interface Subpoena {
  file_name: string;
  case_number: string;
  court_jurisdiction: string;
  requesting_party: string;
  responding_party: string;
  data_custodians: string[] | string;
  date_range_start: string;
  date_range_end: string;
  document_categories_requested: string[] | string;
  production_deadline: string;
  preservation_required: string;
  special_instructions: string;
}

function SubpoenasPage() {
  const [subpoenas, setSubpoenas] = useState<Subpoena[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/specialized/subpoenas')
      .then((r) => r.json())
      .then((data) => {
        setSubpoenas(data.documents || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-content"><p>Loading subpoenas...</p></div>;

  return (
    <div className="page-content">
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: 'var(--navy)', marginBottom: 4 }}>
          Subpoena Tracker
        </h2>
        <p style={{ fontSize: 14, color: 'var(--slate)' }}>
          AI-extracted metadata from {subpoenas.length} subpoenas — custodians, deadlines, and document requests.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-value">{subpoenas.length}</div>
          <div className="stat-label">Total Subpoenas</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {new Set(subpoenas.map((s) => s.court_jurisdiction)).size}
          </div>
          <div className="stat-label">Jurisdictions</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {subpoenas.filter((s) => s.preservation_required === 'true').length}
          </div>
          <div className="stat-label">Preservation Required</div>
        </div>
      </div>

      {subpoenas.map((s) => {
        const custodians = Array.isArray(s.data_custodians)
          ? s.data_custodians
          : typeof s.data_custodians === 'string'
            ? (() => { try { return JSON.parse(s.data_custodians); } catch { return []; } })()
            : [];
        const categories = Array.isArray(s.document_categories_requested)
          ? s.document_categories_requested
          : typeof s.document_categories_requested === 'string'
            ? (() => { try { return JSON.parse(s.document_categories_requested); } catch { return []; } })()
            : [];
        const isExpanded = expanded === s.file_name;

        return (
          <div
            key={s.file_name}
            className="card"
            style={{ padding: 20, marginBottom: 12, cursor: 'pointer' }}
            onClick={() => setExpanded(isExpanded ? null : s.file_name)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontSize: 11, color: 'var(--slate)', marginBottom: 4 }}>
                  {s.file_name}
                </div>
                <h4 style={{ fontSize: 15, fontWeight: 600, color: 'var(--navy)', marginBottom: 6 }}>
                  Case {s.case_number}
                </h4>
                <div style={{ display: 'flex', gap: 16, fontSize: 13, color: 'var(--gray-700)' }}>
                  <span><Building2 size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />{s.court_jurisdiction}</span>
                  <span><Calendar size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />Deadline: {s.production_deadline}</span>
                  <span><Users size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />{custodians.length} custodians</span>
                </div>
              </div>
              {s.preservation_required === 'true' && (
                <span style={{ padding: '4px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600, background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' }}>
                  <AlertTriangle size={12} style={{ verticalAlign: 'middle', marginRight: 3 }} /> Preservation
                </span>
              )}
            </div>

            {isExpanded && (
              <div style={{ marginTop: 16, borderTop: '1px solid var(--gray-200)', paddingTop: 16 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, fontSize: 13 }}>
                  <div>
                    <strong style={{ color: 'var(--navy)' }}>Requesting Party</strong>
                    <p style={{ color: 'var(--gray-700)' }}>{s.requesting_party}</p>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--navy)' }}>Responding Party</strong>
                    <p style={{ color: 'var(--gray-700)' }}>{s.responding_party}</p>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--navy)' }}>Date Range</strong>
                    <p style={{ color: 'var(--gray-700)' }}>{s.date_range_start} — {s.date_range_end}</p>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--navy)' }}>Data Custodians</strong>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                      {custodians.map((c: string) => (
                        <span key={c} style={{ padding: '2px 8px', borderRadius: 100, fontSize: 12, background: 'var(--gray-100)', color: 'var(--gray-700)' }}>{c}</span>
                      ))}
                    </div>
                  </div>
                </div>
                <div style={{ marginTop: 16 }}>
                  <strong style={{ color: 'var(--navy)', fontSize: 13 }}>Document Categories Requested</strong>
                  <ul style={{ margin: '8px 0', paddingLeft: 20, fontSize: 13, color: 'var(--gray-700)' }}>
                    {categories.map((cat: string, i: number) => <li key={i} style={{ marginBottom: 4 }}>{cat}</li>)}
                  </ul>
                </div>
                {s.special_instructions && (
                  <div style={{ marginTop: 12 }}>
                    <strong style={{ color: 'var(--navy)', fontSize: 13 }}>Special Instructions</strong>
                    <p style={{ fontSize: 13, color: 'var(--gray-700)', marginTop: 4 }}>{s.special_instructions}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default SubpoenasPage;
