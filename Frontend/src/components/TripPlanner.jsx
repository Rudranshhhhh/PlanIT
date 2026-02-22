import { useState } from 'react';
import {
    TextInput,
    NumberInput,
    DatePicker,
    DatePickerInput,
    Button,
    Tag,
    InlineLoading,
} from '@carbon/react';
import { SendFilled } from '@carbon/icons-react';
import './TripPlanner.css';

const TRAVEL_STYLES = [
    { id: 'budget', label: 'Budget', icon: '💰', desc: 'Hostels & street food' },
    { id: 'moderate', label: 'Moderate', icon: '🏨', desc: 'Comfortable stays' },
    { id: 'luxury', label: 'Luxury', icon: '✨', desc: 'Premium experiences' },
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
        destination: '',
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
        if (!formData.destination.trim()) {
            setError('Please enter a destination');
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

    return (
        <div className="planner-page">
            <div className="planner-container">
                <div className="planner-header">
                    <span className="planner-icon">🗺️</span>
                    <h1>Plan Your Dream Trip</h1>
                    <p>Fill in the details and let AI craft the perfect itinerary for you</p>
                </div>

                <div className="planner-card">
                    <form onSubmit={handleSubmit}>
                        {/* Destination */}
                        <div className="form-section">
                            <TextInput
                                id="destination"
                                labelText="📍 Where do you want to go?"
                                placeholder="e.g. Mumbai, Goa, Jaipur, Paris..."
                                value={formData.destination}
                                onChange={(e) => updateField('destination', e.target.value)}
                                size="lg"
                                invalid={!!error && !formData.destination}
                                invalidText={error}
                                autoFocus
                            />
                        </div>

                        {/* Days + Date */}
                        <div className="form-row">
                            <div className="form-section">
                                <NumberInput
                                    id="days"
                                    label="📅 Number of Days"
                                    value={formData.days}
                                    min={1}
                                    max={30}
                                    onChange={(e, { value }) => updateField('days', value)}
                                />
                            </div>
                            <div className="form-section">
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
                                        labelText="🗓️ Start Date"
                                        placeholder="dd/mm/yyyy"
                                    />
                                </DatePicker>
                            </div>
                        </div>

                        {/* Budget + Travelers */}
                        <div className="form-row">
                            <div className="form-section flex-1">
                                <TextInput
                                    id="budget"
                                    labelText="💵 Budget (₹)"
                                    placeholder="8000"
                                    type="number"
                                    value={formData.budget}
                                    onChange={(e) => updateField('budget', e.target.value)}
                                />
                            </div>
                            <div className="form-section">
                                <NumberInput
                                    id="travelers"
                                    label="👥 Travelers"
                                    value={formData.travelers}
                                    min={1}
                                    max={20}
                                    onChange={(e, { value }) => updateField('travelers', value)}
                                />
                            </div>
                        </div>

                        {/* Travel Style */}
                        <div className="form-section">
                            <p className="field-label">🎒 Travel Style</p>
                            <div className="style-cards">
                                {TRAVEL_STYLES.map(style => (
                                    <button
                                        key={style.id}
                                        type="button"
                                        className={`style-card ${formData.travel_style === style.id ? 'active' : ''}`}
                                        onClick={() => updateField('travel_style', style.id)}
                                    >
                                        <span className="style-icon">{style.icon}</span>
                                        <span className="style-label">{style.label}</span>
                                        <span className="style-desc">{style.desc}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Interests */}
                        <div className="form-section">
                            <p className="field-label">❤️ What are you interested in?</p>
                            <div className="interest-chips">
                                {INTERESTS.map(interest => (
                                    <button
                                        key={interest.id}
                                        type="button"
                                        className={`interest-chip ${formData.interests.includes(interest.id) ? 'active' : ''}`}
                                        onClick={() => toggleInterest(interest.id)}
                                    >
                                        <span>{interest.icon}</span>
                                        <span>{interest.label}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {error && <div className="form-error">{error}</div>}

                        {isLoading ? (
                            <InlineLoading
                                description="Generating your trip plan..."
                                status="active"
                                className="loading-indicator"
                            />
                        ) : (
                            <Button
                                type="submit"
                                renderIcon={SendFilled}
                                className="submit-btn"
                            >
                                Generate My Trip ✨
                            </Button>
                        )}
                    </form>
                </div>
            </div>
        </div>
    );
};

export default TripPlanner;
