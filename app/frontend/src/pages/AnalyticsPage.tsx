import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { BarChart3, ExternalLink, LayoutDashboard } from 'lucide-react';

interface DashboardEmbed {
  embed_url: string;
  dashboard_url: string;
  dashboard_id: string;
}

interface Overview {
  total_documents: number;
  total_doc_ids: number;
  total_elements: number;
  unique_element_types: number;
}

interface ElementDist {
  distribution: { element_type: string; count: number }[];
}

interface ContentStats {
  stats: {
    file_name: string;
    element_count: number;
    total_chars: number;
    avg_element_length: number;
    max_element_length: number;
  }[];
}

const BAR_COLORS = ['gold', 'blue', 'green', 'navy', 'slate'];

const TYPE_LABELS: Record<string, string> = {
  title: 'Title',
  section_header: 'Section Header',
  text: 'Text Block',
  page_header: 'Page Header',
};

export default function AnalyticsPage() {
  const [view, setView] = useState<'dashboard' | 'details'>('dashboard');
  const embed = useApi<DashboardEmbed>('/api/analytics/dashboard-embed');
  const overview = useApi<Overview>('/api/analytics/overview');
  const dist = useApi<ElementDist>('/api/analytics/element-distribution');
  const contentStats = useApi<ContentStats>('/api/analytics/content-stats');

  return (
    <div className="page-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h2 style={{ marginBottom: 4 }}>Analytics</h2>
          <p style={{ color: '#666', fontSize: 14 }}>
            AI/BI Dashboard powered by Databricks Lakeview
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {/* View toggle */}
          <div style={{ display: 'flex', borderRadius: 8, border: '1px solid var(--gray-200)', overflow: 'hidden' }}>
            <button
              onClick={() => setView('dashboard')}
              style={{
                padding: '8px 16px', fontSize: 12, fontWeight: 600, border: 'none', cursor: 'pointer',
                background: view === 'dashboard' ? 'var(--navy)' : 'white',
                color: view === 'dashboard' ? 'white' : 'var(--gray-700)',
                display: 'flex', alignItems: 'center', gap: 4,
              }}
            >
              <LayoutDashboard size={13} /> AI/BI Dashboard
            </button>
            <button
              onClick={() => setView('details')}
              style={{
                padding: '8px 16px', fontSize: 12, fontWeight: 600, border: 'none', cursor: 'pointer',
                borderLeft: '1px solid var(--gray-200)',
                background: view === 'details' ? 'var(--navy)' : 'white',
                color: view === 'details' ? 'white' : 'var(--gray-700)',
                display: 'flex', alignItems: 'center', gap: 4,
              }}
            >
              <BarChart3 size={13} /> Element Details
            </button>
          </div>
          {embed.data && (
            <a
              href={embed.data.dashboard_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                padding: '8px 14px', fontSize: 12, fontWeight: 600, borderRadius: 8,
                border: '1px solid var(--gray-200)', background: 'white', color: 'var(--navy)',
                textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4,
              }}
            >
              <ExternalLink size={13} /> Open in Databricks
            </a>
          )}
        </div>
      </div>

      {view === 'dashboard' && (
        <>
          {embed.loading && (
            <div className="loading"><div className="spinner" />Loading dashboard...</div>
          )}
          {embed.data && (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <iframe
                src={embed.data.embed_url}
                style={{
                  width: '100%',
                  height: 'calc(100vh - 180px)',
                  border: 'none',
                  minHeight: 600,
                }}
                title="Legal Document Intelligence Analytics"
              />
            </div>
          )}
          {embed.error && (
            <div className="card" style={{ padding: 24, textAlign: 'center' }}>
              <p style={{ color: 'var(--gray-700)', marginBottom: 12 }}>
                Unable to load embedded dashboard. View it directly in Databricks:
              </p>
              <a
                href={`https://fevm-classic-stable-tetifz.cloud.databricks.com/sql/dashboardsv3/01f118d438a118b2ac23e883dff6e16f`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  padding: '10px 20px', background: 'var(--navy)', color: 'white',
                  borderRadius: 8, textDecoration: 'none', fontWeight: 600, fontSize: 14,
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                }}
              >
                <ExternalLink size={14} /> Open Dashboard in Databricks
              </a>
            </div>
          )}
        </>
      )}

      {view === 'details' && (
        <>
          {/* Overview stats */}
          {overview.data && (
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">Documents</div>
                <div className="stat-value">{overview.data.total_documents}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Total Elements</div>
                <div className="stat-value">{overview.data.total_elements}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Element Types</div>
                <div className="stat-value">{overview.data.unique_element_types}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Avg Elements/Doc</div>
                <div className="stat-value">
                  {overview.data.total_documents > 0
                    ? Math.round(overview.data.total_elements / overview.data.total_documents)
                    : 0}
                </div>
              </div>
            </div>
          )}

          <div className="chart-grid">
            {/* Element type distribution */}
            {dist.data && (
              <div className="card">
                <div className="card-header">
                  <h3>Element Type Distribution</h3>
                </div>
                <div className="card-body">
                  <div className="bar-chart">
                    {dist.data.distribution.map((d, i) => {
                      const maxDist = Math.max(...(dist.data?.distribution.map((x) => x.count) || [1]));
                      return (
                        <div key={d.element_type} className="bar-row">
                          <div className="bar-label">{TYPE_LABELS[d.element_type] || d.element_type}</div>
                          <div className="bar-wrapper">
                            <div
                              className={`bar-fill ${BAR_COLORS[i % BAR_COLORS.length]}`}
                              style={{ width: `${(d.count / maxDist) * 100}%` }}
                            >
                              {d.count}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Content size comparison */}
            {contentStats.data && (
              <div className="card">
                <div className="card-header">
                  <h3>Document Size (Characters)</h3>
                </div>
                <div className="card-body">
                  <div className="bar-chart">
                    {contentStats.data.stats.map((s, i) => {
                      const maxChars = Math.max(...(contentStats.data?.stats.map((x) => x.total_chars) || [1]));
                      return (
                        <div key={s.file_name} className="bar-row">
                          <div className="bar-label">{s.file_name}</div>
                          <div className="bar-wrapper">
                            <div
                              className={`bar-fill ${BAR_COLORS[i % BAR_COLORS.length]}`}
                              style={{ width: `${(s.total_chars / maxChars) * 100}%` }}
                            >
                              {s.total_chars.toLocaleString()}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Content length stats table */}
          {contentStats.data && (
            <div className="card" style={{ marginTop: 20 }}>
              <div className="card-header">
                <h3>Content Length Statistics</h3>
              </div>
              <div className="card-body" style={{ padding: 0, overflowX: 'auto' }}>
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th>Document</th>
                      <th style={{ textAlign: 'center' }}>Elements</th>
                      <th style={{ textAlign: 'center' }}>Total Chars</th>
                      <th style={{ textAlign: 'center' }}>Avg Length</th>
                      <th style={{ textAlign: 'center' }}>Max Length</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contentStats.data.stats.map((s) => (
                      <tr key={s.file_name}>
                        <td style={{ fontWeight: 600 }}>{s.file_name}</td>
                        <td style={{ textAlign: 'center' }}>{s.element_count}</td>
                        <td style={{ textAlign: 'center' }}>{s.total_chars.toLocaleString()}</td>
                        <td style={{ textAlign: 'center' }}>{s.avg_element_length}</td>
                        <td style={{ textAlign: 'center' }}>{s.max_element_length.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
