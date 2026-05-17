import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Radar, Doughnut, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, ArcElement, PointElement, LineElement, Filler, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import {
  Search, BarChart3, AlertTriangle, ChevronRight,
  Cpu, FileText, LineChart as LineChartIcon, ShieldCheck, Clock, TrendingUp, Target, Gauge
} from 'lucide-react';

ChartJS.register(RadialLinearScale, ArcElement, PointElement, LineElement, Filler, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const POPULAR_STOCKS = [
  { symbol: 'RELIANCE.NS',  name: 'Reliance Industries',       market: '🇮🇳 NSE' },
  { symbol: 'TCS.NS',       name: 'Tata Consultancy Services',  market: '🇮🇳 NSE' },
  { symbol: 'INFY.NS',      name: 'Infosys',                   market: '🇮🇳 NSE' },
  { symbol: 'HDFCBANK.NS',  name: 'HDFC Bank',                 market: '🇮🇳 NSE' },
  { symbol: 'ICICIBANK.NS', name: 'ICICI Bank',                market: '🇮🇳 NSE' },
  { symbol: 'HINDUNILVR.NS',name: 'Hindustan Unilever',        market: '🇮🇳 NSE' },
  { symbol: 'ITC.NS',       name: 'ITC Limited',               market: '🇮🇳 NSE' },
  { symbol: 'SBIN.NS',      name: 'State Bank of India',       market: '🇮🇳 NSE' },
  { symbol: 'AAPL',         name: 'Apple Inc.',                market: '🇺🇸 NASDAQ' },
  { symbol: 'MSFT',         name: 'Microsoft',                 market: '🇺🇸 NASDAQ' },
  { symbol: 'GOOGL',        name: 'Alphabet (Google)',         market: '🇺🇸 NASDAQ' },
  { symbol: 'NVDA',         name: 'NVIDIA',                    market: '🇺🇸 NASDAQ' },
  { symbol: 'TSLA',         name: 'Tesla',                     market: '🇺🇸 NASDAQ' },
  { symbol: 'V',            name: 'Visa Inc.',                 market: '🇺🇸 NYSE' },
];

const STEPS = [
  { label: 'Data Retrieval',      icon: Search,    desc: 'Scraping real-time news & market feeds' },
  { label: 'Quantitative Analysis', icon: LineChart, desc: 'Computing valuations & PE ratios' },
  { label: 'Qualitative Review', icon: FileText,  desc: 'Analyzing earnings & transcripts' },
  { label: 'AI Synthesis',       icon: Cpu,       desc: 'Generating investment thesis' },
];

const RATING_COLORS = { BUY: '#22d47e', HOLD: '#f5a623', SELL: '#f05a5a' };
const RISK_COLORS = { Low: '#22d47e', Medium: '#f5a623', High: '#f05a5a' };

function ScoreRadarChart({ scores }) {
  if (!scores) return null;
  const labels = Object.keys(scores).map(k => k.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()));
  const values = Object.values(scores);
  return (
    <div style={{ maxWidth: 300, margin: '0 auto' }}>
      <Radar data={{
        labels,
        datasets: [{ label: 'Score', data: values, backgroundColor: 'rgba(0,200,150,0.15)', borderColor: '#00c896', borderWidth: 2, pointBackgroundColor: '#00c896', pointRadius: 4 }]
      }} options={{ scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20, color: '#8aa094', backdropColor: 'transparent' }, grid: { color: 'rgba(255,255,255,0.06)' }, pointLabels: { color: '#e8f0eb', font: { size: 11 } } } }, plugins: { legend: { display: false } }, maintainAspectRatio: true }} />
    </div>
  );
}

function MetricsBarChart({ metrics }) {
  if (!metrics) return null;
  const display = {
    'P/E': metrics.pe_ratio, 'P/S': metrics.ps_ratio, 'P/B': metrics.pb_ratio,
    'ROE%': metrics.roe, 'Gross%': metrics.gross_margin, 'Net%': metrics.net_margin
  };
  const labels = Object.keys(display);
  const values = Object.values(display).map(v => v || 0);
  return (
    <Bar data={{
      labels,
      datasets: [{ label: 'Value', data: values, backgroundColor: ['#4b9aff','#9f82f0','#00c896','#22d47e','#e8a93a','#f05a5a'], borderRadius: 6, borderSkipped: false }]
    }} options={{ plugins: { legend: { display: false } }, scales: { y: { ticks: { color: '#8aa094' }, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { ticks: { color: '#e8f0eb' }, grid: { display: false } } }, maintainAspectRatio: true }} />
  );
}

function RatingBadge({ recommendation, confidence }) {
  const color = RATING_COLORS[recommendation?.toUpperCase()] || '#f5a623';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1.25rem', background: `${color}12`, border: `1px solid ${color}30`, borderRadius: 'var(--r-xl)' }}>
      <div style={{ width: 56, height: 56, borderRadius: '50%', background: `${color}20`, border: `3px solid ${color}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.1rem', fontWeight: 800, color }}>
        {recommendation?.toUpperCase()?.charAt(0) || '?'}
      </div>
      <div>
        <div style={{ fontSize: '1.3rem', fontWeight: 800, color, letterSpacing: '-0.02em' }}>{recommendation?.toUpperCase() || 'N/A'}</div>
        {confidence && <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Confidence: {confidence}%</div>}
      </div>
    </div>
  );
}

function ChartDashboard({ chartData }) {
  if (!chartData) return null;
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
      {/* Rating Card */}
      <div style={{ background: 'var(--ink-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <Target size={16} color="var(--emerald)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>Recommendation</span>
        </div>
        <RatingBadge recommendation={chartData.recommendation} confidence={chartData.confidence} />
        {chartData.currentPrice && chartData.targetPrice && (
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem', padding: '0.75rem', background: 'var(--ink-2)', borderRadius: 'var(--r-md)', fontSize: '0.85rem' }}>
            <div><span style={{ color: 'var(--text-muted)' }}>Current:</span> <strong style={{ color: 'var(--text-primary)' }}>${chartData.currentPrice}</strong></div>
            <div><span style={{ color: 'var(--text-muted)' }}>Target:</span> <strong style={{ color: 'var(--emerald)' }}>${chartData.targetPrice}</strong></div>
            <div style={{ color: chartData.targetPrice > chartData.currentPrice ? 'var(--bull)' : 'var(--bear)', fontWeight: 700 }}>
              {((chartData.targetPrice - chartData.currentPrice) / chartData.currentPrice * 100).toFixed(1)}%
            </div>
          </div>
        )}
      </div>
      {/* Radar Chart */}
      {chartData.scores && (
        <div style={{ background: 'var(--ink-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <Gauge size={16} color="var(--violet)" />
            <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>Analysis Scores</span>
          </div>
          <ScoreRadarChart scores={chartData.scores} />
        </div>
      )}
      {/* Metrics Bar Chart */}
      {chartData.metrics && (
        <div style={{ background: 'var(--ink-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <BarChart3 size={16} color="var(--blue-400)" />
            <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>Key Metrics</span>
          </div>
          <MetricsBarChart metrics={chartData.metrics} />
        </div>
      )}
    </div>
  );
}




function parseSections(text) {
  if (!text || text.length < 200) return null;
  const lines = text.split('\n');
  const sections = [];
  let current = { title: 'Executive Summary', content: [] };
  for (const line of lines) {
    const h1 = line.match(/^#\s+(.+)/);
    const h2 = line.match(/^##\s+(.+)/);
    if (h1 || h2) {
      if (current.content.length > 0 || current.title !== 'Executive Summary')
        sections.push({ ...current, content: current.content.join('\n') });
      current = { title: (h1 || h2)[1].trim(), content: [] };
    } else {
      current.content.push(line);
    }
  }
  if (current.content.length > 0) sections.push({ ...current, content: current.content.join('\n') });
  return sections.length > 1 ? sections : null;
}

export default function StockAnalyzer() {
  const [ticker, setTicker] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [activeStep, setActiveStep] = useState(0);
  const dropdownRef = useRef(null);
  const timerRef = useRef(null);
  const stepRef = useRef(null);

  useEffect(() => {
    function onClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setShowDropdown(false);
    }
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  useEffect(() => {
    if (loading) {
      setElapsed(0); setActiveStep(0);
      timerRef.current = setInterval(() => setElapsed(p => p + 1), 1000);
      stepRef.current = setInterval(() => setActiveStep(p => p < 3 ? p + 1 : p), 25000);
    } else {
      clearInterval(timerRef.current);
      clearInterval(stepRef.current);
    }
    return () => { clearInterval(timerRef.current); clearInterval(stepRef.current); };
  }, [loading]);

  const filtered = POPULAR_STOCKS.filter(s =>
    s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectStock = (s) => {
    setTicker(s.symbol);
    setSearchQuery(`${s.name} (${s.symbol})`);
    setShowDropdown(false);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!ticker) return;
    setLoading(true); setError(null); setResult(null);
    
    try {
      const res = await fetch('http://localhost:8000/api/portfolio/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: ticker }),
      });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Analysis failed.'); }
      setResult(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fmtTime = (s) => { const m = Math.floor(s / 60); return m > 0 ? `${m}m ${s % 60}s` : `${s}s`; };
  const sections = result?.analysis ? parseSections(result.analysis) : null;

  return (
    <div className="container page-wrapper">

      {/* Header */}
      <div className="animate-fade-1" style={{ marginBottom: '2.5rem' }}>
        <div style={{ marginBottom: '0.75rem' }}>
          <span className="badge badge-violet" style={{ fontSize: '0.7rem', letterSpacing: '0.05em' }}>
            <Cpu size={10} /> Multi-Agent AI Research
          </span>
        </div>
        <h1 className="page-title">Stock Intelligence</h1>
        <p className="page-subtitle">
          AI-powered stock analysis giving you quick, simple, and accurate insights on fundamentals and market sentiment.
        </p>
      </div>

      {/* Search panel */}
      <div className="animate-fade-2" style={{
        background: 'var(--ink-1)',
        border: '1px solid var(--border-1)',
        borderRadius: 'var(--r-xl)',
        padding: '1.5rem',
        marginBottom: '1.5rem',
      }}>
        <form onSubmit={handleAnalyze} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <div ref={dropdownRef} style={{ flex: 1, position: 'relative', zIndex: 100 }}>
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{
                position: 'absolute', left: '12px', top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)', pointerEvents: 'none',
              }} />
              <input
                type="text"
                value={searchQuery}
                onChange={e => {
                  setSearchQuery(e.target.value);
                  setShowDropdown(true);
                  const v = e.target.value.trim().toUpperCase();
                  if (v && !v.includes('(')) setTicker(v);
                }}
                onFocus={() => setShowDropdown(true)}
                placeholder="Search ticker (e.g. TSLA, INFY.NS)..."
                className="input-control"
                style={{ paddingLeft: '38px', height: '46px', fontSize: '0.9rem' }}
                disabled={loading}
              />
            </div>

            {showDropdown && (
              <div style={{
                position: 'absolute', top: 'calc(100% + 6px)', left: 0, right: 0,
                maxHeight: '280px', overflowY: 'auto',
                background: 'var(--ink-0)', backdropFilter: 'blur(16px)',
                border: '1px solid var(--border-2)',
                borderRadius: 'var(--r-lg)', zIndex: 50,
                boxShadow: 'var(--shadow-lg)',
              }}>
                {filtered.length > 0 ? filtered.map(s => (
                  <div
                    key={s.symbol} onClick={() => selectStock(s)}
                    style={{
                      padding: '0.825rem 1.1rem', cursor: 'pointer',
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      borderBottom: '1px solid var(--border-1)', transition: 'background 0.15s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--ink-2)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  >
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.9rem', fontFamily: 'var(--font-mono)' }}>{s.symbol}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>{s.name}</div>
                    </div>
                    <span className="badge badge-outline" style={{ fontSize: '0.7rem', padding: '0.15rem 0.5rem' }}>{s.market}</span>
                  </div>
                )) : (
                  <div style={{ padding: '1.25rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    No match — press <kbd style={{ background: 'var(--ink-3)', padding: '0.1rem 0.4rem', borderRadius: '4px', fontSize: '0.8rem', fontFamily: 'var(--font-mono)' }}>Enter</kbd> to analyze custom ticker
                  </div>
                )}
              </div>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !ticker}
            style={{ height: '46px', padding: '0 1.75rem', borderRadius: 'var(--r-lg)', fontSize: '0.9rem', whiteSpace: 'nowrap' }}
          >
            {loading
              ? <><span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Analyzing…</>
              : <><BarChart3 size={15} /> Run Analysis</>
            }
          </button>
        </form>
      </div>

      {/* Progress */}
      {loading && (
        <div className="animate-fade-3" style={{
          background: 'var(--ink-1)',
          border: '1px solid var(--border-1)',
          borderRadius: 'var(--r-xl)',
          padding: '1.5rem',
          marginBottom: '1.5rem',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--amber-400)', display: 'inline-block', boxShadow: '0 0 6px var(--amber-400)' }} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0 }}>
                AI Agents Analyzing <span style={{ color: 'var(--blue-400)', fontFamily: 'var(--font-mono)' }}>{ticker}</span>
              </h3>
            </div>
            <span className="badge badge-amber" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
              <Clock size={11} /> {fmtTime(elapsed)}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {STEPS.map((step, i) => {
              const Icon = step.icon;
              const isActive = i === activeStep;
              const isDone = i < activeStep;
              return (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: '0.875rem',
                  padding: '0.875rem 1rem', borderRadius: 'var(--r-lg)',
                  background: isActive ? 'var(--ink-2)' : 'transparent',
                  border: `1px solid ${isActive ? 'var(--border-blue)' : 'var(--border-1)'}`,
                  opacity: isDone || isActive ? 1 : 0.45,
                  transition: 'all 0.3s',
                }}>
                  <div style={{
                    width: 34, height: 34, borderRadius: 'var(--r-sm)', flexShrink: 0,
                    background: isDone ? 'var(--green-glow-soft)' : isActive ? 'var(--blue-glow-soft)' : 'var(--ink-2)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: isDone ? 'var(--green-400)' : isActive ? 'var(--blue-400)' : 'var(--text-muted)',
                  }}>
                    {isDone ? <ShieldCheck size={16} /> : <Icon size={16} strokeWidth={1.75} />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: '0.875rem', fontWeight: 600,
                      color: isDone ? 'var(--green-400)' : isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                    }}>{step.label}</div>
                    <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>{step.desc}</div>
                  </div>
                  {isActive && <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2, color: 'var(--blue-400)' }} />}
                  {isDone && <ShieldCheck size={15} color="var(--green-400)" />}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          padding: '1rem 1.25rem', background: 'var(--red-glow-soft)',
          border: '1px solid rgba(239,68,68,0.2)', borderLeft: '3px solid var(--red-400)',
          borderRadius: 'var(--r-lg)', display: 'flex', gap: '0.75rem',
          alignItems: 'center', marginBottom: '1.5rem',
        }}>
          <AlertTriangle size={18} color="var(--red-400)" />
          <div>
            <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem' }}>Analysis Error</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{error}</div>
          </div>
        </div>
      )}

      {/* Result */}
      {result && !loading && (
        <div className="animate-fade-4">

          {/* Report header */}
          <div style={{
            background: 'var(--ink-1)', border: '1px solid var(--border-1)',
            borderRadius: 'var(--r-xl)', padding: '1.25rem 1.75rem',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{
                width: 44, height: 44, borderRadius: 'var(--r-md)',
                background: 'linear-gradient(135deg, var(--blue-600), var(--violet-500))',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 14px rgba(75,122,255,0.3)',
              }}>
                <TrendingUp size={22} color="#fff" strokeWidth={2} />
              </div>
              <div>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0 }}>AI Investment Report</h2>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>
                  Ticker: <span style={{ color: 'var(--blue-400)', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{result.company}</span>
                </div>
              </div>
            </div>
            <div className="badge badge-outline" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
              <Clock size={11} /> {new Date(result.timestamp).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}
            </div>
          </div>

          {/* Chart Visualizations */}
          <ChartDashboard chartData={result.chart_data} />

          {/* Sections */}
          {sections ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
              {sections.map((sec, i) => (
                <div key={i} style={{
                  background: 'var(--ink-1)', border: '1px solid var(--border-1)',
                  borderRadius: 'var(--r-xl)', padding: '2rem',
                  animation: `fadeUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.07}s both`,
                  position: 'relative', overflow: 'hidden',
                }}>
                  <div style={{
                    position: 'absolute', top: 0, left: 0, right: 0, height: '1px',
                    background: `linear-gradient(90deg, transparent, var(--blue-500)40, transparent)`,
                  }} />
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-1)' }}>
                    <div style={{ width: 24, height: 24, borderRadius: '6px', background: 'var(--blue-glow-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--blue-400)', flexShrink: 0 }}>
                      <ChevronRight size={14} />
                    </div>
                    <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, letterSpacing: '-0.02em' }}>{sec.title}</h3>
                  </div>
                  <div className="report-md">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{sec.content}</ReactMarkdown>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ background: 'var(--ink-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', padding: '2rem' }}>
              <div className="report-md"><ReactMarkdown remarkPlugins={[remarkGfm]}>{result.analysis}</ReactMarkdown></div>
            </div>
          )}
        </div>
      )}

      <style>{`
        .report-md { line-height: 1.8; color: var(--text-secondary); font-size: 0.9rem; }
        .report-md h1, .report-md h2 { font-size: 1.1rem; color: var(--text-primary); margin: 1.75rem 0 0.75rem; font-weight: 700; letter-spacing: -0.02em; }
        .report-md h1:first-child, .report-md h2:first-child { margin-top: 0; }
        .report-md h3 { font-size: 0.975rem; color: var(--text-primary); margin: 1.25rem 0 0.5rem; font-weight: 600; }
        .report-md p { margin-bottom: 1rem; }
        .report-md strong { color: var(--emerald); font-weight: 600; }
        .report-md ul, .report-md ol { padding-left: 1.25rem; margin-bottom: 1rem; }
        .report-md li { margin-bottom: 0.4rem; }
        .report-md li::marker { color: var(--emerald); }

        /* Table wrapper for horizontal scroll on small screens */
        .report-md table {
          width: 100%;
          border-collapse: separate;
          border-spacing: 0;
          margin: 1.25rem 0;
          font-size: 0.865rem;
          border-radius: var(--r-lg);
          overflow: hidden;
          border: 1px solid var(--border-2);
          box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .report-md th {
          background: linear-gradient(135deg, rgba(0,200,150,0.1), rgba(0,200,150,0.05));
          color: var(--emerald);
          font-weight: 700;
          text-align: left;
          padding: 0.85rem 1.1rem;
          border-bottom: 2px solid var(--border-2);
          font-size: 0.78rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          white-space: nowrap;
        }
        .report-md td {
          padding: 0.75rem 1.1rem;
          border-bottom: 1px solid var(--border-1);
          font-family: var(--font-mono);
          font-size: 0.85rem;
          color: var(--text-primary);
          transition: background 0.15s;
        }
        .report-md tr:nth-child(even) td { background: var(--ink-2); }
        .report-md tr:nth-child(odd) td { background: transparent; }
        .report-md tr:last-child td { border-bottom: none; }
        .report-md tr:hover td { background: var(--ink-3); }

        .report-md blockquote { border-left: 3px solid var(--violet-400); padding: 0.875rem 1.25rem; margin: 1.25rem 0; background: var(--violet-glow-soft); border-radius: 0 var(--r-md) var(--r-md) 0; font-style: italic; color: var(--text-secondary); }
        .report-md code { background: var(--ink-3); padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.85em; color: var(--amber-400); font-family: var(--font-mono); }
        .report-md pre { background: var(--ink-0); padding: 1.25rem; border-radius: var(--r-lg); overflow-x: auto; margin: 1.25rem 0; border: 1px solid var(--border-1); }
        .report-md pre code { background: none; padding: 0; color: var(--text-secondary); font-size: 0.875rem; }
        .report-md hr { border: none; border-top: 1px solid var(--border-1); margin: 2rem 0; }
      `}</style>
    </div>
  );
}
