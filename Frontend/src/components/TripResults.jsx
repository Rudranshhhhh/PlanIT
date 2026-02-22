import { Button, Tag } from '@carbon/react';
import { Renew } from '@carbon/icons-react';
import './TripResults.css';

const TripResults = ({ tripData, tripResults, onPlanAnother }) => {
    const { destination, days, start_date, budget, travelers, travel_style, interests } = tripData;
    const { itinerary, budget_analysis } = tripResults;

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    };

    const parseDays = (text) => {
        if (!text) return [];
        const dayRegex = /(?:^|\n)\s*\**\s*Day\s+(\d+)\s*[:\-–—]?\s*\**\s*/gi;
        const parts = text.split(dayRegex);
        if (parts.length <= 1) return [{ day: 0, content: text }];
        const daysList = [];
        for (let i = 1; i < parts.length; i += 2) {
            const dayNum = parseInt(parts[i]);
            const content = parts[i + 1] || '';
            daysList.push({ day: dayNum, content: content.trim() });
        }
        return daysList;
    };

    const dayBlocks = parseDays(itinerary);

    return (
        <div className="results-page">
            <div className="results-container">
                {/* Hero */}
                <div className="results-hero">
                    <div className="results-hero-bg"></div>
                    <div className="results-hero-content">
                        <span className="results-emoji">🎉</span>
                        <h1>Your Trip to {destination}</h1>
                        <div className="results-tags">
                            <Tag type="blue" size="md">📅 {days} Days</Tag>
                            {start_date && <Tag type="teal" size="md">🗓️ {formatDate(start_date)}</Tag>}
                            {budget > 0 && <Tag type="green" size="md">💰 ₹{Number(budget).toLocaleString('en-IN')}</Tag>}
                            <Tag type="purple" size="md">👥 {travelers} Traveler{travelers > 1 ? 's' : ''}</Tag>
                            <Tag type="cyan" size="md" className="capitalize">🎒 {travel_style}</Tag>
                        </div>
                        {interests.length > 0 && (
                            <div className="results-interests">
                                {interests.map(i => (
                                    <span key={i} className="interest-badge">{i}</span>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Itinerary */}
                <div className="itinerary-section">
                    <h2 className="section-title"><span>📋</span> Your Itinerary</h2>

                    {dayBlocks.length > 0 && dayBlocks[0].day > 0 ? (
                        <div className="timeline">
                            {dayBlocks.map((block, idx) => (
                                <div key={idx} className="timeline-item" style={{ animationDelay: `${idx * 0.1}s` }}>
                                    <div className="timeline-marker">
                                        <div className="marker-dot"></div>
                                        {idx < dayBlocks.length - 1 && <div className="marker-line"></div>}
                                    </div>
                                    <div className="day-card">
                                        <div className="day-label">Day {block.day}</div>
                                        <div className="day-content">
                                            {block.content.split('\n').map((line, j) => {
                                                const trimmed = line.trim();
                                                if (!trimmed) return null;
                                                if (trimmed.startsWith('**') || trimmed.startsWith('##')) {
                                                    const clean = trimmed.replace(/[*#]+/g, '').trim();
                                                    return <h4 key={j} className="activity-heading">{clean}</h4>;
                                                }
                                                if (trimmed.startsWith('-') || trimmed.startsWith('•') || trimmed.startsWith('*')) {
                                                    const clean = trimmed.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '');
                                                    return <p key={j} className="activity-item">• {clean}</p>;
                                                }
                                                return <p key={j} className="activity-text">{trimmed.replace(/\*\*/g, '')}</p>;
                                            })}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="itinerary-raw">
                            {(itinerary || 'No itinerary generated.').split('\n').map((line, i) => {
                                const trimmed = line.trim();
                                if (!trimmed) return <br key={i} />;
                                return <p key={i}>{trimmed.replace(/\*\*/g, '')}</p>;
                            })}
                        </div>
                    )}
                </div>

                {/* Budget */}
                {budget_analysis && budget_analysis.daily_per_person && (
                    <div className="budget-section">
                        <h2 className="section-title"><span>💰</span> Budget Breakdown</h2>
                        <div className="budget-grid">
                            {Object.entries(budget_analysis.daily_per_person).map(([key, val]) => (
                                <div className="budget-card" key={key}>
                                    <span className="budget-category">{key.replace(/_/g, ' ')}</span>
                                    <span className="budget-amount">
                                        ${typeof val === 'object' ? `${val.min}–${val.max}` : val}/day
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Actions */}
                <div className="results-actions">
                    <Button
                        kind="tertiary"
                        size="lg"
                        renderIcon={Renew}
                        onClick={onPlanAnother}
                        className="plan-another-btn"
                    >
                        Plan Another Trip
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default TripResults;
