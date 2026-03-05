import { useState, useEffect } from 'react';
import { AlertTriangle, DollarSign, Clock } from 'lucide-react';

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

function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/specialized/invoices')
      .then((r) => r.json())
      .then((data) => {
        setInvoices(data.documents || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const parseArr = (val: unknown): unknown[] => {
    if (Array.isArray(val)) return val;
    if (typeof val === 'string') { try { return JSON.parse(val); } catch { return []; } }
    return [];
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
          AI-extracted billing data and compliance flags from {invoices.length} outside counsel invoices.
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
          <div className="stat-value">{new Set(invoices.map((i) => i.law_firm)).size}</div>
          <div className="stat-label">Law Firms</div>
        </div>
      </div>

      {invoices.map((inv) => {
        const flags = parseArr(inv.compliance_flags) as ComplianceFlag[];
        const items = parseArr(inv.line_items) as LineItem[];
        const isExpanded = expanded === inv.file_name;

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
              {flags.length > 0 && (
                <span style={{ padding: '4px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600, background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' }}>
                  <AlertTriangle size={12} style={{ verticalAlign: 'middle', marginRight: 3 }} /> {flags.length} flag{flags.length > 1 ? 's' : ''}
                </span>
              )}
            </div>

            {isExpanded && (
              <div style={{ marginTop: 16, borderTop: '1px solid var(--gray-200)', paddingTop: 16 }}>
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
