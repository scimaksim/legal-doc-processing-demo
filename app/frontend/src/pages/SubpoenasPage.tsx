import { useState, useEffect } from 'react';
import { AlertTriangle, Calendar, Users, Building2, CheckCircle2, Clock, UserPlus } from 'lucide-react';

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

interface TrackingItem {
  id: string;
  file_name: string;
  case_number: string;
  status: string;
  assigned_to: string;
  priority: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const STATUS_COLORS: Record<string, { bg: string; color: string; border: string }> = {
  New: { bg: '#eff6ff', color: '#2563eb', border: '#bfdbfe' },
  'In Review': { bg: '#fffbeb', color: '#d97706', border: '#fde68a' },
  Producing: { bg: '#f0fdf4', color: '#16a34a', border: '#bbf7d0' },
  Produced: { bg: '#f0fdf4', color: '#065f46', border: '#a7f3d0' },
  Overdue: { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
};

function SubpoenasPage() {
  const [subpoenas, setSubpoenas] = useState<Subpoena[]>([]);
  const [tracking, setTracking] = useState<TrackingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [showTracking, setShowTracking] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch('/api/specialized/subpoenas').then((r) => r.json()),
      fetch('/api/ops/subpoena-tracking').then((r) => r.json()),
    ]).then(([subData, trackData]) => {
      setSubpoenas(subData.documents || []);
      setTracking(trackData.items || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const getTrackingStatus = (fileName: string) => {
    return tracking.find((t) => t.file_name === fileName);
  };

  const startTracking = async (s: Subpoena) => {
    const res = await fetch('/api/ops/subpoena-tracking', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_name: s.file_name, case_number: s.case_number, status: 'New', priority: 'Normal' }),
    });
    const data = await res.json();
    setTracking([...tracking, { id: data.id, file_name: s.file_name, case_number: s.case_number, status: 'New', assigned_to: '', priority: 'Normal', notes: '', created_at: new Date().toISOString(), updated_at: new Date().toISOString() }]);
  };

  const updateTracking = async (id: string, updates: Record<string, string>) => {
    await fetch(`/api/ops/subpoena-tracking/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    setTracking(tracking.map((t) => t.id === id ? { ...t, ...updates } : t));
  };

  if (loading) return <div className="page-content"><p>Loading subpoenas...</p></div>;

  return (
    <div className="page-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: 'var(--navy)', marginBottom: 4 }}>
            Subpoena Tracker
          </h2>
          <p style={{ fontSize: 14, color: 'var(--slate)' }}>
            AI-extracted metadata from {subpoenas.length} subpoenas with operational tracking via Lakebase.
          </p>
        </div>
        <button
          onClick={() => setShowTracking(!showTracking)}
          style={{
            padding: '8px 16px', borderRadius: 6, fontSize: 13, fontWeight: 600, cursor: 'pointer',
            background: showTracking ? 'var(--navy)' : 'white',
            color: showTracking ? 'white' : 'var(--navy)',
            border: '1px solid var(--navy)',
          }}
        >
          {showTracking ? 'Show All' : 'Show Tracked Only'}
        </button>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-value">{subpoenas.length}</div>
          <div className="stat-label">Total Subpoenas</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{tracking.length}</div>
          <div className="stat-label">Being Tracked</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{tracking.filter((t) => t.status === 'New').length}</div>
          <div className="stat-label">New / Unassigned</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#dc2626' }}>{subpoenas.filter((s) => s.preservation_required === 'true').length}</div>
          <div className="stat-label">Preservation Required</div>
        </div>
      </div>

      {/* Lakebase badge */}
      <div style={{ padding: '8px 14px', borderRadius: 6, background: '#eff6ff', border: '1px solid #bfdbfe', fontSize: 12, color: '#1e40af', marginBottom: 16, display: 'inline-block' }}>
        Operational state backed by <strong>Lakebase</strong> (OLTP) &middot; Extracted data from <strong>Delta Tables</strong> (Analytics)
      </div>

      {subpoenas
        .filter((s) => !showTracking || getTrackingStatus(s.file_name))
        .map((s) => {
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
        const tracked = getTrackingStatus(s.file_name);
        const statusStyle = tracked ? STATUS_COLORS[tracked.status] || STATUS_COLORS['New'] : null;

        return (
          <div
            key={s.file_name}
            className="card"
            style={{ padding: 20, marginBottom: 12, cursor: 'pointer' }}
            onClick={() => setExpanded(isExpanded ? null : s.file_name)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 11, color: 'var(--slate)', marginBottom: 4 }}>
                  {s.file_name}
                </div>
                <h4 style={{ fontSize: 15, fontWeight: 600, color: 'var(--navy)', marginBottom: 6 }}>
                  Case {s.case_number}
                </h4>
                <div style={{ display: 'flex', gap: 16, fontSize: 13, color: 'var(--gray-700)', flexWrap: 'wrap' }}>
                  <span><Building2 size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />{s.court_jurisdiction}</span>
                  <span><Calendar size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />Deadline: {s.production_deadline}</span>
                  <span><Users size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />{custodians.length} custodians</span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                {s.preservation_required === 'true' && (
                  <span style={{ padding: '4px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600, background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' }}>
                    <AlertTriangle size={12} style={{ verticalAlign: 'middle', marginRight: 3 }} /> Preservation
                  </span>
                )}
                {tracked ? (
                  <span style={{ padding: '4px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600, background: statusStyle?.bg, color: statusStyle?.color, border: `1px solid ${statusStyle?.border}` }}>
                    {tracked.status}
                  </span>
                ) : (
                  <button
                    onClick={(e) => { e.stopPropagation(); startTracking(s); }}
                    style={{ padding: '4px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600, background: 'var(--gray-100)', color: 'var(--gray-700)', border: '1px solid var(--gray-200)', cursor: 'pointer' }}
                  >
                    + Track
                  </button>
                )}
              </div>
            </div>

            {isExpanded && (
              <div style={{ marginTop: 16, borderTop: '1px solid var(--gray-200)', paddingTop: 16 }}>
                {/* Tracking controls */}
                {tracked && (
                  <div style={{ padding: 14, borderRadius: 8, background: '#f8fafc', border: '1px solid var(--gray-200)', marginBottom: 16 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--navy)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                      Workflow Status (Lakebase)
                    </div>
                    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
                      <select
                        value={tracked.status}
                        onChange={(e) => updateTracking(tracked.id, { status: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--gray-200)', fontSize: 13 }}
                      >
                        {Object.keys(STATUS_COLORS).map((s) => <option key={s} value={s}>{s}</option>)}
                      </select>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <UserPlus size={14} color="var(--slate)" />
                        <input
                          type="text"
                          placeholder="Assign to..."
                          value={tracked.assigned_to}
                          onChange={(e) => updateTracking(tracked.id, { assigned_to: e.target.value })}
                          onClick={(e) => e.stopPropagation()}
                          style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--gray-200)', fontSize: 13, width: 150 }}
                        />
                      </div>
                      <select
                        value={tracked.priority}
                        onChange={(e) => updateTracking(tracked.id, { priority: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--gray-200)', fontSize: 13 }}
                      >
                        <option value="Low">Low Priority</option>
                        <option value="Normal">Normal Priority</option>
                        <option value="High">High Priority</option>
                        <option value="Urgent">Urgent</option>
                      </select>
                    </div>
                  </div>
                )}

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
