import { Link } from 'react-router-dom';
import {
  Activity, MessageSquare, Calculator, BarChart3,
  ArrowRight, TrendingUp, TrendingDown, Shield,
  Zap, Globe, ChevronRight, Cpu, Brain, LineChart
} from 'lucide-react';

/* ── Live ticker data (static demo) ── */
const TICKER_ITEMS = [
  { sym: 'NIFTY 50',   val: '22,416',   chg: '+0.48%', up: true },
  { sym: 'SENSEX',     val: '73,878',   chg: '+0.52%', up: true },
  { sym: 'RELIANCE',   val: '₹2,847',   chg: '-0.31%', up: false },
  { sym: 'TCS',        val: '₹4,102',   chg: '+1.14%', up: true },
  { sym: 'AAPL',       val: '$187.20',  chg: '+0.66%', up: true },
  { sym: 'NVDA',       val: '$874.15',  chg: '+2.38%', up: true },
  { sym: 'GOLD',       val: '$2,341',   chg: '+0.22%', up: true },
  { sym: 'BTC/USD',    val: '$68,120',  chg: '-1.04%', up: false },
  { sym: 'MSFT',       val: '$415.34',  chg: '+0.91%', up: true },
  { sym: 'TSLA',       val: '$172.63',  chg: '-2.15%', up: false },
  { sym: 'INFY',       val: '₹1,456',   chg: '+0.77%', up: true },
  { sym: 'USD/INR',    val: '83.42',    chg: '+0.09%', up: false },
];

const features = [
  {
    title: 'Market Sentiment Engine',
    desc: 'Real-time Fear & Greed analysis across 200+ news sources. Know the market mood before you trade.',
    icon: Activity,
    link: '/sentiment',
    accent: 'var(--bull)',
    soft: 'var(--bull-soft)',
    tag: 'Live Data',
  },
  {
    title: 'AI Financial Advisor',
    desc: 'Ask anything in plain English — RAG-powered answers grounded in your uploaded financial documents.',
    icon: MessageSquare,
    link: '/chat',
    accent: 'var(--emerald)',
    soft: 'var(--emerald-soft)',
    tag: 'NVIDIA NIM',
  },
  {
    title: 'Smart Budget Planner',
    desc: 'Describe your cash flow naturally. AI categorizes, charts, and builds a wealth strategy for you.',
    icon: Calculator,
    link: '/budget',
    accent: 'var(--gold)',
    soft: 'var(--gold-soft)',
    tag: 'Personal Finance',
  },
  {
    title: 'Stock Intelligence',
    desc: 'Deploy a multi-agent AI research team to generate institutional-grade investment reports on any stock.',
    icon: BarChart3,
    link: '/stock',
    accent: 'var(--violet)',
    soft: 'var(--violet-soft)',
    tag: 'Multi-Agent AI',
  },
];

const stats = [
  { label: 'News Sources', value: '200+', sub: 'Real-time feeds' },
  { label: 'Analysis Time',  value: '<60s',  sub: 'For full stock report' },
  { label: 'AI Models',      value: '3',     sub: 'LLM + RAG + Agents' },
  { label: 'Markets Covered',value: '50+',   sub: 'NSE, BSE, NYSE, NASDAQ' },
];

function TickerBar() {
  const doubled = [...TICKER_ITEMS, ...TICKER_ITEMS];
  return (
    <div className="ticker-bar">
      <div className="ticker-track">
        {doubled.map((item, i) => (
          <span key={i} style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.45rem',
            padding: '0 2rem', fontSize: '0.78rem', fontFamily: 'var(--font-mono)',
            borderRight: '1px solid var(--border-1)',
          }}>
            <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>{item.sym}</span>
            <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{item.val}</span>
            <span style={{
              color: item.up ? 'var(--bull)' : 'var(--bear)',
              display: 'flex', alignItems: 'center', gap: '0.1rem',
            }}>
              {item.up ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
              {item.chg}
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div style={{ paddingTop: 'var(--nav-h)' }}>

      {/* ── Live ticker strip (just below navbar) ── */}
      <TickerBar />

      <div className="container" style={{ paddingTop: '4rem', paddingBottom: '5rem' }}>

        {/* ══ HERO — asymmetric split ══ */}
        <section className="animate-fade-1" style={{
          display: 'grid',
          gridTemplateColumns: '1fr 420px',
          gap: '4rem',
          alignItems: 'center',
          marginBottom: '5rem',
        }}>

          {/* Left copy */}
          <div>
            <div style={{ marginBottom: '1.5rem' }}>
              <span className="badge badge-em" style={{ fontSize: '0.7rem', letterSpacing: '0.06em' }}>
                <Cpu size={10} strokeWidth={2.5} />
                INSTITUTIONAL-GRADE AI FINANCE
              </span>
            </div>

            <h1 className="display" style={{ marginBottom: '1.5rem' }}>
              Your personal<br />
              <span className="grade-em">financial command</span><br />
              centre.
            </h1>

            <p style={{
              fontSize: '1.05rem', color: 'var(--text-secondary)',
              lineHeight: 1.75, maxWidth: '480px', marginBottom: '2.25rem',
            }}>
              Institutional-grade market intelligence, AI-powered portfolio analysis, and smart budgeting tools — built for investors who take their money seriously.
            </p>

            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '2.5rem' }}>
              <Link to="/chat" className="btn btn-primary" style={{ padding: '0.8rem 1.75rem', fontSize: '0.95rem', borderRadius: '10px' }}>
                <MessageSquare size={16} /> Start AI Chat
              </Link>
              <Link to="/stock" className="btn btn-secondary" style={{ padding: '0.8rem 1.75rem', fontSize: '0.95rem', borderRadius: '10px' }}>
                <TrendingUp size={16} /> Analyze a Stock
              </Link>
            </div>

            {/* Trust row */}
            <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
              {[
                { icon: Shield, text: 'Bank-grade security' },
                { icon: Globe,  text: 'Real-time data' },
                { icon: Zap,    text: 'Instant insights' },
              ].map(({ icon: Icon, text }) => (
                <span key={text} style={{
                  display: 'flex', alignItems: 'center', gap: '0.4rem',
                  fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500,
                }}>
                  <Icon size={13} />
                  {text}
                </span>
              ))}
            </div>
          </div>

          {/* Right — dashboard preview card */}
          <div style={{
            background: 'var(--bg-1)',
            border: '1px solid var(--border-2)',
            borderRadius: '20px',
            padding: '1.5rem',
            boxShadow: '0 20px 60px rgba(0,0,0,0.25), 0 0 0 1px var(--border-1)',
            position: 'relative',
          }}>
            {/* Top strip */}
            <div style={{
              position: 'absolute', top: 0, left: '10%', right: '10%', height: '1px',
              background: 'linear-gradient(90deg, transparent, var(--emerald), transparent)',
              opacity: 0.7,
            }} />

            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Portfolio Overview
              </div>
              <div style={{ fontSize: '2rem', fontFamily: 'var(--font-mono)', fontWeight: 700, letterSpacing: '-0.04em', color: 'var(--text-primary)' }}>
                ₹12,84,350
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.3rem' }}>
                <TrendingUp size={14} color="var(--bull)" />
                <span style={{ fontSize: '0.82rem', color: 'var(--bull)', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>+3.42% today</span>
              </div>
            </div>

            {/* Mini chart */}
            <div style={{ marginBottom: '1.25rem', padding: '1rem', background: 'var(--bg-2)', borderRadius: '12px' }}>
              <svg width="100%" height="80" viewBox="0 0 300 80" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--emerald)" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="var(--emerald)" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path
                  d="M0,60 C30,55 60,45 90,42 C120,38 140,30 170,25 C200,20 220,28 250,18 C270,12 285,8 300,5"
                  fill="none"
                  stroke="var(--emerald)"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
                <path
                  d="M0,60 C30,55 60,45 90,42 C120,38 140,30 170,25 C200,20 220,28 250,18 C270,12 285,8 300,5 L300,80 L0,80 Z"
                  fill="url(#chartGrad)"
                />
              </svg>
            </div>

            {/* Mini stat row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
              {[
                { label: 'Total Invested', val: '₹10.2L', color: 'var(--text-primary)' },
                { label: 'P&L', val: '+₹2.6L', color: 'var(--bull)' },
                { label: 'XIRR', val: '18.4%', color: 'var(--emerald)' },
              ].map(({ label, val, color }) => (
                <div key={label} style={{ padding: '0.75rem', background: 'var(--bg-2)', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.3rem' }}>{label}</div>
                  <div style={{ fontSize: '0.95rem', fontFamily: 'var(--font-mono)', fontWeight: 700, color }}>{val}</div>
                </div>
              ))}
            </div>

            {/* Sentiment pill at bottom */}
            <div style={{
              marginTop: '1rem', padding: '0.75rem 1rem',
              background: 'var(--emerald-soft)',
              border: '1px solid rgba(0,200,150,0.18)',
              borderRadius: '10px',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--emerald)', display: 'inline-block' }} />
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Market Sentiment</span>
              </div>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--emerald)' }}>Greed · 74</span>
            </div>
          </div>
        </section>

        {/* ══ STATS BENTO ══ */}
        <section className="animate-fade-2" style={{ marginBottom: '4.5rem' }}>
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
            background: 'var(--bg-1)',
            border: '1px solid var(--border-1)',
            borderRadius: '18px',
            overflow: 'hidden',
            gap: '1px',
          }}>
            {stats.map(({ label, value, sub }) => (
              <div key={label} style={{
                padding: '1.75rem', background: 'var(--bg-1)',
                borderRight: '1px solid var(--border-1)',
              }}>
                <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'var(--font-mono)', letterSpacing: '-0.04em', color: 'var(--emerald)', lineHeight: 1, marginBottom: '0.4rem' }}>{value}</div>
                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{label}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sub}</div>
              </div>
            ))}
          </div>
        </section>

        {/* ══ FEATURES — asymmetric 2+2 ══ */}
        <section className="animate-fade-3" style={{ marginBottom: '4.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem' }}>
            <div>
              <p className="section-label">What We Offer</p>
              <h2 style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.03em', maxWidth: '380px', lineHeight: 1.25 }}>
                Every tool you need to invest smarter
              </h2>
            </div>
            <Link to="/chat" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.85rem', color: 'var(--emerald)', fontWeight: 600, textDecoration: 'none' }}>
              Get started <ArrowRight size={14} />
            </Link>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1px', background: 'var(--border-1)', border: '1px solid var(--border-1)', borderRadius: '18px', overflow: 'hidden' }}>
            {features.map((f, i) => {
              const Icon = f.icon;
              return (
                <Link key={f.title} to={f.link} style={{ textDecoration: 'none', color: 'inherit' }}>
                  <div
                    style={{
                      background: 'var(--bg-1)', padding: '2rem',
                      borderBottom: i < 2 ? '1px solid var(--border-1)' : 'none',
                      height: '100%', display: 'flex', flexDirection: 'column', gap: '0.75rem',
                      transition: 'background 0.2s', position: 'relative', overflow: 'hidden',
                      cursor: 'pointer',
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-2)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'var(--bg-1)'}
                  >
                    {/* top accent on hover */}
                    <div style={{
                      position: 'absolute', top: 0, left: '1.5rem', right: '1.5rem', height: '1px',
                      background: `linear-gradient(90deg, transparent, ${f.accent}60, transparent)`,
                    }} />

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{
                        width: 38, height: 38, borderRadius: '10px',
                        background: f.soft, color: f.accent,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}>
                        <Icon size={18} strokeWidth={1.75} />
                      </div>
                      <span className="badge" style={{ background: f.soft, color: f.accent, border: `1px solid ${f.accent}35`, fontSize: '0.67rem', letterSpacing: '0.04em' }}>
                        {f.tag}
                      </span>
                    </div>

                    <h3 style={{ fontSize: '1rem', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>{f.title}</h3>

                    <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.7, flexGrow: 1 }}>{f.desc}</p>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem', fontWeight: 600, color: f.accent }}>
                      Explore <ChevronRight size={13} />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* ══ WHY FINSMART — editorial strip ══ */}
        <section className="animate-fade-4" style={{
          background: 'var(--bg-1)',
          border: '1px solid var(--border-1)',
          borderRadius: '18px',
          padding: '2.5rem',
          marginBottom: '4.5rem',
          display: 'grid',
          gridTemplateColumns: '1fr 1px 1fr 1px 1fr',
          gap: '2rem',
        }}>
          {[
            { icon: Brain, title: 'AI at the core', desc: 'Every feature is powered by NVIDIA NIM, LangChain, and CrewAI — not just wrappers.' },
            { icon: LineChart, title: 'Data-first design', desc: 'We surface what matters: numbers, trends, signals — not noise.' },
            { icon: Shield, title: 'Your data stays yours', desc: 'All analysis happens on your terms. No third-party data selling, ever.' },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} style={{ gridColumn: i === 0 ? '1' : i === 1 ? '3' : '5' }}>
                <div style={{ width: 32, height: 32, borderRadius: '8px', background: 'var(--emerald-soft)', color: 'var(--emerald)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
                  <Icon size={16} strokeWidth={1.75} />
                </div>
                <h4 style={{ fontSize: '0.975rem', fontWeight: 700, marginBottom: '0.5rem', letterSpacing: '-0.015em' }}>{item.title}</h4>
                <p style={{ fontSize: '0.845rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>{item.desc}</p>
              </div>
            );
          }).reduce((acc, el, i) => {
            acc.push(el);
            if (i < 2) acc.push(
              <div key={`div-${i}`} style={{ gridColumn: i === 0 ? '2' : '4', background: 'var(--border-1)', width: '1px', alignSelf: 'stretch' }} />
            );
            return acc;
          }, [])}
        </section>

        {/* ══ Stack + CTA footer ══ */}
        <section style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          flexWrap: 'wrap', gap: '1.25rem',
          paddingTop: '1.5rem', borderTop: '1px solid var(--border-1)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>Built with</span>
            {['Nvidia NIM', 'CrewAI', 'LangChain', 'FastAPI', 'React', 'MongoDB'].map(t => (
              <span key={t} style={{
                fontSize: '0.75rem', padding: '0.22rem 0.65rem',
                borderRadius: '100px', background: 'var(--bg-2)',
                border: '1px solid var(--border-1)', color: 'var(--text-muted)', fontWeight: 500,
              }}>{t}</span>
            ))}
          </div>
          <Link to="/chat" className="btn btn-primary" style={{ padding: '0.65rem 1.5rem', fontSize: '0.875rem', borderRadius: '8px' }}>
            Get started <ArrowRight size={14} />
          </Link>
        </section>

      </div>
    </div>
  );
}
