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
} from 'lucide-react';
import OverviewPage from './pages/OverviewPage';
import DocumentBrowser from './pages/DocumentBrowser';
import DocumentViewer from './pages/DocumentViewer';
import SearchPage from './pages/SearchPage';
import UploadPage from './pages/UploadPage';
import AnalyticsPage from './pages/AnalyticsPage';
import KeyInsightsPage from './pages/KeyInsightsPage';
import AskPage from './pages/AskPage';

type Page = 'overview' | 'browser' | 'viewer' | 'search' | 'upload' | 'analytics' | 'insights' | 'ask';

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

  const navItems: { id: Page; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <Home /> },
    { id: 'browser', label: 'Documents', icon: <FileText /> },
    { id: 'insights', label: 'Key Insights', icon: <Sparkles /> },
    { id: 'ask', label: 'Ask', icon: <MessageCircleQuestion /> },
    { id: 'search', label: 'Search', icon: <Search /> },
    { id: 'upload', label: 'Upload', icon: <Upload /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3 /> },
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
            <button
              key={item.id}
              className={`nav-item ${page === item.id || (item.id === 'browser' && page === 'viewer') ? 'active' : ''}`}
              onClick={() => navigate(item.id)}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
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
      </main>
    </div>
  );
}

export default App;
