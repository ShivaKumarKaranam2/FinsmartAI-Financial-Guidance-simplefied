import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  BarElement, LineElement, PointElement, Filler,
  Title, Tooltip, Legend
} from 'chart.js';
import {
  Activity, Newspaper, TrendingUp, TrendingDown,
  Search, ExternalLink, BarChart3, Globe, AlertTriangle, RefreshCw
} from 'lucide-react';

ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  LineElement, PointElement, Filler,
  Title, Tooltip, Legend
);

export default function MarketSentiment() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [niftyData, setNiftyData] = useState(null);

  const fetchSentiment = async (search = '') => {
    setLoading(true);
    setError(null);
    try {
      const params = search ? { search } : {};
      const response = await axios.get('http://localhost:8000/api/sentiment/market', { params });
      setData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch market sentiment data.');
    } finally {
      setLoading(false);
    }
  };

  const fetchNifty50 = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/sentiment/nifty50');
      setNiftyData(res.data);
    } catch (err) {
      console.warn('Nifty 50 data unavailable:', err.message);
    }
  };

  useEffect(() => { fetchSentiment(); fetchNifty50(); }, []);

  const handleSearch = (e) => { e.preventDefault(); fetchSentiment(searchTerm); };

  // ── Gauge ──────────────────────────────────────────────────
  const renderGauge = () => {
    if (!data) return null;
    const score = data.average_sentiment_score;
    const level = data.fear_greed_index;
    let indexValue = Math.round((score + 1) * 50);
    indexValue = Math.max(0, Math.min(100, indexValue));
    const needleAngle = (indexValue / 100) * 180 - 90;

    let gaugeAccent = 'var(--green-400)';
    let gaugeGlow = 'var(--green-glow-soft)';
    if (level.includes('Fear')) {
      gaugeAccent = 'var(--red-400)';
      gaugeGlow = 'var(--red-glow-soft)';
    } else if (level === 'Neutral') {
      gaugeAccent = 'var(--amber-400)';
      gaugeGlow = 'var(--amber-glow)';
    }

    return (
      <div style={{
        background: 'var(--ink-1)',
        border: '1px solid var(--border-1)',
        borderRadius: 'var(--r-xl)',
        padding: '2rem 1.75rem',
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        position: 'relative', overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: '2px',
          background: `linear-gradient(90deg, transparent, ${gaugeAccent}, transparent)`,
        }} />

        <div style={{
          fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase',
          letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem'
        }}>
          <Activity size={11} /> Fear & Greed Index
        </div>

        <div style={{ position: 'relative', width: '240px', height: '130px' }}>
          <svg width="240" height="125" viewBox="0 0 240 125">
            <defs>
              <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="var(--red-400)" />
                <stop offset="45%" stopColor="var(--amber-400)" />
                <stop offset="100%" stopColor="var(--green-400)" />
              </linearGradient>
            </defs>
            <path d="M 20 110 A 100 100 0 0 1 220 110" fill="none" stroke="var(--ink-3)" strokeWidth="16" strokeLinecap="round" />
            <path d="M 20 110 A 100 100 0 0 1 220 110" fill="none" stroke="url(#gaugeGrad)" strokeWidth="16" strokeLinecap="round" opacity="0.9" />
          </svg>

          <div style={{
            position: 'absolute', width: '3px', height: '80px',
            background: 'var(--text-primary)',
            left: 'calc(50% - 1.5px)', bottom: '10px',
            transformOrigin: 'bottom center',
            transform: `rotate(${needleAngle}deg)`,
            transition: 'transform 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)',
            borderRadius: '3px', zIndex: 10,
            boxShadow: '0 0 8px rgba(0,0,0,0.6)',
          }} />
          <div style={{
            position: 'absolute', width: '14px', height: '14px',
            background: 'var(--text-primary)', borderRadius: '50%',
            bottom: '4px', left: 'calc(50% - 7px)', zIndex: 15,
            border: '2px solid var(--ink-0)',
          }} />
          <span style={{ position: 'absolute', left: 0, bottom: '0px', fontSize: '0.72rem', fontWeight: 700, color: 'var(--red-400)' }}>Fear</span>
          <span style={{ position: 'absolute', right: 0, bottom: '0px', fontSize: '0.72rem', fontWeight: 700, color: 'var(--green-400)' }}>Greed</span>
        </div>

        <div style={{ marginTop: '0.75rem', textAlign: 'center' }}>
          <div style={{
            fontSize: '3rem', fontWeight: 700, fontFamily: 'var(--font-mono)',
            color: gaugeAccent, lineHeight: 1, letterSpacing: '-0.04em',
          }}>{indexValue}</div>
          <div className="badge" style={{
            marginTop: '0.5rem',
            background: gaugeGlow, color: gaugeAccent,
            border: `1px solid ${gaugeAccent}30`,
            fontSize: '0.72rem', letterSpacing: '0.06em', textTransform: 'uppercase',
          }}>{level}</div>
        </div>

        <div style={{
          marginTop: '1.25rem', padding: '0.875rem 1rem',
          background: 'var(--ink-2)', border: '1px solid var(--border-1)',
          borderRadius: 'var(--r-lg)', fontSize: '0.82rem',
          color: 'var(--text-secondary)', lineHeight: 1.6,
          fontStyle: 'italic', width: '100%',
        }}>
          "{data.summary_note}"
        </div>
      </div>
    );
  };

  // ── Nifty 50 Chart ─────────────────────────────────────────
  const renderNiftyChart = () => {
    if (!niftyData) return null;
    const isPositive = niftyData.change >= 0;
    const lineColor = isPositive ? '#34d399' : '#f87171';
    const fillColor = isPositive
      ? 'rgba(52, 211, 153, 0.08)'
      : 'rgba(248, 113, 113, 0.08)';

    const chartData = {
      labels: niftyData.dates,
      datasets: [{
        label: 'Nifty 50',
        data: niftyData.closes,
        borderColor: lineColor,
        backgroundColor: fillColor,
        fill: true,
        tension: 0.35,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: lineColor,
        borderWidth: 2,
      }],
    };

    const chartOpts = {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(12,14,20,0.95)',
          titleFont: { size: 11, family: 'DM Sans' },
          bodyFont: { size: 13, family: 'DM Mono', weight: 'bold' },
          padding: 10, cornerRadius: 6,
          callbacks: {
            label: (ctx) => `₹${ctx.parsed.y.toLocaleString()}`,
          },
        },
      },
      scales: {
        x: {
          ticks: { color: '#7a9988', font: { size: 10 }, maxTicksLimit: 8 },
          grid: { display: false }, border: { display: false },
        },
        y: {
          ticks: {
            color: '#7a9988', font: { size: 10 },
            callback: (v) => (v / 1000).toFixed(1) + 'K',
          },
          grid: { color: 'rgba(255,255,255,0.055)' }, border: { display: false },
        },
      },
    };

    return (
      <div style={{
        background: 'var(--ink-1)', border: '1px solid var(--border-1)',
        borderRadius: 'var(--r-xl)', padding: '1.5rem',
        position: 'relative', overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: '2px',
          background: `linear-gradient(90deg, transparent, ${lineColor}, transparent)`,
        }} />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
          <div>
            <div style={{
              fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase',
              letterSpacing: '0.07em', color: 'var(--text-muted)',
              marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem',
            }}>
              <TrendingUp size={11} /> Nifty 50 Index
            </div>
            <div style={{
              fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)',
              letterSpacing: '-0.03em', color: 'var(--text-primary)',
            }}>
              ₹{niftyData.current?.toLocaleString()}
            </div>
          </div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.3rem',
            padding: '0.3rem 0.65rem', borderRadius: '100px',
            background: isPositive ? 'var(--green-glow-soft)' : 'var(--red-glow-soft)',
            color: lineColor, fontSize: '0.78rem', fontWeight: 700,
            fontFamily: 'var(--font-mono)',
          }}>
            {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {isPositive ? '+' : ''}{niftyData.change_pct}%
          </div>
        </div>
        <div style={{ height: '150px' }}>
          <Line data={chartData} options={chartOpts} />
        </div>
      </div>
    );
  };

  // ── Sentiment Distribution Chart ──────────────────────────
  const chartData = data ? {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{
      label: 'Articles',
      data: [data.metadata.positive_articles, data.metadata.neutral_articles, data.metadata.negative_articles],
      backgroundColor: ['rgba(52,211,153,0.75)', 'rgba(100,116,139,0.5)', 'rgba(248,113,113,0.75)'],
      borderColor: ['#34d399', '#64748b', '#f87171'],
      borderWidth: 1, borderRadius: 6, barThickness: 32,
    }],
  } : null;

  const chartOptions = {
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(12,14,20,0.95)',
        titleFont: { size: 12, family: 'DM Sans' },
        bodyFont: { size: 13, family: 'DM Mono' },
        padding: 10, cornerRadius: 6,
      },
    },
    scales: {
      x: { ticks: { color: '#8aa094', font: { size: 12, family: 'DM Sans' } }, grid: { display: false }, border: { display: false } },
      y: { ticks: { color: '#4d6057', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.055)' }, border: { display: false } },
    },
  };

  return (
    <div className="container page-wrapper">

      {/* ── Page header ── */}
      <div className="flex-between animate-fade-1" style={{ flexWrap: 'wrap', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span className="badge badge-green" style={{ fontSize: '0.7rem', letterSpacing: '0.05em' }}>
              <Globe size={10} /> Global Market Pulse
            </span>
          </div>
          <h1 className="page-title">Market Sentiment</h1>
          <p className="page-subtitle" style={{ margin: 0 }}>
            Real-time AI analysis of  financial news, quantifying market psychology.
          </p>
        </div>

        <form onSubmit={handleSearch} style={{
          display: 'flex', gap: '0.5rem', flex: '1 1 320px', maxWidth: '420px',
        }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={15} style={{
              position: 'absolute', left: '12px', top: '50%',
              transform: 'translateY(-50%)', color: 'var(--text-muted)', pointerEvents: 'none',
            }} />
            <input
              type="text"
              className="input-control"
              placeholder="Search asset or topic..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              style={{ paddingLeft: '36px', height: '42px', fontSize: '0.88rem' }}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ height: '42px', padding: '0 1.25rem' }}>
            {loading
              ? <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
              : 'Scan'
            }
          </button>
          <button
            type="button"
            onClick={() => fetchSentiment('')}
            className="btn btn-secondary"
            style={{ height: '42px', padding: '0 0.75rem' }}
            title="Refresh"
          >
            <RefreshCw size={14} />
          </button>
        </form>
      </div>

      {/* ── Loading ── */}
      {loading && (
        <div className="flex-center" style={{ padding: '4rem', flexDirection: 'column', gap: '1rem' }}>
          <div style={{
            width: 36, height: 36, border: '3px solid var(--border-2)',
            borderTopColor: 'var(--blue-400)', borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
          }} />
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Aggregating global financial news...</p>
        </div>
      )}

      {/* ── Error ── */}
      {error && (
        <div style={{
          padding: '1rem 1.25rem', background: 'var(--red-glow-soft)',
          border: '1px solid rgba(239,68,68,0.2)', borderLeft: '3px solid var(--red-400)',
          borderRadius: 'var(--r-lg)', display: 'flex', gap: '0.75rem',
          alignItems: 'center', marginBottom: '2rem',
        }}>
          <AlertTriangle size={18} color="var(--red-400)" />
          <div>
            <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem' }}>Analysis Error</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{error}</div>
          </div>
        </div>
      )}

      {/* ── Data ── */}
      {!loading && !error && data && (
        <div className="animate-fade-2">

          {/* Top row: gauge + metrics + chart */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '260px 1fr',
            gap: '1.25rem',
            marginBottom: '1.25rem',
          }}>
            <div>{renderGauge()}</div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1px', background: 'var(--border-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', overflow: 'hidden' }}>
                {[
                  { label: 'Market Mood', value: data.market_mood, icon: Activity, color: 'var(--blue-400)', bg: 'var(--blue-glow-soft)' },
                  { label: 'Sentiment Score', value: data.average_sentiment_score.toFixed(3), icon: TrendingUp, color: 'var(--violet-400)', bg: 'var(--violet-glow-soft)' },
                  { label: 'Articles Scanned', value: data.metadata.total_articles_analyzed, icon: Newspaper, color: 'var(--amber-400)', bg: 'var(--amber-glow)' },
                ].map(({ label, value, icon: Icon, color, bg }) => (
                  <div key={label} style={{ background: 'var(--ink-1)', padding: '1.25rem 1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.75rem' }}>
                      <div style={{ width: 28, height: 28, borderRadius: 'var(--r-sm)', background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center', color }}><Icon size={14} /></div>
                      <span style={{ fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--text-muted)' }}>{label}</span>
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)', letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>{value}</div>
                  </div>
                ))}
              </div>

              <div style={{
                flex: 1,
                background: 'var(--ink-1)', border: '1px solid var(--border-1)',
                borderRadius: 'var(--r-xl)', padding: '1.5rem',
              }}>
                <div style={{
                  fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase',
                  letterSpacing: '0.07em', color: 'var(--text-muted)',
                  marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem',
                }}>
                  <BarChart3 size={11} /> Sentiment Distribution
                </div>
                <div style={{ height: '160px' }}>
                  <Bar data={chartData} options={chartOptions} />
                </div>
              </div>
            </div>
          </div>

          {/* ── Nifty 50 Chart row ── */}
          {niftyData && (
            <div style={{ marginBottom: '1.25rem' }}>
              {renderNiftyChart()}
            </div>
          )}

          {/* News feed */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
            {/* Bullish */}
            <div style={{ background: 'var(--ink-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
                <div style={{ width: 28, height: 28, borderRadius: 'var(--r-sm)', background: 'var(--green-glow-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--green-400)' }}>
                  <TrendingUp size={14} />
                </div>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>Bullish Catalysts</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {data.top_bullish_news.length > 0 ? data.top_bullish_news.map((news, i) => (
                  <div key={i} className="news-item bull">
                    <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.5rem', lineHeight: 1.5 }}>{news.title}</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{news.source}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--green-400)', fontWeight: 600 }}>
                          +{news.sentiment_score.toFixed(2)}
                        </span>
                        {news.url && (
                          <a href={news.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-muted)', display: 'flex' }}>
                            <ExternalLink size={12} />
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                )) : <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No positive signals found.</div>}
              </div>
            </div>

            {/* Bearish */}
            <div style={{ background: 'var(--ink-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
                <div style={{ width: 28, height: 28, borderRadius: 'var(--r-sm)', background: 'var(--red-glow-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--red-400)' }}>
                  <TrendingDown size={14} />
                </div>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>Risks & Headwinds</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {data.top_bearish_news.length > 0 ? data.top_bearish_news.map((news, i) => (
                  <div key={i} className="news-item bear">
                    <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.5rem', lineHeight: 1.5 }}>{news.title}</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{news.source}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--red-400)', fontWeight: 600 }}>
                          {news.sentiment_score.toFixed(2)}
                        </span>
                        {news.url && (
                          <a href={news.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-muted)', display: 'flex' }}>
                            <ExternalLink size={12} />
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                )) : <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No negative signals found.</div>}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
