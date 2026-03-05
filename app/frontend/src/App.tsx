import { useState } from 'react';
import {
  FileText,
  Search,
  Upload,
  BarChart3,
  Scale,
  Sparkles,
  Home,
  MessageCircleQuestion,
  Gavel,
  Receipt,
  Landmark,
} from 'lucide-react';
import OverviewPage from './pages/OverviewPage';
import DocumentBrowser from './pages/DocumentBrowser';
import DocumentViewer from './pages/DocumentViewer';
import SearchPage from './pages/SearchPage';
import UploadPage from './pages/UploadPage';
import AnalyticsPage from './pages/AnalyticsPage';
import KeyInsightsPage from './pages/KeyInsightsPage';
import AskPage from './pages/AskPage';
import SubpoenasPage from './pages/SubpoenasPage';
import InvoicesPage from './pages/InvoicesPage';
import RegulatoryPage from './pages/RegulatoryPage';

type Page = 'overview' | 'browser' | 'viewer' | 'search' | 'upload' | 'analytics' | 'insights' | 'ask' | 'subpoenas' | 'invoices' | 'regulatory';

function App() {
  const [page, setPage] = useState<Page>('overview');
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  const openDocument = (docId: string) => {
    setSelectedDocId(docId);
    setPage('viewer');
  };

  const goBack = () => {
    setPage('browser');
    setSelectedDocId(null);
  };

  const navigate = (target: string) => {
    if (target === 'browser') goBack();
    else setPage(target as Page);
  };

  const navItems: { id: Page; label: string; icon: React.ReactNode; section?: string }[] = [
    { id: 'overview', label: 'Overview', icon: <Home /> },
    { id: 'browser', label: 'Documents', icon: <FileText /> },
    { id: 'insights', label: 'Key Insights', icon: <Sparkles /> },
    { id: 'ask', label: 'Ask', icon: <MessageCircleQuestion /> },
    { id: 'search', label: 'Search', icon: <Search /> },
    { id: 'upload', label: 'Upload', icon: <Upload /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3 /> },
    { id: 'subpoenas', label: 'Subpoenas', icon: <Gavel />, section: 'Specialized' },
    { id: 'invoices', label: 'Invoices', icon: <Receipt /> },
    { id: 'regulatory', label: 'Regulatory', icon: <Landmark /> },
  ];

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header" style={{ cursor: 'pointer' }} onClick={() => setPage('overview')}>
          <h1>
            <Scale size={16} style={{ marginRight: 8, verticalAlign: 'middle' }} />
            Legal Doc Processor
          </h1>
          <p>Document Intelligence</p>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <div key={item.id}>
              {item.section && (
                <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.2, color: 'rgba(255,255,255,0.4)', padding: '16px 16px 6px', marginTop: 4 }}>
                  {item.section}
                </div>
              )}
              <button
                className={`nav-item ${page === item.id || (item.id === 'browser' && page === 'viewer') ? 'active' : ''}`}
                onClick={() => navigate(item.id)}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            </div>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        {page === 'overview' && <OverviewPage onNavigate={navigate} />}
        {page === 'browser' && <DocumentBrowser onOpenDocument={openDocument} />}
        {page === 'viewer' && selectedDocId && (
          <DocumentViewer docId={selectedDocId} onBack={goBack} />
        )}
        {page === 'search' && <SearchPage onOpenDocument={openDocument} />}
        {page === 'upload' && <UploadPage />}
        {page === 'insights' && <KeyInsightsPage />}
        {page === 'ask' && <AskPage />}
        {page === 'analytics' && <AnalyticsPage />}
        {page === 'subpoenas' && <SubpoenasPage />}
        {page === 'invoices' && <InvoicesPage />}
        {page === 'regulatory' && <RegulatoryPage />}
      </main>
    </div>
  );
}

export default App;
