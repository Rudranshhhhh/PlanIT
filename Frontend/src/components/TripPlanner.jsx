import { useState } from 'react';
import {
    TextInput,
    NumberInput,
    DatePicker,
    DatePickerInput,
    Button,
    InlineLoading,
    ProgressIndicator,
    ProgressStep,
} from '@carbon/react';
import { SendFilled, Location, Calendar, Wallet, Partnership, Explore } from '@carbon/icons-react';
import './TripPlanner.css';

const TRAVEL_STYLES = [
    { id: 'budget', label: 'Budget', icon: '💰', desc: 'Hostels & street food', color: '#10b981' },
    { id: 'moderate', label: 'Moderate', icon: '🏨', desc: 'Comfortable stays', color: '#4f46e5' },
    { id: 'luxury', label: 'Luxury', icon: '✨', desc: 'Premium experiences', color: '#d97706' },
];

const INTERESTS = [
    { id: 'food', label: 'Food', icon: '🍜' },
    { id: 'adventure', label: 'Adventure', icon: '🏔️' },
    { id: 'culture', label: 'Culture', icon: '🏛️' },
    { id: 'nightlife', label: 'Nightlife', icon: '🌃' },
    { id: 'shopping', label: 'Shopping', icon: '🛍️' },
    { id: 'nature', label: 'Nature', icon: '🌿' },
    { id: 'religious', label: 'Religious', icon: '🕌' },
    { id: 'photography', label: 'Photography', icon: '📸' },
    { id: 'relaxation', label: 'Relaxation', icon: '🧘' },
    { id: 'history', label: 'History', icon: '📜' },
];

const TripPlanner = ({ onPlanGenerated }) => {
    const [formData, setFormData] = useState({
        destinations: [''],
        days: 3,
        start_date: '',
        budget: '',
        travelers: 1,
        travel_style: 'moderate',
        interests: [],
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const updateField = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const toggleInterest = (id) => {
        setFormData(prev => ({
            ...prev,
            interests: prev.interests.includes(id)
                ? prev.interests.filter(i => i !== id)
                : [...prev.interests, id],
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const validDestinations = formData.destinations.filter(d => d.trim());
        if (validDestinations.length === 0) {
            setError('Please enter at least one destination');
            return;
        }
        setError('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...formData,
                    destinations: validDestinations,
                    budget: Number(formData.budget) || 0,
                }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || 'Failed to generate plan');
            }

            const result = await response.json();
            onPlanGenerated(result, formData);
        } catch (err) {
            setError(err.message || 'Something went wrong. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    // Progress calculation
    const completedSteps = [
        formData.destinations.some(d => d.trim()),
        formData.days > 0,
        formData.budget,
        formData.travel_style,
    ].filter(Boolean).length;

    return (
        <div className="planner-page">
            {/* Decorative background elements */}
            <div className="planner-bg">
                <div className="bg-orb bg-orb-1"></div>
                <div className="bg-orb bg-orb-2"></div>
                <div className="bg-grid"></div>
            </div>

            <div className="planner-container">
                {/* Header */}
                <div className="planner-header">
                    <div className="header-badge">
                        <span>✈️</span> AI Trip Planner
                    </div>
                    <h1>Plan Your <span className="gradient-text">Dream Trip</span></h1>
                    <p>Fill in the details below and our AI will craft a personalized itinerary just for you</p>
                </div>

                {/* Progress */}
                <div className="planner-progress">
                    <div className="progress-bar-track">
                        <div
                            className="progress-bar-fill"
                            style={{ width: `${(completedSteps / 4) * 100}%` }}
                        ></div>
                    </div>
                    <span className="progress-label">{completedSteps} of 4 steps completed</span>
                </div>

                {/* Form Card */}
                <div className="planner-card">
                    <form onSubmit={handleSubmit}>

                        {/* Step 1: Destinations */}
                        <div className="form-step">
                            <div className="step-header">
                                <div className="step-number">1</div>
                                <div>
                                    <h3>Destinations</h3>
                                    <p>Where would you like to explore?</p>
                                </div>
                            </div>
                            {formData.destinations.map((dest, index) => (
                                <div key={index} style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                                    <TextInput
                                        id={`destination-${index}`}
                                        labelText=""
                                        placeholder={index === 0 ? "e.g. Mumbai, Goa, Jaipur..." : "Add another city"}
                                        value={dest}
                                        onChange={(e) => {
                                            const newDests = [...formData.destinations];
                                            newDests[index] = e.target.value;
                                            updateField('destinations', newDests);
                                        }}
                                        size="lg"
                                        invalid={index === 0 && !!error && !formData.destinations.some(d => d.trim())}
                                        invalidText={index === 0 ? error : ''}
                                        autoFocus={index === 0}
                                    />
                                    {formData.destinations.length > 1 && (
                                        <Button
                                            kind="danger--ghost"
                                            size="sm"
                                            onClick={() => {
                                                const newDests = formData.destinations.filter((_, i) => i !== index);
                                                updateField('destinations', newDests);
                                            }}
                                            style={{ padding: '0 12px' }}
                                        >
                                            ✕
                                        </Button>
                                    )}
                                </div>
                            ))}
                            <Button
                                kind="ghost"
                                size="sm"
                                onClick={() => updateField('destinations', [...formData.destinations, ''])}
                            >
                                + Add Destination
                            </Button>
                        </div>

                        <div className="form-divider"></div>

                        {/* Step 2: Schedule */}
                        <div className="form-step">
                            <div className="step-header">
                                <div className="step-number">2</div>
                                <div>
                                    <h3>Schedule</h3>
                                    <p>When and how long?</p>
                                </div>
                            </div>
                            <div className="form-row">
                                <div className="form-field">
                                    <NumberInput
                                        id="days"
                                        label="Duration (days)"
                                        value={formData.days}
                                        min={1}
                                        max={30}
                                        onChange={(e, { value }) => updateField('days', value)}
                                    />
                                </div>
                                <div className="form-field">
                                    <DatePicker
                                        datePickerType="single"
                                        onChange={([date]) => {
                                            if (date) {
                                                const formatted = date.toISOString().split('T')[0];
                                                updateField('start_date', formatted);
                                            }
                                        }}
                                    >
                                        <DatePickerInput
                                            id="start-date"
                                            labelText="Start Date"
                                            placeholder="dd/mm/yyyy"
                                        />
                                    </DatePicker>
                                </div>
                            </div>
                        </div>

                        <div className="form-divider"></div>

                        {/* Step 3: Budget & Travelers */}
                        <div className="form-step">
                            <div className="step-header">
                                <div className="step-number">3</div>
                                <div>
                                    <h3>Budget & Group</h3>
                                    <p>Set your budget and group size</p>
                                </div>
                            </div>
                            <div className="form-row">
                                <div className="form-field flex-grow">
                                    <TextInput
                                        id="budget"
                                        labelText="Total Budget (₹)"
                                        placeholder="e.g. 15000"
                                        type="number"
                                        value={formData.budget}
                                        onChange={(e) => updateField('budget', e.target.value)}
                                    />
                                </div>
                                <div className="form-field">
                                    <NumberInput
                                        id="travelers"
                                        label="Travelers"
                                        value={formData.travelers}
                                        min={1}
                                        max={20}
                                        onChange={(e, { value }) => updateField('travelers', value)}
                                    />
                                </div>
                            </div>
                            {formData.budget && formData.travelers > 0 && (
                                <div className="budget-hint">
                                    ≈ ₹{Math.round(Number(formData.budget) / formData.travelers / formData.days).toLocaleString('en-IN')} per person / day
                                </div>
                            )}
                        </div>

                        <div className="form-divider"></div>

                        {/* Step 4: Travel Style */}
                        <div className="form-step">
                            <div className="step-header">
                                <div className="step-number">4</div>
                                <div>
                                    <h3>Travel Style</h3>
                                    <p>How do you prefer to travel?</p>
                                </div>
                            </div>
                            <div className="style-cards">
                                {TRAVEL_STYLES.map(style => (
                                    <button
                                        key={style.id}
                                        type="button"
                                        className={`style-card ${formData.travel_style === style.id ? 'active' : ''}`}
                                        onClick={() => updateField('travel_style', style.id)}
                                    >
                                        <div className="style-check">
                                            {formData.travel_style === style.id && <span>✓</span>}
                                        </div>
                                        <span className="style-icon">{style.icon}</span>
                                        <span className="style-label">{style.label}</span>
                                        <span className="style-desc">{style.desc}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="form-divider"></div>

                        {/* Step 5: Interests */}
                        <div className="form-step">
                            <div className="step-header">
                                <div className="step-number">5</div>
                                <div>
                                    <h3>Interests</h3>
                                    <p>Select what excites you <span className="hint-text">(optional — pick any)</span></p>
                                </div>
                            </div>
                            <div className="interest-chips">
                                {INTERESTS.map(interest => (
                                    <button
                                        key={interest.id}
                                        type="button"
                                        className={`interest-chip ${formData.interests.includes(interest.id) ? 'active' : ''}`}
                                        onClick={() => toggleInterest(interest.id)}
                                    >
                                        <span className="chip-icon">{interest.icon}</span>
                                        <span>{interest.label}</span>
                                        {formData.interests.includes(interest.id) && (
                                            <span className="chip-check">✓</span>
                                        )}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Error */}
                        {error && <div className="form-error">{error}</div>}

                        {/* Submit */}
                        <div className="submit-area">
                            {isLoading ? (
                                <div className="loading-container">
                                    <div className="loading-spinner"></div>
                                    <div className="loading-text">
                                        <strong>Generating your personalized itinerary...</strong>
                                        <p>Our AI is crafting the perfect plan for you</p>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <Button
                                        type="submit"
                                        renderIcon={SendFilled}
                                        className="submit-btn"
                                        disabled={!formData.destinations.some(d => d.trim())}
                                    >
                                        Generate My Trip Plan
                                    </Button>
                                    <p className="submit-hint">Powered by AI — takes about 15-30 seconds</p>
                                </>
                            )}
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default TripPlanner;
