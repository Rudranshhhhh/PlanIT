import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './TripMap.css';

// Fix default marker icon (Leaflet + bundler issue)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const TripMap = ({ destination }) => {
    const [coords, setCoords] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!destination) return;
        setLoading(true);

        // Try weather API first (gives coords + weather data)
        fetch(`/api/weather/${encodeURIComponent(destination)}`)
            .then(r => r.ok ? r.json() : Promise.reject())
            .then(data => {
                if (data.coords) {
                    setCoords({ lat: data.coords.lat, lon: data.coords.lon, city: data.city });
                }
            })
            .catch(() => {
                // Fallback: use OpenStreetMap Nominatim for geocoding (free, no key)
                return fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(destination)}&format=json&limit=1`)
                    .then(r => r.json())
                    .then(results => {
                        if (results && results.length > 0) {
                            setCoords({
                                lat: parseFloat(results[0].lat),
                                lon: parseFloat(results[0].lon),
                                city: results[0].display_name.split(',')[0],
                            });
                        }
                    })
                    .catch(() => setCoords(null));
            })
            .finally(() => setLoading(false));
    }, [destination]);

    if (loading) {
        return (
            <div className="trip-map-wrapper">
                <h2 className="section-title"><span>🗺️</span> Destination Map</h2>
                <div className="map-loading">
                    <div className="weather-spinner" />
                    <span>Loading map…</span>
                </div>
            </div>
        );
    }

    if (!coords) return null;

    return (
        <div className="trip-map-wrapper">
            <h2 className="section-title"><span>🗺️</span> Destination Map</h2>
            <div className="map-container">
                <MapContainer
                    center={[coords.lat, coords.lon]}
                    zoom={12}
                    scrollWheelZoom={true}
                    style={{ height: '100%', width: '100%', borderRadius: '16px' }}
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    <Marker position={[coords.lat, coords.lon]}>
                        <Popup>
                            <strong>{coords.city}</strong><br />
                            Your destination 📍
                        </Popup>
                    </Marker>
                </MapContainer>
            </div>
        </div>
    );
};

export default TripMap;
