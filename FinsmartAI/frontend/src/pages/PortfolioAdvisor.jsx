import React, { useState } from 'react';
import axios from 'axios';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function PortfolioAdvisor() {
    const [savingsAmount, setSavingsAmount] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const [aiLoading, setAiLoading] = useState(false);
    const [aiGuidance, setAiGuidance] = useState('');

    const handleRecommend = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);
        setAiGuidance('');
        try {
            const res = await axios.post('http://localhost:8000/api/portfolio/recommendation', {
                savings_amount: parseFloat(savingsAmount) || 0
            });
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch recommendation');
        } finally {
            setLoading(false);
        }
    };

    const fetchAIGuidance = async () => {
        if (!result) return;
        setAiLoading(true);
        try {
            // Create a mock cash_flow_summary to feed the AI based on the user's savings
            const mockCashFlow = {
                total_income: result.input_savings * 3, // rough guess purely for the AI persona framing
                total_expenses: result.input_savings * 2,
                net_savings: result.input_savings,
                savings_percentage: 33,
                expenses_by_category: { 'General': result.input_savings * 2 }
            };

            const res = await axios.post('http://localhost:8000/api/portfolio/ai-advisor', {
                cash_flow_summary: mockCashFlow,
                financial_goals: "Long-term wealth building",
                risk_tolerance: "Moderate"
            });
            setAiGuidance(res.data.guidance);
        } catch (err) {
            console.error(err);
            setAiGuidance("Error loading AI insights.");
        } finally {
            setAiLoading(false);
        }
    };

    const renderChart = () => {
        if (!result?.recommended_allocation) return null;

        const labels = result.recommended_allocation.map(a => a.instrument);
        const data = result.recommended_allocation.map(a => a.allocation_percent);

        // Gradient-like colors mapping to risk
        const getColors = (items) => {
            return items.map(item => {
                if (item.risk_level === 'High') return 'rgba(248, 81, 73, 0.8)';
                if (item.risk_level === 'Medium') return 'rgba(210, 153, 34, 0.8)';
                return 'rgba(46, 160, 67, 0.8)'; // Low risk
            });
        };

        const chartData = {
            labels,
            datasets: [
                {
                    data,
                    backgroundColor: getColors(result.recommended_allocation),
                    borderColor: 'rgba(13, 17, 23, 1)',
                    borderWidth: 2,
                },
            ],
        };

        return (
            <div style={{ maxWidth: '350px', margin: '0 auto' }}>
                <Doughnut data={chartData} options={{ maintainAspectRatio: true }} />
            </div>
        );
    };

    return (
        <div className="container">
            <h1 className="page-title">Portfolio Advisor</h1>

            <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '2rem' }}>

                {/* Left Column: Form & Notes */}
                <div>
                    <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
                        <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>Enter Current Savings</h2>
                        <form onSubmit={handleRecommend}>
                            <div style={{ marginBottom: '1.5rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Savings Amount (₹)</label>
                                <input
                                    type="number"
                                    className="input-control"
                                    value={savingsAmount}
                                    onChange={(e) => setSavingsAmount(e.target.value)}
                                    placeholder="e.g. 50000"
                                    required
                                />
                            </div>
                            <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
                                {loading ? 'Calculating...' : 'Get Allocation Setup'}
                            </button>
                        </form>

                        {error && (
                            <div style={{ marginTop: '1rem', color: 'var(--danger-color)' }}>
                                {error}
                            </div>
                        )}
                    </div>

                    {result && (
                        <div className="glass-card">
                            <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Advisor Notes</h3>
                            <ul style={{ paddingLeft: '1.2rem', color: 'var(--accent-color)' }}>
                                {result.advisor_notes.map((note, idx) => (
                                    <li key={idx} style={{ marginBottom: '0.5rem', fontSize: '0.9rem' }}>{note}</li>
                                ))}
                            </ul>

                            {!aiGuidance && (
                                <button
                                    onClick={fetchAIGuidance}
                                    className="btn btn-secondary"
                                    style={{ width: '100%', marginTop: '1rem' }}
                                    disabled={aiLoading}
                                >
                                    {aiLoading ? 'Generating...' : 'Get Personalized AI Guidance'}
                                </button>
                            )}
                        </div>
                    )}
                </div>

                {/* Right Column: Allocation Breakdown */}
                <div className="glass-card">
                    <h2 style={{ fontSize: '1.2rem', marginBottom: '1.5rem' }}>
                        {result ? `Strategy: ${result.investment_strategy}` : 'Investment Strategy Insight'}
                    </h2>

                    {!result && !loading && (
                        <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '3rem 0' }}>
                            Enter your savings to view an AI-driven, risk-adjusted portfolio allocation strategy.
                        </div>
                    )}

                    {loading && (
                        <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--accent-color)' }}>
                            Structuring Optimal Portfolio...
                        </div>
                    )}

                    {result && !loading && (
                        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                            <div style={{ flex: '1 1 300px' }}>
                                {renderChart()}
                            </div>
                            <div style={{ flex: '1 1 300px' }}>
                                <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>Allocation Breakdown</h3>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                    {result.recommended_allocation.map((alloc, idx) => (
                                        <div key={idx} style={{ padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                                <span style={{ fontWeight: '600' }}>{alloc.instrument}</span>
                                                <span style={{ fontWeight: 'bold', color: 'var(--accent-color)' }}>{alloc.allocation_percent}%</span>
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                                <span style={{
                                                    display: 'inline-block',
                                                    padding: '0.1rem 0.4rem',
                                                    borderRadius: '4px',
                                                    background: alloc.risk_level === 'High' ? 'rgba(248,81,73,0.2)' : (alloc.risk_level === 'Medium' ? 'rgba(210,153,34,0.2)' : 'rgba(46,160,67,0.2)'),
                                                    color: alloc.risk_level === 'High' ? 'var(--danger-color)' : (alloc.risk_level === 'Medium' ? '#d29922' : 'var(--success-color)'),
                                                    fontSize: '0.75rem',
                                                    marginRight: '0.5rem'
                                                }}>
                                                    {alloc.risk_level} Risk
                                                </span>
                                                {alloc.reason}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {aiGuidance && (
                        <div style={{ marginTop: '2rem', padding: '1.5rem', background: 'rgba(88, 166, 255, 0.1)', border: '1px solid rgba(88, 166, 255, 0.2)', borderRadius: '12px' }}>
                            <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--accent-color)' }}>AI Wealth Manager Insight</h3>
                            <div style={{ fontSize: '0.95rem', whiteSpace: 'pre-wrap', lineHeight: '1.7' }}>
                                {aiGuidance}
                            </div>
                        </div>
                    )}

                </div>

            </div>
        </div>
    );
}
