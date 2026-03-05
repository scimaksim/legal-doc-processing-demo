import { useState, useEffect } from 'react';
import { AlertTriangle, DollarSign, Clock, CheckCircle2, XCircle } from 'lucide-react';

interface ComplianceFlag {
  flag_type: string;
  description: string;
}

interface LineItem {
  timekeeper_role: string;
  hours: string;
  rate: string;
  amount: string;
  description: string;
}

interface Invoice {
  file_name: string;
  invoice_number: string;
  law_firm: string;
  client: string;
  matter_number: string;
  billing_period: string;
  professional_services_total: string;
  expenses_total: string;
  invoice_total: string;
  line_items: LineItem[] | string;
  compliance_flags: ComplianceFlag[] | string;
  highest_hourly_rate: string;
  total_hours: string;
}

interface ReviewItem {
  id: string;
  file_name: string;
  invoice_number: string;
  review_status: string;
  reviewer: string;
  approved_amount: string;
  disputed_amount: string;
  reviewer_notes: string;
}

const REVIEW_COLORS: Record<string, { bg: string; color: string; border: string }> = {
  Pending: { bg: '#fffbeb', color: '#d97706', border: '#fde68a' },
  Approved: { bg: '#f0fdf4', color: '#16a34a', border: '#bbf7d0' },
  'Partially Approved': { bg: '#fefce8', color: '#a16207', border: '#fef08a' },
  Disputed: { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
  Paid: { bg: '#f0fdf4', color: '#065f46', border: '#a7f3d0' },
};

function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch('/api/specialized/invoices').then((r) => r.json()),
      fetch('/api/ops/invoice-reviews').then((r) => r.json()),
    ]).then(([invData, revData]) => {
      setInvoices(invData.documents || []);
      setReviews(revData.items || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const parseArr = (val: unknown): unknown[] => {
    if (Array.isArray(val)) return val;
    if (typeof val === 'string') { try { return JSON.parse(val); } catch { return []; } }
    return [];
  };

  const getReview = (fileName: string) => reviews.find((r) => r.file_name === fileName);

  const startReview = async (inv: Invoice) => {
    const res = await fetch('/api/ops/invoice-reviews', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_name: inv.file_name, invoice_number: inv.invoice_number, review_status: 'Pending' }),
    });
    const data = await res.json();
    setReviews([...reviews, { id: data.id, file_name: inv.file_name, invoice_number: inv.invoice_number, review_status: 'Pending', reviewer: '', approved_amount: '', disputed_amount: '', reviewer_notes: '' }]);
  };

  const updateReview = async (id: string, updates: Record<string, string>) => {
    await fetch(`/api/ops/invoice-reviews/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    setReviews(reviews.map((r) => r.id === id ? { ...r, ...updates } : r));
  };

  const totalFlagged = invoices.reduce((sum, inv) => sum + parseArr(inv.compliance_flags).length, 0);

  if (loading) return <div className="page-content"><p>Loading invoices...</p></div>;

  return (
    <div className="page-content">
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: 'var(--navy)', marginBottom: 4 }}>
          Invoice Auditor
        </h2>
        <p style={{ fontSize: 14, color: 'var(--slate)' }}>
          AI-extracted billing data, compliance flags, and review workflow from {invoices.length} outside counsel invoices.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-value">{invoices.length}</div>
          <div className="stat-label">Total Invoices</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: totalFlagged > 0 ? '#dc2626' : undefined }}>
            {totalFlagged}
          </div>
          <div className="stat-label">Compliance Flags</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{reviews.filter((r) => r.review_status === 'Approved' || r.review_status === 'Paid').length}</div>
          <div className="stat-label">Approved/Paid</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{reviews.filter((r) => r.review_status === 'Disputed').length}</div>
          <div className="stat-label">Disputed</div>
        </div>
      </div>

      <div style={{ padding: '8px 14px', borderRadius: 6, background: '#eff6ff', border: '1px solid #bfdbfe', fontSize: 12, color: '#1e40af', marginBottom: 16, display: 'inline-block' }}>
        Review workflow backed by <strong>Lakebase</strong> (OLTP) &middot; Billing data extracted via <strong>ai_query</strong> into <strong>Delta Tables</strong>
      </div>

      {invoices.map((inv) => {
        const flags = parseArr(inv.compliance_flags) as ComplianceFlag[];
        const items = parseArr(inv.line_items) as LineItem[];
        const isExpanded = expanded === inv.file_name;
        const review = getReview(inv.file_name);
        const reviewStyle = review ? REVIEW_COLORS[review.review_status] || REVIEW_COLORS['Pending'] : null;

        return (
          <div
            key={inv.file_name}
            className="card"
            style={{ padding: 20, marginBottom: 12, cursor: 'pointer', borderLeft: flags.length > 0 ? '3px solid #dc2626' : undefined }}
            onClick={() => setExpanded(isExpanded ? null : inv.file_name)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontSize: 11, color: 'var(--slate)', marginBottom: 4 }}>
                  {inv.file_name} &middot; {inv.invoice_number}
                </div>
                <h4 style={{ fontSize: 15, fontWeight: 600, color: 'var(--navy)', marginBottom: 6 }}>
                  {inv.law_firm}
                </h4>
                <div style={{ display: 'flex', gap: 16, fontSize: 13, color: 'var(--gray-700)' }}>
                  <span>Client: {inv.client}</span>
                  <span><DollarSign size={13} style={{ verticalAlign: 'middle' }} />{inv.invoice_total}</span>
                  <span><Clock size={13} style={{ verticalAlign: 'middle', marginRight: 3 }} />{inv.total_hours}h</span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                {flags.length > 0 && (
                  <span style={{ padding: '4px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600, background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' }}>
                    <AlertTriangle size={12} style={{ verticalAlign: 'middle', marginRight: 3 }} /> {flags.length} flag{flags.length > 1 ? 's' : ''}
                  </span>
                )}
                {review ? (
                  <span style={{ padding: '4px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600, background: reviewStyle?.bg, color: reviewStyle?.color, border: `1px solid ${reviewStyle?.border}` }}>
                    {review.review_status}
                  </span>
                ) : (
                  <button
                    onClick={(e) => { e.stopPropagation(); startReview(inv); }}
                    style={{ padding: '4px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600, background: 'var(--gray-100)', color: 'var(--gray-700)', border: '1px solid var(--gray-200)', cursor: 'pointer' }}
                  >
                    + Review
                  </button>
                )}
              </div>
            </div>

            {isExpanded && (
              <div style={{ marginTop: 16, borderTop: '1px solid var(--gray-200)', paddingTop: 16 }}>
                {/* Review controls */}
                {review && (
                  <div style={{ padding: 14, borderRadius: 8, background: '#f8fafc', border: '1px solid var(--gray-200)', marginBottom: 16 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--navy)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                      Review Status (Lakebase)
                    </div>
                    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
                      <select
                        value={review.review_status}
                        onChange={(e) => updateReview(review.id, { review_status: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--gray-200)', fontSize: 13 }}
                      >
                        {Object.keys(REVIEW_COLORS).map((s) => <option key={s} value={s}>{s}</option>)}
                      </select>
                      <input
                        type="text"
                        placeholder="Reviewer name..."
                        value={review.reviewer}
                        onChange={(e) => updateReview(review.id, { reviewer: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--gray-200)', fontSize: 13, width: 140 }}
                      />
                      <input
                        type="text"
                        placeholder="Notes..."
                        value={review.reviewer_notes}
                        onChange={(e) => updateReview(review.id, { reviewer_notes: e.target.value })}
                        onClick={(e) => e.stopPropagation()}
                        style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--gray-200)', fontSize: 13, flex: 1, minWidth: 200 }}
                      />
                    </div>
                  </div>
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, fontSize: 13, marginBottom: 16 }}>
                  <div><strong style={{ color: 'var(--navy)' }}>Matter</strong><p style={{ color: 'var(--gray-700)' }}>{inv.matter_number}</p></div>
                  <div><strong style={{ color: 'var(--navy)' }}>Period</strong><p style={{ color: 'var(--gray-700)' }}>{inv.billing_period}</p></div>
                  <div><strong style={{ color: 'var(--navy)' }}>Highest Rate</strong><p style={{ color: 'var(--gray-700)' }}>{inv.highest_hourly_rate}/hr</p></div>
                </div>

                {flags.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <strong style={{ color: '#dc2626', fontSize: 13, display: 'block', marginBottom: 8 }}>Compliance Flags</strong>
                    {flags.map((f, i) => (
                      <div key={i} style={{ padding: '8px 12px', borderRadius: 6, background: '#fef2f2', marginBottom: 6, fontSize: 13 }}>
                        <span style={{ fontWeight: 600, color: '#dc2626', marginRight: 8 }}>{f.flag_type}</span>
                        <span style={{ color: '#7f1d1d' }}>{f.description}</span>
                      </div>
                    ))}
                  </div>
                )}

                {items.length > 0 && (
                  <div>
                    <strong style={{ color: 'var(--navy)', fontSize: 13, display: 'block', marginBottom: 8 }}>Line Items ({items.length})</strong>
                    <div style={{ maxHeight: 300, overflowY: 'auto' }}>
                      <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
                        <thead>
                          <tr style={{ borderBottom: '1px solid var(--gray-200)', textAlign: 'left' }}>
                            <th style={{ padding: '6px 8px', color: 'var(--slate)' }}>Role</th>
                            <th style={{ padding: '6px 8px', color: 'var(--slate)' }}>Hours</th>
                            <th style={{ padding: '6px 8px', color: 'var(--slate)' }}>Rate</th>
                            <th style={{ padding: '6px 8px', color: 'var(--slate)' }}>Amount</th>
                            <th style={{ padding: '6px 8px', color: 'var(--slate)' }}>Description</th>
                          </tr>
                        </thead>
                        <tbody>
                          {items.map((item, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid var(--gray-100)' }}>
                              <td style={{ padding: '6px 8px', color: 'var(--gray-700)' }}>{item.timekeeper_role}</td>
                              <td style={{ padding: '6px 8px', color: 'var(--gray-700)' }}>{item.hours}</td>
                              <td style={{ padding: '6px 8px', color: 'var(--gray-700)' }}>{item.rate}</td>
                              <td style={{ padding: '6px 8px', color: 'var(--gray-700)' }}>{item.amount}</td>
                              <td style={{ padding: '6px 8px', color: 'var(--gray-700)', maxWidth: 300 }}>{item.description}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
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

export default InvoicesPage;
