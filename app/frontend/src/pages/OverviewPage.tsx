import {
  FileText,
  Search,
  Upload,
  BarChart3,
  Sparkles,
  Database,
  Cpu,
  ArrowRight,
  Layers,
  ScanText,
  BrainCircuit,
} from 'lucide-react';

interface OverviewPageProps {
  onNavigate: (page: string) => void;
}

function OverviewPage({ onNavigate }: OverviewPageProps) {
  return (
    <div className="page-content">
      {/* Hero */}
      <div
        style={{
          background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%)',
          borderRadius: 'var(--radius-lg)',
          padding: '48px 40px',
          color: 'white',
          marginBottom: 32,
        }}
      >
        <div style={{ maxWidth: 720 }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '4px 12px',
              background: 'rgba(200, 160, 74, 0.2)',
              borderRadius: 100,
              fontSize: 12,
              fontWeight: 600,
              color: 'var(--gold-light)',
              marginBottom: 16,
              letterSpacing: 0.5,
            }}
          >
            <Cpu size={14} /> Powered by Databricks AI Functions
          </div>
          <h1 style={{ fontSize: 32, fontWeight: 700, marginBottom: 12, lineHeight: 1.3 }}>
            Legal Document Intelligence
          </h1>
          <p style={{ fontSize: 16, lineHeight: 1.7, color: 'var(--slate-light)', marginBottom: 24 }}>
            Upload, parse, and extract structured insights from legal documents using
            Databricks <code style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: 4, fontSize: 14 }}>ai_document_parse</code> and{' '}
            <code style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: 4, fontSize: 14 }}>ai_query</code>.
            Transform unstructured PDFs into queryable, structured data — parties, dates,
            financial terms, obligations, and risk flags — all within Unity Catalog.
          </p>
          <button
            onClick={() => onNavigate('browser')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 20px',
              background: 'var(--gold)',
              color: 'var(--navy-dark)',
              border: 'none',
              borderRadius: 'var(--radius)',
              fontSize: 14,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Explore Documents <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* Pipeline diagram */}
      <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--navy)', marginBottom: 16 }}>
        How It Works
      </h3>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 0,
          marginBottom: 32,
          position: 'relative',
        }}
      >
        {[
          {
            icon: <ScanText size={24} />,
            step: '1',
            title: 'Document Parsing',
            fn: 'ai_document_parse()',
            desc: 'PDFs are ingested from Unity Catalog Volumes and parsed into structured elements — titles, section headers, text blocks, tables, and figures — with bounding box coordinates and page metadata.',
            color: 'var(--blue)',
            bg: 'var(--blue-light)',
          },
          {
            icon: <BrainCircuit size={24} />,
            step: '2',
            title: 'Key Info Extraction',
            fn: 'ai_query()',
            desc: 'Parsed text is sent through a Foundation Model to extract structured fields: parties, effective dates, dollar amounts, governing law, obligations, and risk flags — returned as typed JSON.',
            color: 'var(--gold-dark)',
            bg: 'rgba(200, 160, 74, 0.1)',
          },
          {
            icon: <Database size={24} />,
            step: '3',
            title: 'Structured Storage',
            fn: 'Delta Tables',
            desc: 'All parsed elements and extracted fields are stored as Delta tables in Unity Catalog — fully governed, versioned, and queryable via SQL, Python, or this application.',
            color: 'var(--green)',
            bg: 'var(--green-light)',
          },
        ].map((item, i) => (
          <div key={i} style={{ position: 'relative' }}>
            <div
              className="card"
              style={{
                margin: '0 8px',
                padding: 24,
                borderTop: `3px solid ${item.color}`,
                height: '100%',
              }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 'var(--radius)',
                  background: item.bg,
                  color: item.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: 14,
                }}
              >
                {item.icon}
              </div>
              <div
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  color: item.color,
                  textTransform: 'uppercase',
                  letterSpacing: 1,
                  marginBottom: 4,
                }}
              >
                Step {item.step}
              </div>
              <h4 style={{ fontSize: 16, fontWeight: 700, color: 'var(--navy)', marginBottom: 4 }}>
                {item.title}
              </h4>
              <code
                style={{
                  fontSize: 12,
                  color: 'var(--slate)',
                  background: 'var(--gray-100)',
                  padding: '2px 6px',
                  borderRadius: 4,
                  display: 'inline-block',
                  marginBottom: 10,
                }}
              >
                {item.fn}
              </code>
              <p style={{ fontSize: 13, color: 'var(--gray-700)', lineHeight: 1.6 }}>{item.desc}</p>
            </div>
            {i < 2 && (
              <div
                style={{
                  position: 'absolute',
                  right: -4,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--gray-300)',
                  zIndex: 1,
                }}
              >
                <ArrowRight size={20} />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Feature cards */}
      <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--navy)', marginBottom: 16 }}>
        App Features
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, marginBottom: 32 }}>
        {[
          {
            icon: <FileText size={20} />,
            title: 'Document Browser',
            desc: 'Browse all processed documents with element breakdowns. View parsed content organized sequentially or grouped by element type (titles, headers, text blocks).',
            page: 'browser',
            color: 'var(--navy)',
          },
          {
            icon: <Sparkles size={20} />,
            title: 'Key Insights',
            desc: 'AI-extracted structured data from each document: parties, dates, financial terms, governing law, key obligations, and flagged risks — all in one view.',
            page: 'insights',
            color: 'var(--gold-dark)',
          },
          {
            icon: <Search size={20} />,
            title: 'Full-Text Search',
            desc: 'Search across all document content with highlighted matches. Find specific clauses, terms, or parties across your entire document corpus instantly.',
            page: 'search',
            color: 'var(--blue)',
          },
          {
            icon: <Upload size={20} />,
            title: 'Document Upload',
            desc: 'Drag-and-drop new PDF documents. The pipeline automatically parses them with ai_document_parse, extracts elements, and makes them searchable.',
            page: 'upload',
            color: 'var(--green)',
          },
          {
            icon: <BarChart3 size={20} />,
            title: 'Analytics Dashboard',
            desc: 'Visualize document statistics — element type distribution, document size comparisons, and content length analysis across your collection.',
            page: 'analytics',
            color: 'var(--slate)',
          },
          {
            icon: <Layers size={20} />,
            title: 'Unity Catalog Governed',
            desc: 'All data stored in Delta tables within Unity Catalog. Fine-grained access control, lineage tracking, and full audit trail for compliance.',
            page: '',
            color: 'var(--navy-light)',
          },
        ].map((item) => (
          <div
            key={item.title}
            className="card"
            style={{
              padding: 20,
              cursor: item.page ? 'pointer' : 'default',
              transition: 'all 0.15s',
            }}
            onClick={() => item.page && onNavigate(item.page)}
            onMouseEnter={(e) => {
              if (item.page) (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--gold)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLDivElement).style.borderColor = '';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 'var(--radius)',
                  background: 'var(--gray-100)',
                  color: item.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                {item.icon}
              </div>
              <div>
                <h4 style={{ fontSize: 15, fontWeight: 600, color: 'var(--navy)', marginBottom: 4 }}>
                  {item.title}
                  {item.page && (
                    <ArrowRight
                      size={14}
                      style={{ marginLeft: 6, color: 'var(--slate-light)', verticalAlign: 'middle' }}
                    />
                  )}
                </h4>
                <p style={{ fontSize: 13, color: 'var(--gray-700)', lineHeight: 1.6 }}>{item.desc}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Tech stack */}
      <div className="card" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--navy)', marginBottom: 16, textTransform: 'uppercase', letterSpacing: 0.5 }}>
          Databricks Components Used
        </h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
          {[
            'ai_document_parse()',
            'ai_query()',
            'Foundation Model APIs',
            'Unity Catalog',
            'UC Volumes',
            'Delta Tables',
            'SQL Warehouse (Serverless)',
            'Databricks Apps',
            'SQL Statements API',
          ].map((tech) => (
            <span
              key={tech}
              style={{
                padding: '6px 14px',
                borderRadius: 100,
                fontSize: 13,
                fontWeight: 500,
                background: 'var(--gray-100)',
                color: 'var(--gray-700)',
                border: '1px solid var(--gray-200)',
              }}
            >
              {tech}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default OverviewPage;
