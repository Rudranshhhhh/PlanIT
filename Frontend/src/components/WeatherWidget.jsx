import { useState, useEffect } from 'react';
import './WeatherWidget.css';

const ICON_URL = 'https://openweathermap.org/img/wn';

const WeatherWidget = ({ destination }) => {
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!destination) return;
        setLoading(true);
        fetch(`/api/weather/${encodeURIComponent(destination)}`)
            .then(r => r.ok ? r.json() : Promise.reject())
            .then(data => setWeather(data))
            .catch(() => setWeather(null))
            .finally(() => setLoading(false));
    }, [destination]);

    if (loading) {
        return (
            <div className="weather-widget weather-loading">
                <div className="weather-spinner" />
                <span>Loading weather…</span>
            </div>
        );
    }

    if (!weather) return null;

    const { current, forecast, city } = weather;

    return (
        <div className="weather-widget">
            <h2 className="section-title"><span>🌤️</span> Weather in {city}</h2>

            {/* Current */}
            <div className="weather-current">
                <img
                    src={`${ICON_URL}/${current.icon}@2x.png`}
                    alt={current.description}
                    className="weather-icon-large"
                />
                <div className="weather-current-info">
                    <span className="weather-temp-big">{current.temp}°C</span>
                    <span className="weather-desc">{current.description}</span>
                    <div className="weather-details">
                        <span>Feels like {current.feels_like}°C</span>
                        <span>💧 {current.humidity}%</span>
                        <span>💨 {current.wind_speed} m/s</span>
                    </div>
                </div>
            </div>

            {/* 5-day Forecast */}
            {forecast && forecast.length > 0 && (
                <div className="weather-forecast">
                    {forecast.map((day) => (
                        <div key={day.date} className="forecast-day">
                            <span className="forecast-date">
                                {new Date(day.date).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}
                            </span>
                            <img
                                src={`${ICON_URL}/${day.icon}@2x.png`}
                                alt={day.description}
                                className="forecast-icon"
                            />
                            <span className="forecast-temps">
                                <strong>{day.temp_max}°</strong> / {day.temp_min}°
                            </span>
                            <span className="forecast-desc">{day.description}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default WeatherWidget;
