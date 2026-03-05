import { useState, useEffect } from 'react';
import { AlertTriangle, DollarSign, Users, Calendar, MapPin, Shield, ChevronDown, ChevronUp } from 'lucide-react';

interface DollarAmount {
  description: string;
  amount: string;
}

interface DocumentExtraction {
  file_name: string;
  document_type: string;
  parties: string[];
  effective_date: string | null;
  termination_date: string | null;
  governing_law: string | null;
  key_dollar_amounts: DollarAmount[];
  confidentiality_period: string | null;
  termination_notice_period: string | null;
  non_compete_duration: string | null;
  key_obligations: string[];
  risk_flags: string[];
}

function KeyInsightsPage() {
  const [documents, setDocuments] = useState<DocumentExtraction[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedDoc, setExpandedDoc] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/extraction')
      .then((r) => r.json())
      .then((data) => {
        setDocuments(data.documents || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading extracted insights...</div>;

  const toggleDoc = (fileName: string) => {
    setExpandedDoc(expandedDoc === fileName ? null : fileName);
  };

  const totalRisks = documents.reduce((sum, d) => sum + (d.risk_flags?.length || 0), 0);
  const totalAmounts = documents.reduce((sum, d) => sum + (d.key_dollar_amounts?.length || 0), 0);
  const allParties = new Set(documents.flatMap(d => d.parties || []));

  return (
    <div className="page-content">
      <h2 style={{ marginBottom: 8 }}>Key Insights</h2>
      <p style={{ color: '#666', marginBottom: 24 }}>AI-extracted structured data from legal documents using <code>ai_query</code></p>

      {/* Summary cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        <div className="stat-card">
          <div style={{ fontSize: 28, fontWeight: 700, color: '#1a365d' }}>{documents.length}</div>
          <div style={{ color: '#666', fontSize: 13 }}>Documents Analyzed</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: 28, fontWeight: 700, color: '#2563eb' }}>{allParties.size}</div>
          <div style={{ color: '#666', fontSize: 13 }}>Unique Parties</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: 28, fontWeight: 700, color: '#059669' }}>{totalAmounts}</div>
          <div style={{ color: '#666', fontSize: 13 }}>Dollar Amounts Found</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: 28, fontWeight: 700, color: '#dc2626' }}>{totalRisks}</div>
          <div style={{ color: '#666', fontSize: 13 }}>Risk Flags Identified</div>
        </div>
      </div>

      {/* Document cards */}
      {documents.map((doc) => {
        const isExpanded = expandedDoc === doc.file_name;
        return (
          <div key={doc.file_name} className="card" style={{ marginBottom: 16 }}>
            {/* Header */}
            <div
              onClick={() => toggleDoc(doc.file_name)}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
                padding: '16px 20px',
                borderBottom: isExpanded ? '1px solid #e5e7eb' : 'none',
              }}
            >
              <div>
                <span
                  style={{
                    display: 'inline-block',
                    padding: '2px 10px',
                    borderRadius: 4,
                    fontSize: 11,
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: 0.5,
                    background: '#dbeafe',
                    color: '#1e40af',
                    marginRight: 12,
                  }}
                >
                  {doc.document_type}
                </span>
                <span style={{ fontWeight: 600, color: '#1a365d' }}>{doc.file_name}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                {(doc.risk_flags?.length || 0) > 0 && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: '#dc2626', fontSize: 13 }}>
                    <AlertTriangle size={14} /> {doc.risk_flags.length} risks
                  </span>
                )}
                {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </div>
            </div>

            {/* Expanded content */}
            {isExpanded && (
              <div style={{ padding: 20 }}>
                {/* Key facts grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <Users size={16} style={{ color: '#2563eb', marginTop: 2, flexShrink: 0 }} />
                    <div>
                      <div style={{ fontSize: 11, fontWeight: 600, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5 }}>Parties</div>
                      <div style={{ fontSize: 14 }}>{doc.parties?.join(' & ') || 'N/A'}</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <MapPin size={16} style={{ color: '#7c3aed', marginTop: 2, flexShrink: 0 }} />
                    <div>
                      <div style={{ fontSize: 11, fontWeight: 600, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5 }}>Governing Law</div>
                      <div style={{ fontSize: 14 }}>{doc.governing_law || 'Not specified'}</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <Calendar size={16} style={{ color: '#059669', marginTop: 2, flexShrink: 0 }} />
                    <div>
                      <div style={{ fontSize: 11, fontWeight: 600, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5 }}>Effective Date</div>
                      <div style={{ fontSize: 14 }}>{doc.effective_date || 'N/A'}</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <Calendar size={16} style={{ color: '#dc2626', marginTop: 2, flexShrink: 0 }} />
                    <div>
                      <div style={{ fontSize: 11, fontWeight: 600, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5 }}>Termination</div>
                      <div style={{ fontSize: 14 }}>{doc.termination_date || doc.termination_notice_period || 'N/A'}</div>
                    </div>
                  </div>
                </div>

                {/* Additional terms */}
                {(doc.confidentiality_period || doc.non_compete_duration) && (
                  <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
                    {doc.confidentiality_period && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Shield size={14} style={{ color: '#6b7280' }} />
                        <span style={{ fontSize: 13, color: '#4b5563' }}>
                          <strong>Confidentiality:</strong> {doc.confidentiality_period}
                        </span>
                      </div>
                    )}
                    {doc.non_compete_duration && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Shield size={14} style={{ color: '#6b7280' }} />
                        <span style={{ fontSize: 13, color: '#4b5563' }}>
                          <strong>Non-compete:</strong> {doc.non_compete_duration}
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* Dollar amounts */}
                {doc.key_dollar_amounts?.length > 0 && (
                  <div style={{ marginBottom: 20 }}>
                    <h4 style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8, color: '#059669' }}>
                      <DollarSign size={16} /> Financial Terms
                    </h4>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                      <thead>
                        <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                          <th style={{ textAlign: 'left', padding: '6px 12px', color: '#6b7280', fontWeight: 600 }}>Description</th>
                          <th style={{ textAlign: 'right', padding: '6px 12px', color: '#6b7280', fontWeight: 600 }}>Amount</th>
                        </tr>
                      </thead>
                      <tbody>
                        {doc.key_dollar_amounts.map((amt, i) => (
                          <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
                            <td style={{ padding: '8px 12px' }}>{amt.description}</td>
                            <td style={{ padding: '8px 12px', textAlign: 'right', fontWeight: 600, fontFamily: 'monospace' }}>{amt.amount}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Key obligations */}
                {doc.key_obligations?.length > 0 && (
                  <div style={{ marginBottom: 20 }}>
                    <h4 style={{ marginBottom: 8, color: '#1a365d' }}>Key Obligations</h4>
                    <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13, lineHeight: 1.8 }}>
                      {doc.key_obligations.map((ob, i) => (
                        <li key={i} style={{ color: '#374151' }}>{ob}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Risk flags */}
                {doc.risk_flags?.length > 0 && (
                  <div>
                    <h4 style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8, color: '#dc2626' }}>
                      <AlertTriangle size={16} /> Risk Flags
                    </h4>
                    {doc.risk_flags.map((flag, i) => (
                      <div
                        key={i}
                        style={{
                          padding: '10px 14px',
                          marginBottom: 8,
                          background: '#fef2f2',
                          border: '1px solid #fecaca',
                          borderRadius: 6,
                          fontSize: 13,
                          color: '#991b1b',
                          lineHeight: 1.5,
                        }}
                      >
                        {flag}
                      </div>
                    ))}
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

export default KeyInsightsPage;
