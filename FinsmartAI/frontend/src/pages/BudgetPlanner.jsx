import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Wallet, TrendingDown, PiggyBank, Sparkles, AlertTriangle, Lightbulb, Receipt } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend);

const CHART_COLORS = [
  '#4b7aff', '#10b981', '#ef4444', '#8b5cf6',
  '#f59e0b', '#6b9aff', '#f87171', '#34d399',
];

export default function BudgetPlanner() {
  const [incomeText, setIncomeText] = useState('');
  const [expensesText, setExpensesText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post('http://localhost:8000/api/budget/analyze', {
        income_text: incomeText,
        expenses_text: expensesText,
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze budget');
    } finally {
      setLoading(false);
    }
  };

  const renderChart = () => {
    if (!result?.analysis?.expense_breakdown_by_category) return null;
    const breakdown = result.analysis.expense_breakdown_by_category;
    const labels = Object.keys(breakdown);
    const data = Object.values(breakdown);
    return (
      <Pie
        data={{
          labels,
          datasets: [{
            data,
            backgroundColor: CHART_COLORS.slice(0, labels.length).map(c => c + 'cc'),
            borderColor: CHART_COLORS.slice(0, labels.length),
            borderWidth: 2,
          }],
        }}
        options={{
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: 'rgba(240,242,248,0.7)',
                padding: 16,
                usePointStyle: true,
                pointStyleWidth: 10,
                font: { size: 11, family: 'DM Sans' },
              },
            },
            tooltip: {
              backgroundColor: 'rgba(12,14,20,0.97)',
              titleFont: { size: 12, family: 'DM Sans' },
              bodyFont: { size: 12, family: 'DM Mono', weight: 'bold' },
              padding: 10, cornerRadius: 6,
              borderColor: 'rgba(255,255,255,0.08)', borderWidth: 1,
            },
          },
        }}
      />
    );
  };

  const savingsPercent = result?.analysis?.savings_percentage || 0;
  const savingsColor = savingsPercent >= 30
    ? 'var(--green-400)' : savingsPercent >= 10
    ? 'var(--amber-400)' : 'var(--red-400)';

  return (
    <div className="container page-wrapper">

      {/* Header */}
      <div className="animate-fade-1" style={{ marginBottom: '2.5rem' }}>
        <div style={{ marginBottom: '0.75rem' }}>
          <span className="badge badge-amber" style={{ fontSize: '0.7rem', letterSpacing: '0.05em' }}>
            <Wallet size={10} /> AI Budget Intelligence
          </span>
        </div>
        <h1 className="page-title">Smart Budget Planner</h1>
        <p className="page-subtitle">
          Describe your income and expenses in plain English — our AI will categorize,
          visualize, and generate a personalized financial strategy.
        </p>
      </div>

      {/* Input section */}
      <div className="animate-fade-2" style={{
        background: 'var(--ink-1)',
        border: '1px solid var(--border-1)',
        borderRadius: 'var(--r-xl)',
        padding: '2rem',
        marginBottom: '2rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.75rem' }}>
          <div style={{ width: 28, height: 28, borderRadius: 'var(--r-sm)', background: 'var(--blue-glow-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--blue-400)' }}>
            <Receipt size={14} />
          </div>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>Financial Data Entry</h3>
        </div>

        <form onSubmit={handleAnalyze}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '1.5rem' }}>

            {/* Income */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.6rem' }}>
                <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--green-400)' }} />
                <label className="input-label" style={{ margin: 0 }}>Income Sources</label>
              </div>
              <textarea
                className="input-control"
                rows={5}
                value={incomeText}
                onChange={e => setIncomeText(e.target.value)}
                placeholder="e.g. Monthly salary ₹80,000. Freelance work ₹5,000 this month."
                style={{ fontSize: '0.9rem', minHeight: '130px', resize: 'vertical' }}
              />
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                Enter monthly salary, freelancing, or other earnings.
              </p>
            </div>

            {/* Expenses */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.6rem' }}>
                <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--red-400)' }} />
                <label className="input-label" style={{ margin: 0 }}>Monthly Expenses</label>
              </div>
              <textarea
                className="input-control"
                rows={5}
                value={expensesText}
                onChange={e => setExpensesText(e.target.value)}
                placeholder="e.g. ₹15,000 rent, ₹6,000 groceries, ₹3,000 electricity, ₹8,000 dining."
                style={{ fontSize: '0.9rem', minHeight: '130px', resize: 'vertical' }}
              />
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                Enter rent, groceries, utilities, dining, subscriptions, etc.
              </p>
            </div>
          </div>

          {error && (
            <div style={{
              padding: '0.875rem 1.1rem',
              background: 'var(--red-glow-soft)',
              border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 'var(--r-lg)',
              display: 'flex', gap: '0.6rem', alignItems: 'center',
              marginBottom: '1.25rem',
            }}>
              <AlertTriangle size={15} color="var(--red-400)" />
              <span style={{ fontSize: '0.875rem', color: 'var(--red-400)', fontWeight: 500 }}>{error}</span>
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', height: '46px', fontSize: '0.9rem', borderRadius: 'var(--r-lg)' }}
            disabled={loading || !incomeText.trim() || !expensesText.trim()}
          >
            {loading ? (
              <><span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Analyzing your finances...</>
            ) : (
              <><Sparkles size={15} /> Generate Budget Analysis & Strategy</>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {result && !loading && (
        <div className="animate-fade-3">

          {/* KPI strip */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '1px',
            background: 'var(--border-1)',
            border: '1px solid var(--border-1)',
            borderRadius: 'var(--r-xl)',
            overflow: 'hidden',
            marginBottom: '1.25rem',
          }}>
            {[
              { label: 'Total Income', value: `₹${result.analysis.income?.toLocaleString()}`, icon: Wallet, color: 'var(--blue-400)', bg: 'var(--blue-glow-soft)' },
              { label: 'Total Expenses', value: `₹${result.analysis.total_expenses?.toLocaleString()}`, icon: TrendingDown, color: 'var(--red-400)', bg: 'var(--red-glow-soft)' },
              { label: 'Net Savings', value: `₹${result.analysis.savings?.toLocaleString()}`, icon: PiggyBank, color: savingsColor, bg: savingsPercent >= 20 ? 'var(--green-glow-soft)' : 'var(--amber-glow)' },
            ].map(({ label, value, icon: Icon, color, bg }) => (
              <div key={label} style={{ background: 'var(--ink-1)', padding: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <div style={{ width: 28, height: 28, borderRadius: 'var(--r-sm)', background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center', color }}>
                    <Icon size={14} />
                  </div>
                  <span style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--text-muted)' }}>{label}</span>
                </div>
                <div style={{ fontSize: '1.65rem', fontWeight: 700, fontFamily: 'var(--font-mono)', letterSpacing: '-0.04em', color }}>{value}</div>
              </div>
            ))}
          </div>

          {/* Savings bar */}
          <div style={{
            background: 'var(--ink-1)',
            border: '1px solid var(--border-1)',
            borderRadius: 'var(--r-xl)',
            padding: '1.25rem 1.5rem',
            marginBottom: '1.25rem',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Savings Rate</span>
              <span style={{ fontSize: '0.82rem', fontFamily: 'var(--font-mono)', fontWeight: 700, color: savingsColor }}>{savingsPercent}%</span>
            </div>
            <div style={{ width: '100%', height: '8px', background: 'var(--ink-3)', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{
                width: `${Math.min(100, Math.max(0, savingsPercent))}%`,
                height: '100%', background: savingsColor, borderRadius: '4px',
                transition: 'width 1.2s cubic-bezier(0.16, 1, 0.3, 1)',
              }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              <span>0% (Critical)</span>
              <span>20% Target</span>
              <span>50%+ Aggressive</span>
            </div>
          </div>

          {/* Chart + Transactions */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '1.25rem', marginBottom: '1.25rem' }}>

            {/* Pie chart */}
            <div style={{ background: 'var(--ink-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', padding: '1.5rem' }}>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                Expense Breakdown
              </div>
              <div style={{ maxWidth: '260px', margin: '0 auto' }}>
                {renderChart()}
              </div>
            </div>

            {/* Transactions list */}
            <div style={{ background: 'var(--ink-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', padding: '1.5rem' }}>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                Itemized Transactions
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
                {result.expenses?.map((exp, i) => (
                  <div key={i} style={{
                    padding: '0.875rem 1rem',
                    background: 'var(--ink-2)',
                    border: '1px solid var(--border-1)',
                    borderRadius: 'var(--r-lg)',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    transition: 'background 0.15s',
                  }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--ink-3)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'var(--ink-2)'}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 'var(--r-sm)',
                        background: CHART_COLORS[i % CHART_COLORS.length] + '20',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: CHART_COLORS[i % CHART_COLORS.length],
                        fontWeight: 700, fontSize: '0.85rem',
                      }}>
                        {exp.category?.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{exp.category}</div>
                        <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>{exp.description}</div>
                      </div>
                    </div>
                    <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                      ₹{exp.amount?.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* AI advice */}
          {result.advice && (
            <div style={{ background: 'var(--ink-1)', border: '1px solid var(--border-1)', borderRadius: 'var(--r-xl)', padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', paddingBottom: '1.25rem', borderBottom: '1px solid var(--border-1)' }}>
                <div style={{ width: 36, height: 36, borderRadius: 'var(--r-md)', background: 'var(--violet-glow-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--violet-400)' }}>
                  <Lightbulb size={18} strokeWidth={1.75} />
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>AI Financial Strategy</h3>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Personalized for your financial profile</span>
                </div>
              </div>
              <div className="advice-md">
                <ReactMarkdown>{result.advice}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}

      <style>{`
        .advice-md { line-height: 1.8; color: var(--text-secondary); font-size: 0.9rem; }
        .advice-md h3 { font-size: 1rem; color: var(--text-primary); margin: 1.5rem 0 0.6rem; font-weight: 700; }
        .advice-md h3:first-child { margin-top: 0; }
        .advice-md p { margin-bottom: 1rem; }
        .advice-md strong { color: var(--blue-400); font-weight: 600; }
        .advice-md ul, .advice-md ol { padding-left: 1.25rem; margin-bottom: 1rem; }
        .advice-md li { margin-bottom: 0.4rem; }
        .advice-md li::marker { color: var(--blue-400); }
      `}</style>
    </div>
  );
}
