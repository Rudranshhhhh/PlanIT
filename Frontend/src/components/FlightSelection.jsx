import React from 'react';
import { motion } from 'framer-motion';
import './FlightSelection.css';

const FlightSelection = ({ flights, onContinue }) => {

    // If no flights found, just proceed immediately to itinerary (optional safety check)
    // Actually the parent App.jsx handles that, but just in case:
    if (!flights || flights.length === 0) {
        return (
            <div className="flight-selection-screen empty-flights">
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="empty-flight-box">
                    <h2>Creating your Itinerary...</h2>
                    <p>No suitable flights found for this exact route & date. Proceeding...</p>
                    <button className="primary-btn" onClick={onContinue}>Show Itinerary</button>
                </motion.div>
            </div>
        );
    }

    const { origin_iata, destination_iata } = flights[0];

    return (
        <div className="flight-selection-screen">
            {/* Cinematic Background */}
            <div className="flight-bg-glass"></div>

            <motion.div
                className="flight-selection-container"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            >
                <header className="fs-header">
                    <div className="fs-route-badge">
                        <span className="fs-iata">{origin_iata}</span>
                        <span className="fs-route-icon" style={{ fontSize: '24px' }}>✈️</span>
                        <span className="fs-iata">{destination_iata}</span>
                    </div>
                    <h1>Exclusive Flight Intel</h1>
                    <p>We found the absolute best routes for your journey. Secure your seats now before planning the daily details.</p>
                </header>

                <div className="fs-tickets-grid">
                    {flights.map((flight, idx) => (
                        <motion.div
                            key={idx}
                            className="fs-ticket-card"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 + (idx * 0.1) }}
                        >
                            <div className="fs-ticket-left">
                                <div className="fs-airline">{flight.airline || "Airway"}</div>
                                <div className="fs-flight-number">Flight {flight.flight_number}</div>
                                <div className="fs-depart-time">Departing: {new Date(flight.departure_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</div>
                            </div>

                            <div className="fs-ticket-right">
                                <div className="fs-price">₹{flight.price_inr.toLocaleString('en-IN')}</div>
                                <a
                                    href={flight.booking_url}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="fs-book-btn"
                                >
                                    Book Now <span>➔</span>
                                </a>
                            </div>
                        </motion.div>
                    ))}
                </div>

                <div className="fs-footer-actions">
                    <button className="fs-skip-btn" onClick={onContinue}>
                        Skip & Build Itinerary <span style={{ marginLeft: '8px' }}>➔</span>
                    </button>
                </div>
            </motion.div>
        </div>
    );
};

export default FlightSelection;
