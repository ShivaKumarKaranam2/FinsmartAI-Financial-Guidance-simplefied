import { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { TrendingUp, Activity, MessageSquare, Calculator, BarChart3, Sun, Moon } from 'lucide-react';

import LandingPage      from './pages/LandingPage';
import MarketSentiment  from './pages/MarketSentiment';
import ChatBot          from './pages/ChatBot';
import BudgetPlanner    from './pages/BudgetPlanner';
import StockAnalyzer    from './pages/StockAnalyzer';

const navItems = [
  { path: '/sentiment', label: 'Sentiment', icon: Activity },
  { path: '/chat',      label: 'AI Chat',   icon: MessageSquare },
  { path: '/budget',    label: 'Budget',    icon: Calculator },
  { path: '/stock',     label: 'Stock AI',  icon: BarChart3 },
];

function Navbar({ theme, onToggle }) {
  const { pathname } = useLocation();
  const isDark = theme === 'dark';

  return (
    <nav className="navbar">
      <div className="nav-container">
        {/* Logo */}
        <Link to="/" className="nav-logo">
          <div className="nav-logo-icon">
            <TrendingUp size={16} color="#fff" strokeWidth={2.5} />
          </div>
          FinSmart
          <span style={{ color: 'var(--emerald)', fontWeight: 700 }}>AI</span>
        </Link>

        {/* Nav links */}
        <div className="nav-links">
          {navItems.map(({ path, label, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`nav-link ${pathname === path ? 'active' : ''}`}
            >
              <Icon size={14} strokeWidth={2} />
              {label}
            </Link>
          ))}
        </div>

        {/* Right side controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          {/* Live status */}
          <div className="nav-live">
            <span className="nav-live-dot" />
            Live
          </div>

          {/* Dark / Light toggle */}
          <button
            className="theme-toggle"
            onClick={onToggle}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle theme"
          >
            {isDark ? <Sun size={15} strokeWidth={2} /> : <Moon size={15} strokeWidth={2} />}
          </button>
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  // Read saved theme or default dark
  const [theme, setTheme] = useState(() => localStorage.getItem('fs-theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('fs-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');

  return (
    <>
      <Navbar theme={theme} onToggle={toggleTheme} />
      <main className="page-container">
        <Routes>
          <Route path="/"          element={<LandingPage />} />
          <Route path="/sentiment" element={<MarketSentiment />} />
          <Route path="/chat"      element={<ChatBot />} />
          <Route path="/budget"    element={<BudgetPlanner />} />
          <Route path="/stock"     element={<StockAnalyzer />} />
        </Routes>
      </main>
    </>
  );
}
