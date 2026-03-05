import { useState, useEffect } from 'react';
import { Building, Calendar, Shield } from 'lucide-react';

interface Regulatory {
  file_name: string;
  regulation_id: string;
  issuing_agency: string;
  document_type: string;
  effective_date: string;
  affected_entities: string[] | string;
  compliance_requirements: string[] | string;
  penalties: string[] | string;
  comment_period_deadline: string | null;
  summary: string;
}

function RegulatoryPage() {
  const [filings, setFilings] = useState<Regulatory[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/specialized/regulatory')
      .then((r) => r.json())
      .then((data) => {
        setFilings(data.documents || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const parseArr = (val: unknown): string[] => {
    if (Array.isArray(val)) return val;
    if (typeof val === 'string') { try { return JSON.parse(val); } catch { return []; } }
    return [];
  };

  if (loading) return <div className="page-content"><p>Loading regulatory filings...</p></div>;

  const docTypes = [...new Set(filings.map((f) => f.document_type))];
  const agencies = [...new Set(filings.map((f) => f.issuing_agency))];

  return (
    <div className="page-content">
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: 'var(--navy)', marginBottom: 4 }}>
          Regulatory Filings
        </h2>
        <p style={{ fontSize: 14, color: 'var(--slate)' }}>
          AI-extracted metadata from {filings.length} regulatory filings across {agencies.length} agencies.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-value">{filings.length}</div>
          <div className="stat-label">Total Filings</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{agencies.length}</div>
          <div className="stat-label">Agencies</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{docTypes.length}</div>
          <div className="stat-label">Document Types</div>
        </div>
      </div>

      {filings.map((f) => {
        const entities = parseArr(f.affected_entities);
        const requirements = parseArr(f.compliance_requirements);
        const penalties = parseArr(f.penalties);
        const isExpanded = expanded === f.file_name;

        return (
          <div
            key={f.file_name}
            className="card"
            style={{ padding: 20, marginBottom: 12, cursor: 'pointer' }}
            onClick={() => setExpanded(isExpanded ? null : f.file_name)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontSize: 11, color: 'var(--slate)', marginBottom: 4 }}>
                  {f.file_name}
                </div>
                <h4 style={{ fontSize: 15, fontWeight: 600, color: 'var(--navy)', marginBottom: 6 }}>
                  {f.regulation_id}
                </h4>
                <div style={{ display: 'flex', gap: 16, fontSize: 13, color: 'var(--gray-700)' }}>
                  <span><Building size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />{f.issuing_agency}</span>
                  <span><Calendar size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />Effective: {f.effective_date}</span>
                </div>
              </div>
              <span style={{
                padding: '4px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600,
                background: f.document_type?.includes('Enforcement') ? '#fef2f2' : f.document_type?.includes('Proposed') ? '#fffbeb' : '#f0fdf4',
                color: f.document_type?.includes('Enforcement') ? '#dc2626' : f.document_type?.includes('Proposed') ? '#d97706' : '#16a34a',
                border: `1px solid ${f.document_type?.includes('Enforcement') ? '#fecaca' : f.document_type?.includes('Proposed') ? '#fde68a' : '#bbf7d0'}`
              }}>
                {f.document_type}
              </span>
            </div>

            {isExpanded && (
              <div style={{ marginTop: 16, borderTop: '1px solid var(--gray-200)', paddingTop: 16 }}>
                {f.summary && (
                  <div style={{ marginBottom: 16 }}>
                    <strong style={{ color: 'var(--navy)', fontSize: 13 }}>Summary</strong>
                    <p style={{ fontSize: 13, color: 'var(--gray-700)', marginTop: 4, lineHeight: 1.6 }}>{f.summary}</p>
                  </div>
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, fontSize: 13, marginBottom: 16 }}>
                  <div>
                    <strong style={{ color: 'var(--navy)' }}>Affected Entities</strong>
                    <ul style={{ margin: '6px 0', paddingLeft: 18, color: 'var(--gray-700)' }}>
                      {entities.map((e, i) => <li key={i} style={{ marginBottom: 3 }}>{e}</li>)}
                    </ul>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--navy)' }}>
                      <Shield size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />Penalties
                    </strong>
                    <ul style={{ margin: '6px 0', paddingLeft: 18, color: '#dc2626' }}>
                      {penalties.map((p, i) => <li key={i} style={{ marginBottom: 3 }}>{p}</li>)}
                    </ul>
                  </div>
                </div>

                <div>
                  <strong style={{ color: 'var(--navy)', fontSize: 13 }}>Compliance Requirements</strong>
                  <ul style={{ margin: '6px 0', paddingLeft: 18, fontSize: 13, color: 'var(--gray-700)' }}>
                    {requirements.map((r, i) => <li key={i} style={{ marginBottom: 4 }}>{r}</li>)}
                  </ul>
                </div>

                {f.comment_period_deadline && (
                  <div style={{ marginTop: 12, padding: '8px 12px', borderRadius: 6, background: '#fffbeb', fontSize: 13, color: '#92400e' }}>
                    Comment period deadline: <strong>{f.comment_period_deadline}</strong>
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

export default RegulatoryPage;
