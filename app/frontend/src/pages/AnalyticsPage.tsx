import { useApi } from '../hooks/useApi';

interface Overview {
  total_documents: number;
  total_doc_ids: number;
  total_elements: number;
  unique_element_types: number;
}

interface ElementDist {
  distribution: { element_type: string; count: number }[];
}

interface DocComparison {
  documents: { file_name: string; elements: Record<string, number> }[];
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

const SHORT_FILE_NAMES: Record<string, string> = {
  'nda_agreement.pdf': 'NDA',
  'software_license.pdf': 'Software License',
  'employment_agreement.pdf': 'Employment',
  'commercial_lease.pdf': 'Commercial Lease',
  'merger_agreement.pdf': 'Merger',
};

export default function AnalyticsPage() {
  const overview = useApi<Overview>('/api/analytics/overview');
  const dist = useApi<ElementDist>('/api/analytics/element-distribution');
  const comparison = useApi<DocComparison>('/api/analytics/document-comparison');
  const contentStats = useApi<ContentStats>('/api/analytics/content-stats');

  const isLoading = overview.loading || dist.loading || comparison.loading || contentStats.loading;

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner" />
        Loading analytics...
      </div>
    );
  }

  const maxDist = dist.data ? Math.max(...dist.data.distribution.map((d) => d.count)) : 1;
  const maxChars = contentStats.data
    ? Math.max(...contentStats.data.stats.map((s) => s.total_chars))
    : 1;

  return (
    <div>
      <div className="page-header">
        <h2>Analytics Dashboard</h2>
        <p>Document processing statistics and comparisons</p>
      </div>

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
                {dist.data.distribution.map((d, i) => (
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
                ))}
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
                {contentStats.data.stats.map((s, i) => (
                  <div key={s.file_name} className="bar-row">
                    <div className="bar-label">
                      {SHORT_FILE_NAMES[s.file_name] || s.file_name}
                    </div>
                    <div className="bar-wrapper">
                      <div
                        className={`bar-fill ${BAR_COLORS[i % BAR_COLORS.length]}`}
                        style={{ width: `${(s.total_chars / maxChars) * 100}%` }}
                      >
                        {s.total_chars.toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Document comparison table */}
      {comparison.data && (
        <div className="card" style={{ marginTop: 20 }}>
          <div className="card-header">
            <h3>Document Element Comparison</h3>
          </div>
          <div className="card-body" style={{ padding: 0, overflowX: 'auto' }}>
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th style={{ textAlign: 'center' }}>Titles</th>
                  <th style={{ textAlign: 'center' }}>Section Headers</th>
                  <th style={{ textAlign: 'center' }}>Text Blocks</th>
                  <th style={{ textAlign: 'center' }}>Page Headers</th>
                  <th style={{ textAlign: 'center' }}>Total</th>
                </tr>
              </thead>
              <tbody>
                {comparison.data.documents.map((doc) => {
                  const total = Object.values(doc.elements).reduce((a, b) => a + b, 0);
                  return (
                    <tr key={doc.file_name}>
                      <td style={{ fontWeight: 600 }}>
                        {SHORT_FILE_NAMES[doc.file_name] || doc.file_name}
                      </td>
                      <td style={{ textAlign: 'center' }}>{doc.elements.title || 0}</td>
                      <td style={{ textAlign: 'center' }}>{doc.elements.section_header || 0}</td>
                      <td style={{ textAlign: 'center' }}>{doc.elements.text || 0}</td>
                      <td style={{ textAlign: 'center' }}>{doc.elements.page_header || 0}</td>
                      <td style={{ textAlign: 'center', fontWeight: 700 }}>{total}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Avg element length stats */}
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
                    <td style={{ fontWeight: 600 }}>
                      {SHORT_FILE_NAMES[s.file_name] || s.file_name}
                    </td>
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
    </div>
  );
}
