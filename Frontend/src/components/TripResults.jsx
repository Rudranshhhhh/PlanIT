import { useState, useEffect, useCallback, useMemo } from 'react';
import { Button, Tag } from '@carbon/react';
import { Renew } from '@carbon/icons-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import WeatherWidget from './WeatherWidget';
import TripMap from './TripMap';
import './TripResults.css';

/* ═══════════════════════════════════════════════════════
   Helpers & Env config
   ═══════════════════════════════════════════════════════ */

const UNSPLASH_KEY = import.meta.env.VITE_UNSPLASH_ACCESS_KEY;
const imgCache = {};

async function fetchUnsplashImage(query, orientation = 'landscape') {
    const cacheKey = `${query}_${orientation}`;
    if (imgCache[cacheKey]) return imgCache[cacheKey];
    try {
        const res = await fetch(
            `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}&orientation=${orientation}&per_page=1`,
            { headers: { Authorization: `Client-ID ${UNSPLASH_KEY}` } }
        );
        if (!res.ok) throw new Error('Unsplash API failed');
        const data = await res.json();
        const url = data.results?.[0]?.urls?.regular || '';
        if (url) imgCache[cacheKey] = url;
        return url;
    } catch { return ''; }
}

function useUnsplashImage(query, orientation = 'landscape') {
    const [url, setUrl] = useState(imgCache[`${query}_${orientation}`] || '');
    useEffect(() => {
        if (!query || !UNSPLASH_KEY) return;
        let cancelled = false;
        fetchUnsplashImage(query, orientation).then((u) => {
            if (!cancelled && u) setUrl(u);
        });
        return () => { cancelled = true; };
    }, [query, orientation]);
    return url;
}

function getDayKeyword(content, destination) {
    if (!content) return `${destination} travel landmark`;
    const t = content.toLowerCase();
    if (/beach|coast|shore/.test(t)) return 'tropical beach travel';
    if (/temple|mandir|shrine/.test(t)) return 'ancient temple india';
    if (/mountain|trek|hike/.test(t)) return 'mountain trekking landscape';
    if (/fort|palace|castle|monument/.test(t)) return 'historical palace india';
    if (/market|bazaar|shopping/.test(t)) return 'vibrant street market';
    if (/museum|gallery/.test(t)) return 'museum architecture';
    if (/park|garden|botanical/.test(t)) return 'botanical garden';
    if (/lake|river|waterfall/.test(t)) return 'waterfall nature';
    if (/desert|sand|dune/.test(t)) return 'desert sand dunes';
    return `${destination} city vibrant`;
}

function getIcon(text) {
    const t = text.toLowerCase();
    if (/breakfast|brunch/.test(t)) return '🍳';
    if (/lunch|meal/.test(t)) return '🍽️';
    if (/dinner|supper/.test(t)) return '🍷';
    if (/cafe|coffee/.test(t)) return '☕';
    if (/restaurant|food|eat|cuisine|street food/.test(t)) return '🍜';
    if (/hotel|check.?in|stay|resort|hostel/.test(t)) return '🏨';
    if (/check.?out|depart|airport|flight/.test(t)) return '🛫';
    if (/temple|mandir|shrine/.test(t)) return '🛕';
    if (/church|cathedral/.test(t)) return '⛪';
    if (/mosque|masjid/.test(t)) return '🕌';
    if (/museum|gallery|exhibit/.test(t)) return '🏛️';
    if (/beach|coast|shore/.test(t)) return '🏖️';
    if (/lake|river|waterfall/.test(t)) return '🌊';
    if (/mountain|trek|hike/.test(t)) return '🥾';
    if (/fort|palace|castle|monument/.test(t)) return '🏰';
    if (/market|bazaar|shopping|mall|shop/.test(t)) return '🛍️';
    if (/park|garden|botanical/.test(t)) return '🌳';
    if (/zoo|wildlife|safari|sanctuary/.test(t)) return '🦁';
    if (/sunset|sunrise|view/.test(t)) return '🌅';
    if (/photo/.test(t)) return '📸';
    if (/boat|cruise|ferry|kayak/.test(t)) return '⛵';
    if (/spa|massage|relax|yoga/.test(t)) return '🧘';
    if (/train|railway/.test(t)) return '🚂';
    if (/bus/.test(t)) return '🚌';
    if (/taxi|cab|drive|car/.test(t)) return '🚕';
    if (/walk|stroll/.test(t)) return '🚶';
    if (/night|bar|pub|club/.test(t)) return '🌙';
    if (/show|dance|music|concert|performance/.test(t)) return '🎭';
    if (/festival|celebration|event/.test(t)) return '🎉';
    return '📍';
}

function categorizeActivity(text) {
    const t = text.toLowerCase();
    if (/hotel|stay|resort|hostel|check.?in|accommodation/.test(t)) return 'Stay';
    if (/breakfast|lunch|dinner|food|eat|restaurant|cafe|coffee|cuisine|meal/.test(t)) return 'Food';
    if (/taxi|cab|bus|train|flight|drive|car|transport|auto|rickshaw|metro/.test(t)) return 'Transport';
    return 'Activities';
}

const BUDGET_COLORS = { Stay: '#4f46e5', Food: '#10b981', Activities: '#f59e0b', Transport: '#06b6d4' };

function parseDays(text) {
    if (!text) return [];
    // Accommodate markdown formats like "## Day 1", "**Day 1**", "Day 1:"
    const dayRegex = /(?:^|\n)\s*(?:#|\*)*\s*Day\s+(\d+)\s*[:\-–—]?\s*(?:#|\*)*\s*/gi;
    const parts = text.split(dayRegex);
    if (parts.length <= 1) return [{ day: 0, content: text }];
    const daysList = [];
    for (let i = 1; i < parts.length; i += 2) {
        daysList.push({ day: parseInt(parts[i]), content: parts[i + 1]?.trim() || '' });
    }
    return daysList;
}

function extractCosts(text) {
    const costs = [];
    text.split('\n').forEach(line => {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('**') || trimmed.startsWith('##')) return;
        const matches = trimmed.match(/₹([\d,]+)/g);
        if (matches) {
            const category = categorizeActivity(trimmed);
            matches.forEach(m => {
                const amount = parseInt(m.replace(/[₹,]/g, '')) || 0;
                if (amount > 0) costs.push({ amount, category });
            });
        }
    });
    return costs;
}

function activityKey(dayNum, idx) { return `d${dayNum}_l${idx}`; }


/* ═══════════════════════════════════════════════════════
   Cinematic Background Component
   ═══════════════════════════════════════════════════════ */
function FullscreenBackground({ content, destination, dayNum }) {
    const keyword = useMemo(() => getDayKeyword(content, destination), [content, destination]);
    // Append dayNum into query to assure cache miss for same keywords if needed, or rely on distinct keywords
    const imgUrl = useUnsplashImage(`${keyword} signature`);

    return (
        <div className="cinematic-bg-wrap">
            <AnimatePresence mode="wait">
                {imgUrl && (
                    <motion.div
                        key={imgUrl}
                        initial={{ opacity: 0, scale: 1.1 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 1.2, ease: "easeOut" }}
                        className="cinematic-bg-img"
                        style={{ backgroundImage: `url(${imgUrl})` }}
                    />
                )}
            </AnimatePresence>
            <div className="cinematic-bg-overlay" />
        </div>
    );
}

/* ═══════════════════════════════════════════════════════
   Sub-Components
   ═══════════════════════════════════════════════════════ */

function ActivityRow({ text, dayNum, lineIndex, saved, checked, onToggleSave, onToggleCheck, onSwap, swapping }) {
    const clean = text.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '');
    const costMatch = clean.match(/₹[\d,]+(?:\s*[-–]\s*₹?[\d,]+)?/g);
    const textWithoutCost = clean.replace(/\(?\s*₹[\d,]+(?:\s*[-–]\s*₹?[\d,]+)?\s*\)?/g, '').trim();
    const icon = getIcon(clean);
    const key = activityKey(dayNum, lineIndex);

    return (
        <motion.div
            className={`activity-row ${checked ? 'activity-row--checked' : ''}`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: lineIndex * 0.08, duration: 0.4 }}
            whileHover={{ scale: 1.02, x: 5, backgroundColor: 'rgba(255,255,255,0.1)' }}
        >
            <div className="activity-icon-wrap">
                <span className="activity-icon">{icon}</span>
            </div>

            <span className="activity-label">{textWithoutCost || clean}</span>
            {costMatch && costMatch.map((c, ci) => (
                <span key={ci} className="cost-tag">{c}</span>
            ))}

            <div className="activity-actions">
                <button
                    className={`act-btn act-btn--check ${checked ? 'active' : ''}`}
                    onClick={() => onToggleCheck(key)}
                    title={checked ? 'Unmark visited' : 'Mark as visited'}
                >
                    {checked ? '✅' : '☐'}
                </button>
                <button
                    className={`act-btn act-btn--heart ${saved ? 'active' : ''}`}
                    onClick={() => onToggleSave(key, textWithoutCost || clean)}
                    title={saved ? 'Unsave' : 'Save place'}
                >
                    {saved ? '❤️' : '🤍'}
                </button>
                <button
                    className="act-btn act-btn--swap"
                    onClick={() => onSwap(dayNum, lineIndex, textWithoutCost || clean)}
                    title="Suggest alternative"
                    disabled={swapping}
                >
                    {swapping ? <div className="swap-loading" /> : '🔄'}
                </button>
            </div>
        </motion.div>
    );
}

function TipCallout({ text }) {
    const [expanded, setExpanded] = useState(false);
    const tipText = text.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '');
    return (
        <motion.div
            layout
            className="tip-callout"
            onClick={() => setExpanded(!expanded)}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
        >
            <span className="tip-icon">💡</span>
            <span className={`tip-text ${expanded ? 'expanded' : ''}`}>{tipText}</span>
        </motion.div>
    );
}

/* ═══════════════════════════════════════════════════════
   Main Component
   ═══════════════════════════════════════════════════════ */

const TripResults = ({ tripData, tripResults, onPlanAnother }) => {
    const { destinations, destination, days, start_date, budget, travelers, travel_style, interests } = tripData;
    const { itinerary, budget_analysis, flight_data } = tripResults;

    const destList = destinations || (destination ? [destination] : []);
    const primaryDest = destList[0] || '';
    const totalBudget = Number(budget) || 0;

    const [dayBlocks, setDayBlocks] = useState(() => parseDays(itinerary));

    // Safety check - what if AI returned no clear days? Fake a day block.
    const safeDayBlocks = useMemo(() => {
        if (!dayBlocks || dayBlocks.length === 0) return [{ day: 1, content: itinerary }];
        if (dayBlocks[0].day === 0) dayBlocks[0].day = 1; // fix '0' day parsing quirk
        return dayBlocks;
    }, [dayBlocks, itinerary]);

    const [activeDay, setActiveDay] = useState(safeDayBlocks[0]?.day || 1);

    const [savedPlaces, setSavedPlaces] = useState(() => {
        try { const s = localStorage.getItem('planit_saved'); return s ? JSON.parse(s) : {}; }
        catch { return {}; }
    });
    const [checkedItems, setCheckedItems] = useState(() => {
        try { const s = localStorage.getItem('planit_checked'); return s ? JSON.parse(s) : {}; }
        catch { return {}; }
    });
    const [swappingKey, setSwappingKey] = useState(null);

    useEffect(() => { localStorage.setItem('planit_saved', JSON.stringify(savedPlaces)); }, [savedPlaces]);
    useEffect(() => { localStorage.setItem('planit_checked', JSON.stringify(checkedItems)); }, [checkedItems]);

    // Trap scroll on body only when this page is mounted
    useEffect(() => {
        document.body.classList.add('results-active-body');
        return () => document.body.classList.remove('results-active-body');
    }, []);


    const budgetCosts = useMemo(() => extractCosts(itinerary), [itinerary]);

    const toggleSave = useCallback((key, name) => {
        setSavedPlaces(prev => { const n = { ...prev }; if (n[key]) delete n[key]; else n[key] = name; return n; });
    }, []);
    const toggleCheck = useCallback((key) => {
        setCheckedItems(prev => ({ ...prev, [key]: !prev[key] }));
    }, []);

    const handleSwap = useCallback(async (dayNum, lineIndex, activityText) => {
        const key = activityKey(dayNum, lineIndex);
        setSwappingKey(key);
        try {
            const response = await fetch('/api/plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    destinations: destList, days: 1,
                    budget: Math.round(totalBudget / (Number(days) || 1)),
                    travelers: travelers || 1, travel_style: travel_style || 'moderate',
                    interests: interests || [],
                }),
            });
            if (response.ok) {
                const result = await response.json();
                const lines = (result.itinerary || '').split('\n');
                const activityLines = lines.filter(l => l.trim().startsWith('-') || l.trim().startsWith('•'));
                const replacement = activityLines[0]?.trim().replace(/^[-•*]\s*/, '') || activityText;
                setDayBlocks(prev => {
                    const next = [...prev];
                    const dayIdx = next.findIndex(b => b.day === dayNum);
                    if (dayIdx >= 0) {
                        const contentLines = next[dayIdx].content.split('\n');
                        let bulletCount = 0;
                        for (let i = 0; i < contentLines.length; i++) {
                            const trimmed = contentLines[i].trim();
                            if (trimmed.startsWith('-') || trimmed.startsWith('•') || trimmed.startsWith('*')) {
                                if (bulletCount === lineIndex) { contentLines[i] = `- ${replacement}`; break; }
                                bulletCount++;
                            }
                        }
                        next[dayIdx] = { ...next[dayIdx], content: contentLines.join('\n') };
                    }
                    return next;
                });
            }
        } catch { /* ignored */ }
        finally { setSwappingKey(null); }
    }, [destList, totalBudget, days, travelers, travel_style, interests]);

    const activeBlock = safeDayBlocks.find(b => b.day === activeDay) || safeDayBlocks[0];

    const renderBlockContent = (block) => {
        let bulletCount = 0;
        return block.content.split('\n').map((line, j) => {
            const trimmed = line.trim();
            if (!trimmed) return null;

            if (trimmed.startsWith('**') || trimmed.startsWith('##')) {
                const clean = trimmed.replace(/[*#]+/g, '').trim();
                const lower = clean.toLowerCase();
                let icon = '📌';
                if (lower.includes('morning') || lower.includes('breakfast')) icon = '🌅';
                else if (lower.includes('afternoon') || lower.includes('lunch')) icon = '☀️';
                else if (lower.includes('evening') || lower.includes('dinner') || lower.includes('sunset')) icon = '🌆';
                else if (lower.includes('night')) icon = '🌙';

                return (
                    <motion.div
                        key={j}
                        className="time-section-header"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <span className="sh-icon">{icon}</span>
                        <h3>{clean}</h3>
                        <div className="sh-line" />
                    </motion.div>
                );
            }

            const lowerTrimmed = trimmed.toLowerCase().replace(/^[-•*]\s*/, '');
            if (lowerTrimmed.startsWith('tip') || lowerTrimmed.startsWith('note:') || lowerTrimmed.startsWith('pro tip') || lowerTrimmed.startsWith('💡')) {
                return <TipCallout key={j} text={trimmed} />;
            }

            if (trimmed.startsWith('-') || trimmed.startsWith('•') || trimmed.startsWith('*')) {
                const cur = bulletCount++;
                return (
                    <ActivityRow
                        key={j} text={trimmed} dayNum={block.day} lineIndex={cur}
                        saved={!!savedPlaces[activityKey(block.day, cur)]}
                        checked={!!checkedItems[activityKey(block.day, cur)]}
                        onToggleSave={toggleSave} onToggleCheck={toggleCheck}
                        onSwap={handleSwap} swapping={swappingKey === activityKey(block.day, cur)}
                    />
                );
            }

            return <motion.p key={j} className="plain-text-activity" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>{trimmed.replace(/\*\*/g, '')}</motion.p>;
        });
    };

    return (
        <div className="hud-viewport">
            {/* 1. Cinematic Background */}
            <FullscreenBackground
                content={activeBlock.content}
                destination={primaryDest}
                dayNum={activeDay}
            />

            {/* 2. Floating Header Navbar */}
            <motion.header
                className="hud-header"
                initial={{ y: -50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
            >
                <div className="hud-header-info">
                    <h1>{destList.join(' ➔ ')}</h1>
                    <div className="hud-tags">
                        <Tag type="blue">{days} Days</Tag>
                        {budget > 0 && <Tag type="green">₹{totalBudget.toLocaleString()}</Tag>}
                        <Tag type="purple">{travelers} Traveler{travelers > 1 ? 's' : ''}</Tag>
                    </div>
                </div>
                <div className="hud-header-actions">
                    <Button kind="secondary" size="md" renderIcon={Renew} onClick={onPlanAnother}>Re-Plan</Button>
                    <button className="glass-btn-icon" onClick={() => window.print()} title="Export HUD">📄</button>
                </div>
            </motion.header>

            {/* 3. Main Stage Content */}
            <main className="hud-stage">

                {/* Left side: The Itinerary Player */}
                <section className="hud-itinerary">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeDay}
                            className="hud-glass-card itinerary-glass"
                            initial={{ x: -40, opacity: 0, scale: 0.98 }}
                            animate={{ x: 0, opacity: 1, scale: 1 }}
                            exit={{ x: 30, opacity: 0, scale: 0.98 }}
                            transition={{ type: "spring", stiffness: 220, damping: 25 }}
                        >
                            <header className="ig-header">
                                <div className="ig-day-badge">Day {activeDay}</div>
                                <h2>{activeBlock.content.split('\n').find(l => l.startsWith('**') || l.startsWith('##'))?.replace(/[*#]+/g, '') || `Exploring ${primaryDest}`}</h2>
                            </header>

                            <div className="ig-scroll-area custom-scrollbar">
                                {renderBlockContent(activeBlock)}
                            </div>
                        </motion.div>
                    </AnimatePresence>
                </section>

                {/* Right side: Floating Widgets */}
                <aside className="hud-widgets">
                    <motion.div
                        className="hud-widget map-widget"
                        initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
                    >
                        <TripMap destination={primaryDest} />
                        <div className="map-glass-overlay">Interactive Map Engine</div>
                    </motion.div>

                    <motion.div
                        className="hud-widget"
                        initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
                    >
                        <WeatherWidget destination={primaryDest} />
                    </motion.div>

                    {/* Donut Chart (budget) inside a small glass tile */}
                    {budgetCosts.length > 0 && (
                        <motion.div
                            className="hud-widget budget-widget"
                            initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}
                        >
                            <h4 className="widget-title">Spend Analytics</h4>
                            <div className="bw-chart">
                                <ResponsiveContainer width="100%" height={120}>
                                    <PieChart>
                                        <Pie data={Object.entries(budgetCosts.reduce((acc, c) => { acc[c.category] = (acc[c.category] || 0) + c.amount; return acc; }, {})).map(([n, v]) => ({ name: n, value: v }))}
                                            cx="50%" cy="50%" innerRadius={35} outerRadius={55} paddingAngle={4} dataKey="value" stroke="none">
                                            {budgetCosts.map((_, i) => <Cell key={i} fill={Object.values(BUDGET_COLORS)[i % 4]} />)}
                                        </Pie>
                                        <Tooltip />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </motion.div>
                    )}
                </aside>

            </main>

            {/* 4. The Interactive Timeline Dock */}
            <motion.nav
                className="hud-dock-wrapper"
                initial={{ y: 80, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ type: "spring", bounce: 0.4 }}
            >
                <div className="hud-dock">
                    <div className="dock-track-line" />
                    {safeDayBlocks.map((b) => {
                        const isActive = b.day === activeDay;
                        return (
                            <button
                                key={b.day}
                                className={`dock-node ${isActive ? 'active' : ''}`}
                                onClick={() => setActiveDay(b.day)}
                            >
                                <span className="dock-node-dot" />
                                <span className="dock-node-label">Day {b.day}</span>
                                {isActive && <motion.div layoutId="dockGlow" className="dock-glow" />}
                            </button>
                        );
                    })}
                </div>
            </motion.nav>

        </div>
    );
};

export default TripResults;
